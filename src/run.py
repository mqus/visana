import datasource

ds=datasource.DataSource()
ds.read_data("../../dust-2014.dat")
ds.select("selection","Small",3680,3680)
#ds.project("proj","Large","OutdoorTemp",in_table="selection")
ds.aggregate("aggro","MAX",["Small","Large"],limit=5,in_table="selection")
print(ds.get_data("aggro").df())
