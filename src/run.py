import datasource

ds=datasource.data_source()
ds.read_data("../../dust-2014.dat")
print(ds.get_base_data().table)
