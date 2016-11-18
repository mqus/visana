import pandas as pd

class DataTable:
	def __init__(self,path="",df=pd.DataFrame()):
		if path is "":
			self.table=df #type:pd.DataFrame
		else:
			self.table=pd.read_csv(path,sep=";",na_values="NA",index_col=0) #type:pd.DataFrame
		
	def df(self):
		return self.table

	def get_attr_count(self):
		return len(self.table.columns.values)

	def get_attr_names(self):
		return self.table.columns.values

	def get_count(self):
		return len(self.table)
