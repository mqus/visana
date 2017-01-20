import datasource

## (temporary) test script
ds=datasource.DataSource()
ds.read_data("../data/dust-32-grain-size-classes-2014.dat")
print(ds.get_data("base").df().head())
#ds.select("selection","Small",3680,3680)
#ds.project("proj","Large","OutdoorTemp",in_table="selection")
ds.aggregateTime("aggro", "AVG", minutes=360)
ds.aggregateTime("aggro2", "AVG", 24*60, "aggro")
#ds.groupby("all_days", "MasterTime", "COUNT", "base", bydate=True)
print(ds.get_data("aggro").df().head())
print("------------------------")
print(ds.get_data("aggro2").df().head())

#for i,r in ds.get_base_data().df().iterrows():
#    print(i,type(r['MasterTime']), type(r['Large']), type(r['OutdoorTemp']))
#    if i>3:
#        break















































































