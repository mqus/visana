## abstract
class data_iter:
	def next():
		pass

	def hasNext():
		pass

	def reset():
		pass

## abstract
class data_store:
	def get_count():
		pass

	def get_iter():
		pass

## abstract
class data_table(data_store):
	def get_attr_count():
		pass

	def get_attr_names():
		pass