import sys
import time
import datasource
if len(sys.argv) is not 2:
    print("profile needs an input file as argument")

ds=datasource.DataSource()
#print("id;natural1;natural2;float1;integer1")

start=time.perf_counter()
ds.read_data(sys.argv[1])
stop=time.perf_counter()
size=ds.get_base_data().get_count()
print("read: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms. "
                "(size:" + str(ds.get_base_data().get_count()) + ")")

start=time.perf_counter()
ds.select("selection","natural1",500,1000)
stop=time.perf_counter()
print("sel : " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms. "
                "(size:" + str(ds.get_data("selection").get_count()) + ")")

start=time.perf_counter()
ds.project("proj","float1","integer1")
stop=time.perf_counter()
print("proj: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms.")


start=time.perf_counter()
ds.aggregate("aggro","MAX",["natural2","natural1"],limit=100)
stop=time.perf_counter()
print("aggr: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms.")

