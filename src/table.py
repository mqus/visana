import pandas as pd

##  abstract
class data_iter:
	def next(self):
		pass

	def hasNext(self):
		pass

	def reset(self):
		pass

## abstract
class data_store:
	def get_count(self):
		pass

	def get_iter(self):
		pass

## abstract
class data_table(data_store):
	def __init__(self,path):
		self.table=pd.read_csv(path,sep=";",na_values="NA",index_col=0)
		pass

	def get_attr_count(self):
		pass#return self.table.`

	def get_attr_names(self):
		pass