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
        if attr_name == self.get_time_colname():
            col=pd.to_datetime(df.index.values)
            #print(type(df.index.values), type(col), type(a))
        else:
            col=df[attr_name]
        if a is not None:
            df = df.loc[col >= a]
        if b is not None:
            df = df.loc[col <= b]

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
                elif equation["comp"] == "!=":
                    tmp_df = tmp_df.loc[tmp_df[param] != val]
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

        #delete all inf
        df = df.replace([np.inf, -np.inf], np.nan)

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
        df = df.copy() # type:pd.DataFrame

        kmeans = cluster.KMeans(n_clusters=k, n_jobs=-1)
        kmeans.fit(df[params])
        #centroids = kmeans.cluster_centers_

        # ORDER LABELS BY CENTROID
        cent_map = dict()
        centroids = kmeans.cluster_centers_

        # print("centr")
        # print(centroids)
        # print(type(centroids))

        # attach original index to each first centroid value
        temp_cent_order = [ [c, centroids[c, 0]] for c in range(0, len(centroids)) ]

        # temp_cent_order = []
        #
        # for c in range(0, len(centroids)):
        #     t = [c, centroids[c, 0]]
        #     temp_cent_order.append(t)

        # print(temp_cent_order)

        # order by the centroid value
        cent_order = sorted(temp_cent_order, key=lambda x: x[1], reverse=True)

        #cent_map = []
        for c in range(0, len(centroids)):
            cent_map[cent_order[c][0]] = c
        # print(cent_order)
        # print(cent_map)

        newcentroids = [centroids[cent_order[c][0]] for c in range(0, len(centroids))]
        #for c in range(0, len(centroids)):
        #    newcentroids.append(centroids[cent_order[c][0]])
        # print(np.asarray(newcentroids))

        labels = kmeans.labels_
        # print("lbl")
        # print(labels)
        # print(len(labels))
        #print("lbstart")
        newlabels = []
        for label in labels:
            newlabels.append(cent_map[label])
        df["_cluster"] = newlabels
        #print("lb  end")

        #df["_color"] =df.apply(lambda row:COLORS[row["_label"]], axis=1)

        self.table_store[out_table] = DataTable(df=df, centroids=newcentroids)


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

    def get_significant_nan_columns(self):
        cols=["OutdoorTemp", "RelHumidity"]
        if "Large" in self.base().get_attr_names():
            cols.append("Small")
        else:
            cols.append("GrainSize0_25")
        return cols



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




