import datasource

ds=datasource.data_source()
ds.read_data("../../dust-2014.dat")
ds.select("selection","Small",3680,3680)
#ds.project("proj","Large","OutdoorTemp",in_table="selection")
ds.aggregate("aggro","MAX",["Small","Large"],limit=5,in_table="selection")
print(ds.get_table_store()["aggro"].df())
