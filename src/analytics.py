from datasource import TIME_ATTR, GRAIN_COLS
import pandas as pd
from sklearn import cluster
from matplotlib import pyplot
import numpy as np

def create_distributions(in_table, out_table, datasource, intervalsize=360):
	df = datasource.get_data(name=in_table).df()
	## which columns to keep? 
	df = df[[TIME_ATTR] + GRAIN_COLS]
	## store column-reduced table
	datasource.store_df(df=df, name="cluster_graincols")
	## aggregate values in time intervals
	datasource.aggregate(out_table="cluster_aggr", mode="AVG", limit=intervalsize, in_table="cluster_graincols")
	df = datasource.get_data(name="cluster_aggr").df()

	## iterate through aggregated values,
	## calculate frequencies for each row,
	## and store it into a new dataframe
	data=dict() ## dictionary for results
	for col in GRAIN_COLS:
		data[col] = list()
	data[TIME_ATTR] = list()

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
				#	data[col].append(0)
			else:
				for col in GRAIN_COLS:
					freq = abs(row[col]) / rowsum
					data[col].append(freq)
					if freq < 0 or freq > 1:
						print(row)
						print("freq: "+str(freq))
					#print(str(freq)+",",)
				data[TIME_ATTR].append(row[TIME_ATTR])

	df=pd.DataFrame(data)
	print(df.describe())
	datasource.store_df(df=pd.DataFrame(data), name="cluster_distr")
	#self.table_store[out_table]=DataTable(df=pd.DataFrame(data))
	#print(table_store[out_table])
	calc_clusters("cluster_distr", datasource, k=2)

def calc_clusters(in_table, datasource, k):
	print("CLUSTERING")
	df = datasource.get_data(in_table).df()
	kmeans = cluster.KMeans(n_clusters=k)
	kmeans.fit(df[["Small", "Large"]])

	labels = kmeans.labels_
	#print("labels: ")
	#print(labels)
	#print("labelsLEN: "+str(len(labels)))
	#for i in labels:
#		print(i)
	df['labels'] = labels
	#print(df.describe())
	#print(df[TIME_ATTR])

	centroids = kmeans.cluster_centers_
	#print("centroids: ")
	#print(centroids)

	pyplot.scatter(df["Small"], df["Large"])
	for i in range(k):
	    # select only data observations with cluster label == i
	    #ds = df[np.where(labels==i)]
	    # plot the data observations
	    #pyplot.plot(ds[:,0],ds[:,1],'o')
	    # plot the centroids
	    lines = pyplot.plot(centroids[i,0],centroids[i,1],'kx')
	    # make the centroid x's bigger
	    pyplot.setp(lines,ms=15.0)
	    pyplot.setp(lines,mew=2.0)
	pyplot.show()
