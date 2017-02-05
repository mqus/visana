import pandas as pd
import numpy as np
from sklearn import cluster

from table import DataTable

## attribute that contains timestamp
TIME_ATTR="MasterTime"
GRAIN_COLS2=["Small", "Large"]
GRAIN_COLS=["GrainSize0_25", "GrainSize0_28", "GrainSize0_30", "GrainSize0_35", "GrainSize0_40", "GrainSize0_45",
 "GrainSize0_50", "GrainSize0_58", "GrainSize0_65", "GrainSize0_70", "GrainSize0_80", "GrainSize1_0", "GrainSize1_3", "GrainSize1_6", "GrainSize2_0", "GrainSize2_5", "GrainSize3_0", "GrainSize3_5", "GrainSize4_0", "GrainSize5_0", "GrainSize6_5", "GrainSize7_5", "GrainSize8_0", "GrainSize10_0", "GrainSize12_5", "GrainSize15_0", "GrainSize17_5", "GrainSize20_0", "GrainSize25_0", "GrainSize30_0", "GrainSize32_0"]
CUSTOM_COLS=[]
COLORS=["#1F77B4", "#FF7F0E", "#2CA02C", "#d62728", "#9467BD", "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"]


class DataSource:


    def __init__(self):
        self.table_store=dict()

    ## return number of tables in this Source
    def get_table_count(self) -> int:
        return len(self.table_store)

    ## return table with the given name
    def get_data(self, name) -> DataTable:
        return self.table_store[name]

    ## return table with the given name
    def table(self, name)-> pd.DataFrame:
        return self.table_store[name]

    ## return base table with original data
    def get_base_data(self) -> DataTable:
        return self.table_store["base"]

    ## return base table with original data
    def base(self) -> DataTable:
        return self.table_store["base"]

    ## return the dictionary with all tables
    def get_table_store(self):
        return self.table_store

    ## returns if a labeled table exists
    def exists(self,name) ->bool:
        return name in self.table_store

    ## construct base table with csv file at given path
    def read_data(self,path):
        self.table_store["base"]=DataTable(path)
        #self.table_store["base"] = DataTable(df=self.get_data("base").df().sort_values(by=TIME_ATTR))

    def pop_table(self,name)-> DataTable:
        return self.table_store.pop(name)

    ## give in_table another alias out_table
    def link(self, out_table, in_table="base"):
        df = self.table_store[in_table].df()
        c = self.table_store[in_table].centroids
        ## store 'copy' in new table
        self.table_store[out_table] = DataTable(df=df, centroids=c)

    ## perform a selection on data
    ##	out_table: name of new table with results
    ##	attr_name: attribute for the selection
    ##	a: min-value for this attribute
    ##	b: max-value for this attribute
    ## 	in_table: table to perform the selection on
    def select(self,out_table,attr_name,a=None,b=None,in_table="base"):
        df = self.table_store[in_table].df()
        c = self.table_store[in_table].centroids

        ## select the according tuples for these boundaries
        ## for the given attribute
        if a is not None:
            df = df.loc[df[attr_name] >= a]
        if b is not None:
            df = df.loc[df[attr_name] <= b]

        ## store results in new table
        self.table_store[out_table] = DataTable(df=df, centroids=c)

    ## perform a groupby aggregation on data
    ##	out_table: name of new table with results
    ##	attr: attribute or list of attributes to group by
    ##	mode: aggregation mode of the other columns
    ## 	in_table: table to perform the projection on
    def groupby2(self,out_table,attr, mode,in_table="base", bydate=False):
        df = self.table_store[in_table].df() #type:pd.DataFrame
        c = self.table_store[in_table].centroids
        if bydate:
            by=df[attr].dt.normalize()
        else:
            by=df[attr]

        grouped = df.groupby(by)

        if mode is 'COUNT':
            out=grouped.count()
        elif mode is 'SUM':
            out=grouped.sum()
        else:
            out=grouped.max()
        #data.groupby().count()

        ## narrow data to the specified attributes
        #df = df[[attr1, attr2]]

        ## store results in new table
        self.table_store[out_table] = DataTable(df=out, centroids=c)

    ## perform a projection on data
    ##	out_table: name of new table with results
    ##	attr1: attribute to remain in table
    ##	attr2: attribute to remain in table
    ## 	in_table: table to perform the projection on
    def project(self,out_table,attr1,attr2,in_table="base"):
        df = self.table_store[in_table].df()

        ## narrow data to the specified attributes
        df = df[[attr1, attr2]]

        ## store results in new table
        self.table_store[out_table] = DataTable(df=df)

    def store_df(self, df, name):
        self.table_store[name] = DataTable(df=df)

    ## perform aggregation on data
    ##	out_table: name of new table with results
    ##	mode: how to aggregate data? AVG, MIN or MAX
    ##	attr_names: list of attributes to aggregate and keep in results
    ##	limit (or 'range'): only aggregate that many rows for each resulting row
    ## 	in_table: table to perform the aggregation on
    def aggregate(self, out_table, mode, limit=0, in_table="base"):
        df = self.table_store[in_table].df() #type:pd.DataFrame
        c = self.table_store[in_table].centroids
        #new_df = pd.DataFrame(columns=attr_names)
        ## only view selected columns
        data=dict() ## dictionary for results
        ## aggregate all rows in one step if limit is 0
        if limit is 0:
            limit=len(df.index)
        ## iterate over columns
        for attr,values in df.iteritems():
            data[attr]=list()
            i=0
            if attr == TIME_ATTR:
                for value in values:
                    if i % limit == 0 and mode is "MIN":
                        data[attr].append(value)
                    i += 1
                    if i % limit == 0 and mode is not "MIN":
                        data[attr].append(value)

            else:
                ## track data characteristics for result
                sum=0
                min=0
                max=0
                ## count how many non-missing values in interval
                valid_cnt = 0
                for value in values:
                    ## update min, max and sum for each value
                    if i % limit == 0 or np.isnan(min):
                        min=value
                        max=value
                        sum=0
                        valid_cnt = 0
                    else:
                        if not np.isnan(value):
                            if value<min:
                                min=value
                            if value>max:
                                max=value
                    if not np.isnan(value):
                        valid_cnt += 1
                        sum=sum+value
                    i=i+1
                    ## produce new result row if i%limit==0
                    if i % limit is 0:
                        insval=np.nan
                        if valid_cnt > 0:
                            if mode is "AVG":
                                insval=sum/valid_cnt
                            elif mode is "MAX":
                                insval=max
                            elif mode is "MIN":
                                insval=min
                        data[attr].append(insval)
                        #new_df.insert(int(i / limit), attr, insval)

        self.table_store[out_table]=DataTable(df=pd.DataFrame(data), centroids=c)
        #print(table_store[out_table])

    def aggregateTime(self, out_table, mode, minutes=60*24, in_table='base'):
        df = self.table_store[in_table].df() #type:pd.DataFrame
        c = self.table_store[in_table].centroids

        freq='{}Min'.format(minutes)
        #df.index = pd.DatetimeIndex(df[TIME_ATTR], copy=True)
        by=pd.TimeGrouper(freq=freq)
        grouped = df.groupby(by)
        if mode == 'COUNT':
            out=grouped.count()
        elif mode == 'AVG':
            out=grouped.mean()
        elif mode == 'MIN':
            out=grouped.min()
        else:
            out=grouped.max()

        self.table_store[out_table] = DataTable(df=out, centroids=c)



    def filterforvalues(self,out_table, cols,method="OR", in_table="base"):
        #TODO ?
        real_cols=[]
        #exclude Timestamps
        for col in cols:
            if not col == self.get_time_colname():
                real_cols.append(col)



    #select with multiple ids
    def select_ids(self,out_table, ids, in_table="base"):
        df = self.table_store[in_table].df()  # type:pd.DataFrame
        c = self.table_store[in_table].centroids
        df= df.loc[ids]
        self.table_store[out_table] = DataTable(df=df, centroids=c)

    def select_complex(self,out_table, clause, in_table="base"):
        in_df = self.table_store[in_table].df()  # type:pd.DataFrame
        c = self.table_store[in_table].centroids
        out_df=None
        if clause is None:
            self.table_store[out_table] = DataTable(df=in_df)
            return
        once=True
        for i in clause:
            tmp_df=in_df
            for j in clause[i]:
                print(i, j, clause[i][j])

                equation=clause[i][j]
                val = float(equation["val"])
                param = 	equation["param"]
                if equation["comp"] == "<":
                    tmp_df = tmp_df.loc[tmp_df[param] < val]
                elif equation["comp"] == "<=":
                    tmp_df = tmp_df.loc[tmp_df[param] <= val]
                elif equation["comp"] == "=":
                    tmp_df = tmp_df.loc[tmp_df[param] == val]
                elif equation["comp"] == "=>":
                    tmp_df = tmp_df.loc[tmp_df[param] >= val]
                elif equation["comp"] == ">":
                    tmp_df = tmp_df.loc[tmp_df[param] > val]
            if once:
                once=False
                out_df=tmp_df
            else:
                out_df=tmp_df.combine_first(out_df)
        if once: #if no clauses were within the dict
            out_df=in_df
        self.table_store[out_table] = DataTable(df=out_df, centroids=c)

    # normalize all values in the columns specified by params for each row, such that each summed up row is then
    # equal to 1
    # TODO:
    # rows where all parameters are 0 will be turned into n.a
    # negative values are not handled appropriately!
    def normalize(self,out_table, params=None, in_table="base"):
        if params is None:
            params=self.get_grain_columns()
        df = self.table_store[in_table].df()  # type:pd.DataFrame
        c = self.table_store[in_table].centroids
        other_params = [col for col in df.columns if col not in params]
        #temporarily save unconcerned columns
        out_df=df[other_params]

        #normalize all other columns
        df = df[params]
        df = df.div(df.sum(axis=1), axis=0)

        #put them back together
        out_df = out_df.join(df)
        self.table_store[out_table] = DataTable(df=out_df, centroids=c)

    # create new columns by adding other summed up columns as a new column to the dataframe
    def newcols(self, out_table, mode, newcols, in_table="base"):
        df = self.table_store[in_table].df().copy()  # type:pd.DataFrame
        c = self.table_store[in_table].centroids

        if mode == "SUM":
            for new_colname,paramlist in newcols.items():
                df[new_colname] = df[paramlist].sum(axis=1)
        elif mode == "MEAN":
            for new_colname,paramlist in newcols.items():
                df[new_colname] = df[paramlist].mean(axis=1)
        elif mode == "MIN":
            for new_colname,paramlist in newcols.items():
                df[new_colname] = df[paramlist].min(axis=1)
        elif mode == "MAX":
            for new_colname,paramlist in newcols.items():
                df[new_colname] = df[paramlist].max(axis=1)

        self.table_store[out_table] = DataTable(df=df, centroids=c)


    def cluster(self, out_table, k, params, in_table="base"):
        df = self.table_store[in_table].df()  # type:pd.DataFrame

        ##TMP
        #check for null values and remove them
        #(retain only not-null-values for relevant params)
        for p in params:
            df = df.loc[df[p].notnull()]

        kmeans = cluster.KMeans(n_clusters=k)
        kmeans.fit(df[params])
        centroids = kmeans.cluster_centers_

        df["_label"] = kmeans.labels_

        self.table_store[out_table] = DataTable(df=df, centroids=centroids)

    # def calc_clusters(in_table, out_table, datasource, k, colNames=GRAIN_COLS):
    #     print("CLUSTERING")
    #     print(colNames)
    #     df = datasource.get_data(in_table).df()
    #     kmeans = cluster.KMeans(n_clusters=k)
    #     kmeans.fit(df[colNames])
    #
    #     cent_map = {}
    #     centroids = kmeans.cluster_centers_
    #     temp_cent_order = []
    #     for c in range(0, len(centroids)):
    #         t = [c, centroids[c, 0]]
    #         temp_cent_order.append(t)
    #
    #     print(temp_cent_order)
    #     cent_order = sorted(temp_cent_order, key=lambda x: x[1], reverse=True)
    #     for c in range(0, len(centroids)):
    #         cent_map[temp_cent_order[c][0]] = cent_order[c][0]
    #     print(cent_order)
    #     print(cent_map)
    #
    #     newcentroids = []
    #     for c in range(0, len(centroids)):
    #         newcentroids.append(centroids[cent_order[c][0]])
    #     print(np.asarray(newcentroids))
    #
    #     labels = kmeans.labels_
    #     newlabels = []
    #     for label in labels:
    #         newlabels.append(cent_map[label])
    #
    #     print(type(labels))
    #     print(type(np.asarray(newlabels)))
    #     # print(labels)
    #     # print(newlabels)
    #     # print("labels: ")
    #     # print(labels)
    #     # print("labelsLEN: "+str(len(labels)))
    #     # for i in labels:
    #     #       print(i)
    #     df['clusterlabels'] = newlabels
    #     # print(df.describe())
    #     # print(df[TIME_ATTR])
    #
    #
    #     datasource.store_df(df=df, name=out_table)
    #
    #     # print("centroids: ")
    #     # print(centroids)
    #     debugprint = """
    #     print(centroids)
    #
    #     firstcentroids = df.loc[df['clusterlabels'] == 0]
    #     seccentroids = df.loc[df['clusterlabels'] == 1]
    #     qcentroids = df.loc[df['clusterlabels'] == 2]
    #     acentroids = df.loc[df['clusterlabels'] == 3]
    #
    #     firstindex = 0
    #     secindex = 25
    #     #pyplot.scatter(firstcentroids["Small"], firstcentroids["Large"], color="red")
    #     #pyplot.scatter(seccentroids["Small"], seccentroids["Large"], color="blue")
    #     pyplot.scatter(firstcentroids[GRAIN_COLS[firstindex]], firstcentroids[GRAIN_COLS[secindex]], color="red")
    #     pyplot.scatter(seccentroids[GRAIN_COLS[firstindex]], seccentroids[GRAIN_COLS[secindex]], color="blue")
    #     pyplot.scatter(qcentroids[GRAIN_COLS[firstindex]], qcentroids[GRAIN_COLS[secindex]], color="green")
    #     pyplot.scatter(acentroids[GRAIN_COLS[firstindex]], acentroids[GRAIN_COLS[secindex]], color="yellow")
    #
    #     for i in range(k):
    #         # select only data observations with cluster label == i
    #         #ds = df[np.where(labels==i)]
    #         # plot the data observations
    #         #pyplot.plot(ds[:,0],ds[:,1],'o')
    #         # plot the centroids
    #         lines = pyplot.plot(centroids[i,firstindex],centroids[i,secindex],'kx')
    #         # make the centroid x's bigger
    #         pyplot.setp(lines,ms=15.0)
    #         pyplot.setp(lines,mew=2.0)
    #     pyplot.show()
    #     """
    #     return newcentroids

    # ## create a new table for aggregated distributions in 2 steps:
    # ##      1. aggregate data with given intervalsize (with MEAN value)
    # ##      2. create distributions for given grain size columns for each row
    # def create_distributions(in_table, out_table, datasource, intervalsize=60, custom_classes_dict=None):
    #     df = datasource.get_data(name=in_table).df()
    #     ## which columns to keep?
    #     # df = df[[TIME_ATTR] + GRAIN_COLS]
    #     df = df[GRAIN_COLS]
    #
    #     ## store column-reduced table
    #     datasource.store_df(df=df, name="cluster_graincols")
    #     ## aggregate values in time intervals
    #     datasource.aggregateTime(out_table="cluster_aggr", mode="AVG", minutes=intervalsize,
    #                              in_table="cluster_graincols")
    #     df = datasource.get_data(name="cluster_aggr").df()
    #
    #     ## iterate through aggregated values,
    #     ## calculate frequencies for each row,
    #     ## and store it into a new dataframe
    #     data = dict()  ## dictionary for results
    #     if custom_classes_dict == None:
    #         for col in GRAIN_COLS:
    #             data[col] = list()
    #     else:
    #         custom_cols = sorted(custom_classes_dict.keys())
    #         for k in custom_cols:
    #             data[k] = list()
    #
    #     # data[TIME_ATTR] = list()
    #
    #     # print(df.describe())
    #
    #     ## iterate through rows
    #     for index, row in df.iterrows():
    #         ## check for NA and ignore rows with missing values
    #         if not row.isnull().any():
    #             ## calculate sum of row
    #             ## TODO: how to handle negative values?
    #             ## (dirty fix for negative values: absolute values)
    #             rowsum = float(sum([abs(x) for x in row[GRAIN_COLS]]))
    #             if rowsum == 0:  ## no particles found in interval
    #                 ## TODO: how to handle rows with only 0?
    #                 pass  ## now: ignore
    #                 # for col in grain_columns:
    #                 #   data[col].append(0)
    #             else:
    #                 if custom_classes_dict == None:
    #                     for col in GRAIN_COLS:
    #                         freq = abs(row[col]) / rowsum
    #                         data[col].append(freq)
    #                         # if freq < 0 or freq > 1:
    #                         #    print(row)
    #                         #    print("freq: "+str(freq))
    #                         # print(str(freq)+",",)
    #                 else:
    #                     for col in custom_cols:
    #                         comb_freq = 0
    #                         for grain in custom_classes_dict[col]:
    #                             freq = abs(row[grain]) / rowsum
    #                             comb_freq += freq
    #                         data[col].append(comb_freq)
    #                         # data[TIME_ATTR].append(row[TIME_ATTR])
    #
    #     df = pd.DataFrame(data)
    #     # print(df.describe())
    #     datasource.store_df(df=pd.DataFrame(data), name="cluster_distr")
    #     # self.table_store[out_table]=DataTable(df=pd.DataFrame(data))
    #     # print(table_store[out_table])
    #     # calc_clusters(in_table="cluster_distr", out_table="clustered", datasource=datasource, k=4)

    def get_time_colname(self):
        return TIME_ATTR

    def df(self,name)-> pd.DataFrame:
        return self.get_data(name).df()

    def get_grain_columns(self):
        if "Large" in self.base().get_attr_names():
            return ["Small","Large"]
        else:
            return  ["GrainSize0_25", "GrainSize0_28", "GrainSize0_30", "GrainSize0_35", "GrainSize0_40",
                     "GrainSize0_45", "GrainSize0_50", "GrainSize0_58", "GrainSize0_65", "GrainSize0_70",
                     "GrainSize0_80", "GrainSize1_0", "GrainSize1_3", "GrainSize1_6", "GrainSize2_0", "GrainSize2_5",
                     "GrainSize3_0", "GrainSize3_5", "GrainSize4_0", "GrainSize5_0", "GrainSize6_5", "GrainSize7_5",
                     "GrainSize8_0", "GrainSize10_0", "GrainSize12_5", "GrainSize15_0", "GrainSize17_5",
                     "GrainSize20_0", "GrainSize25_0", "GrainSize30_0", "GrainSize32_0"]





if __name__ == "__main__":
    from datetime import datetime
    ds = DataSource()
    ds.read_data("../data/dust-2014.dat")
    print("read")
    data=ds.get_base_data().df()
    #days=data["MasterTime"].map(lambda x: x % (24*3600))#(x.year, x.month, x.day))
    #print(days)
    #print(data.groupby([pd.DatetimeIndex(data["MasterTime"]) ]).count())
    print( )




