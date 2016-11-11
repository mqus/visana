import pandas as pd

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
		df = self.table_store[in_table].df()

		df = df.loc[df[attr_name] >= a]
		df = df.loc[df[attr_name] <= b]

		self.table_store[out_table] = data_table(df=df)

	def project(self,out_table,attr1,attr2,in_table="base"):
		df = self.table_store[in_table].df()

		df = df[[attr1, attr2]]

		self.table_store[out_table] = data_table(df=df)

	def aggregate(self,out_table,mode,attr_names,limit=0,in_table="base"):
		df = self.table_store[in_table].df() #type:pd.DataFrame
		#new_df = pd.DataFrame(columns=attr_names)
		#only view selected columns
		df = df[attr_names]
		data=dict()
		if limit is 0:
			limit=len(df.index)
		#iterate over columns
		for attr,values in df.iteritems():
			data[attr]=list()
			i=0
			sum=0
			min=0
			max=0
			for value in values:
				if i % limit == 0:
					min=value
					max=value
					sum=0
				else:
					if value<min:
						min=value
					if value>max:
						max=value
				sum=sum+value
				i=i+1
				if i % limit is 0:
					insval=0
					if mode is "AVG":
						insval=sum/limit
					elif mode is "MAX":
						insval=max
					elif mode is "MIN":
						insval=min
					data[attr].append(insval)
					#new_df.insert(int(i / limit), attr, insval)
		self.table_store[out_table]=data_table(df=pd.DataFrame(data))





