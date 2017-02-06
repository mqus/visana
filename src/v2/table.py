import pandas as pd
import numpy as np

class DataTable:
	## initiate with either csv file path or dataframe
	indexName="MasterTime"

	centroids=None

	def __init__(self,path="",df=pd.DataFrame(), centroids=None):
		if path is "":
			self.table=df #type:pd.DataFrame
		else:
			self.table=pd.read_csv(path,sep=";",na_values="NA",parse_dates=[self.indexName])#type:pd.DataFrame
			self.table=self.table.set_index(self.indexName, drop=False)

			# calculate minute of day and insert it
			anchor=np.datetime64('2000-01-01T00:00')
			day=np.timedelta64(1, 'D')
			since2k=self.table.index.values - anchor #type:np.ndarray
			self.table["Daytime"] = np.rint(np.remainder(since2k/day,1)*1440)

		if centroids is not None:
			self.centroids=centroids
	## return dataframe
	def df(self):
		return self.table

	## return number of attributes
	def get_attr_count(self):
		return len(self.table.columns.values)

	## return list of attribute names
	def get_attr_names(self):
		return list(self.table.columns.values)
		#return np.append(self.table.columns.values,[self.indexName])

	## return number of tuples in table
	def get_count(self):
		return len(self.table)

	def get_column(self,colname):
		if colname == self.indexName:
				return self.table.index.values
		return self.table[colname]

	def is_clustered(self):
		return self.centroids is not None


	#def getcolumns(self):
#		return np.append(self.table.)