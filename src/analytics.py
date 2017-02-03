from datasource import TIME_ATTR, GRAIN_COLS, GRAIN_COLS2
import pandas as pd
from sklearn import cluster
from matplotlib import pyplot
import numpy as np

## create a new table for aggregated distributions in 2 steps:
##      1. aggregate data with given intervalsize (with MEAN value)
##      2. create distributions for given grain size columns for each row
def create_distributions(in_table, out_table, datasource, intervalsize=60):
    df = datasource.get_data(name=in_table).df()
    ## which columns to keep? 
    #df = df[[TIME_ATTR] + GRAIN_COLS]
    df = df[GRAIN_COLS]

    ## store column-reduced table
    datasource.store_df(df=df, name="cluster_graincols")
    ## aggregate values in time intervals
    datasource.aggregateTime(out_table="cluster_aggr", mode="AVG", minutes=intervalsize, in_table="cluster_graincols")
    df = datasource.get_data(name="cluster_aggr").df()

    ## iterate through aggregated values,
    ## calculate frequencies for each row,
    ## and store it into a new dataframe
    data=dict() ## dictionary for results
    for col in GRAIN_COLS:
        data[col] = list()
    #data[TIME_ATTR] = list()

    #print(df.describe())

    ## iterate through rows
    for index, row in df.iterrows():
        #print("row:")
        #print(row)
        #print(row.isnull().any())
        ## check for NA and ignore rows with missing values
        if not row.isnull().any():
            ## calculate sum of row
            ## TODO: how to handle negative values?
            ## (dirty fix for negative values: absolute values)
            rowsum = float(sum([abs(x) for x in row[GRAIN_COLS]]))
            if rowsum == 0: ## no particles found in interval
                ## TODO: how to handle rows with only 0?
                pass ## now: ignore
                #for col in grain_columns:
                #   data[col].append(0)
            else:
                for col in GRAIN_COLS:
                    freq = abs(row[col]) / rowsum
                    data[col].append(freq)
                    if freq < 0 or freq > 1:
                        print(row)
                        print("freq: "+str(freq))
                    #print(str(freq)+",",)
                #data[TIME_ATTR].append(row[TIME_ATTR])

    df=pd.DataFrame(data)
    #print(df.describe())
    datasource.store_df(df=pd.DataFrame(data), name="cluster_distr")
    #self.table_store[out_table]=DataTable(df=pd.DataFrame(data))
    #print(table_store[out_table])
    #calc_clusters(in_table="cluster_distr", out_table="clustered", datasource=datasource, k=4)

def calc_clusters(in_table, out_table, datasource, k):
    print("CLUSTERING")
    df = datasource.get_data(in_table).df()
    kmeans = cluster.KMeans(n_clusters=k)
    kmeans.fit(df[GRAIN_COLS])

    cent_map = {}
    centroids = kmeans.cluster_centers_
    temp_cent_order = []
    for c in range(0, len(centroids)):
        t = [c, centroids[c, 0]]
        temp_cent_order.append(t)

    print(temp_cent_order)
    cent_order = sorted(temp_cent_order, key=lambda x:x[1], reverse=True)
    for c in range(0, len(centroids)):
        cent_map[temp_cent_order[c][0]] = cent_order[c][0]
    print(cent_order)
    print(cent_map)

    newcentroids = []
    for c in range(0, len(centroids)):
        newcentroids.append(centroids[cent_order[c][0]])
    print(np.asarray(newcentroids))


    labels = kmeans.labels_
    newlabels = []
    for label in labels:
        newlabels.append(cent_map[label])

    print(type(labels))
    print(type(np.asarray(newlabels)))
    #print(labels)
    #print(newlabels)
    #print("labels: ")
    #print(labels)
    #print("labelsLEN: "+str(len(labels)))
    #for i in labels:
#       print(i)
    df['clusterlabels'] = newlabels
    #print(df.describe())
    #print(df[TIME_ATTR])


    datasource.store_df(df=df, name=out_table)


    #print("centroids: ")
    #print(centroids)
    debugprint="""
    print(centroids)

    firstcentroids = df.loc[df['clusterlabels'] == 0]
    seccentroids = df.loc[df['clusterlabels'] == 1]
    qcentroids = df.loc[df['clusterlabels'] == 2]
    acentroids = df.loc[df['clusterlabels'] == 3]

    firstindex = 0
    secindex = 25
    #pyplot.scatter(firstcentroids["Small"], firstcentroids["Large"], color="red")
    #pyplot.scatter(seccentroids["Small"], seccentroids["Large"], color="blue")
    pyplot.scatter(firstcentroids[GRAIN_COLS[firstindex]], firstcentroids[GRAIN_COLS[secindex]], color="red")
    pyplot.scatter(seccentroids[GRAIN_COLS[firstindex]], seccentroids[GRAIN_COLS[secindex]], color="blue")
    pyplot.scatter(qcentroids[GRAIN_COLS[firstindex]], qcentroids[GRAIN_COLS[secindex]], color="green")
    pyplot.scatter(acentroids[GRAIN_COLS[firstindex]], acentroids[GRAIN_COLS[secindex]], color="yellow")

    for i in range(k):
        # select only data observations with cluster label == i
        #ds = df[np.where(labels==i)]
        # plot the data observations
        #pyplot.plot(ds[:,0],ds[:,1],'o')
        # plot the centroids
        lines = pyplot.plot(centroids[i,firstindex],centroids[i,secindex],'kx')
        # make the centroid x's bigger
        pyplot.setp(lines,ms=15.0)
        pyplot.setp(lines,mew=2.0)
    pyplot.show()
    """
    return newcentroids
