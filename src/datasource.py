import pandas as pd

from table import DataTable


class DataSource:

	def __init__(self):
		self.table_store=dict()

	## return number of tables in this Source
	def get_table_count(self):
		return len(self.table_store)

	## return table with the given name
	def get_data(self,table):
		return self.table_store[table]

	## return base table with original data
	def get_base_data(self):
		return self.table_store["base"] #type:DataTable

	## return the dictionary with all tables
	def get_table_store(self):
		return self.table_store

	## construct base table with csv file at given path
	def read_data(self,path):
		self.table_store["base"]=DataTable(path)

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

	## perform aggregation on data
	##	out_table: name of new table with results
	##	mode: how to aggregate data? AVG, MIN or MAX
	##	attr_names: list of attributes to aggregate and keep in results
	##	limit (or 'range'): only aggregate that many rows for each resulting row
	## 	in_table: table to perform the aggregation on
	def aggregate(self,out_table,mode,attr_names,limit=0,in_table="base"):
		df = self.table_store[in_table].df() #type:pd.DataFrame
		#new_df = pd.DataFrame(columns=attr_names)
		## only view selected columns
		df = df[attr_names]
		data=dict() ## dictionary for results
		## aggregate all rows in one step if limit is 0
		if limit is 0:
			limit=len(df.index)
		## iterate over columns
		for attr,values in df.iteritems():
			data[attr]=list()
			i=0
			## track data characteristics for result
			sum=0
			min=0
			max=0
			for value in values:
				## update min, max and sum for each value
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
				## produce new result row if i%limit==0
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

		## store results in new table
		self.table_store[out_table]=DataTable(df=pd.DataFrame(data))





