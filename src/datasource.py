import pandas as pd
import numpy as np

from table import DataTable


class DataSource:

	def __init__(self):
		self.table_store=dict()

	## return number of tables in this Source
	def get_table_count(self):
		return len(self.table_store)

	## return table with the given name
	def get_data(self, name):
		return self.table_store[name]

	## return base table with original data
	def get_base_data(self):
		return self.table_store["base"] #type:DataTable

	## return the dictionary with all tables
	def get_table_store(self):
		return self.table_store

	## construct base table with csv file at given path
	def read_data(self,path):
		self.table_store["base"]=DataTable(path)

	def pop_table(self,name):
		self.table_store.pop(name)

	## perform a selection on data
	##	out_table: name of new table with results
	##	attr_name: attribute for the selection
	##	a: min-value for this attribute
	##	b: max-value for this attribute
	## 	in_table: table to perform the selection on
	def select(self,out_table,attr_name,a,b,in_table="base"):
		df = self.table_store[in_table].df()

		## select the according tuples for these boundaries
		## for the given attribute
		df = df.loc[df[attr_name] >= a]
		df = df.loc[df[attr_name] <= b]

		## store results in new table
		self.table_store[out_table] = DataTable(df=df)

	## perform a groupby aggregation on data
	##	out_table: name of new table with results
	##	attr: attribute or list of attributes to group by
	##	mode: aggregation mode of the other columns
	## 	in_table: table to perform the projection on
	def groupby(self,out_table,attr, mode,in_table="base", bydate=False):
		df = self.table_store[in_table].df()
		if bydate:
			by=data[attr].dt.normalize()
		else:
			by=data[attr]

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
		self.table_store[out_table] = DataTable(df=out)

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
			if attr == "MasterTime":
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

		self.table_store[out_table]=DataTable(df=pd.DataFrame(data))
		#print(table_store[out_table])

	#select with multiple ids
	def select_ids(self,out_table, ids, in_table="base"):
		df = self.table_store[in_table].df()  # type:pd.DataFrame
		df= df.loc[ids]
		self.table_store[out_table] = DataTable(df=df)




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




