import pandas as pd

class DataTable:
	## initiate with either csv file path or dataframe
	def __init__(self,path="",df=pd.DataFrame()):
		if path is "":
			self.table=df #type:pd.DataFrame
		else:
			self.table=pd.read_csv(path,sep=";",na_values="NA",parse_dates=["MasterTime"]) #type:pd.DataFrame
		
	## return dataframe
	def df(self):
		return self.table

	## return number of attributes
	def get_attr_count(self):
		return len(self.table.columns.values)

	## return list of attribute names
	def get_attr_names(self):
		return self.table.columns.values

	## return number of tuples in table
	def get_count(self):
		return len(self.table)
