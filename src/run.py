import datasource

## (temporary) test script
ds=datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
ds.select("selection","Small",3680,3680)
#ds.project("proj","Large","OutdoorTemp",in_table="selection")
ds.aggregate("aggro", "MAX", limit=5, in_table="selection")
print(ds.get_data("aggro").df())

#for i,r in ds.get_base_data().df().iterrows():
#    print(i,type(r['MasterTime']), type(r['Large']), type(r['OutdoorTemp']))
#    if i>3:
#        break
