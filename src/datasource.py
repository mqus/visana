from table import data_table


class data_source:

	def __init__(self):
		self.table_store=dict()

	def get_table_count(self):
		return len(self.table_store)

	def get_base_data(self):
		return self.table_store["base"]
		pass

	def get_table_store(self):
		return self.table_store


	def read_data(self,path):
		self.table_store["base"]=data_table(path)
		pass

	def select(self,out_table,attr_name,a,b,in_table="base"):
		df = self.table_store[in_table]

		df = df.loc[df[attr_name] > a]
		df = df.loc[df[attr_name] < b]

		self.table_store[out_table] = df

	def project(self,out_table,attr1,attr2,in_table="base"):
		df = self.table_store[in_table]

		df = df[[attr1, attr2]]

		self.table_store[out_table] = df

	def aggregate(self,out_table,mode,attr_names,limit=0,in_table="base"):
		pass




