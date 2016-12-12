import sys
import time
import datasource
import random
if len(sys.argv) is not 2:
    print("profile needs an input file as argument")


## set seed for comparable runs
random.seed(0)
## how many runs ?
runCnt = 10
##number of input-data rows(will be filled in later)
size=0

## create random conditions for the SELECT-function
## return one attribute with random min-max values
## 	(condCnt: number of random conditions in result)
def createSelectConds(attributes, ranges, condCnt):
	selectConds = []
	for i in range(0, condCnt):
		## which attribute?
		rdmAttr = random.choice(attributes)
		## range for this attribute
		attrRange = ranges[rdmAttr]
		## random value from whole attribute range
		rdmMin = random.randint(attrRange[0], attrRange[1])
		rdmMax = random.randint(rdmMin, attrRange[1])
		selectConds.append((rdmAttr, rdmMin, rdmMax))

	return selectConds

## create random conditions for the AGGREGATE-function
## returns random subset of attributes, random function and random RANGE value
## 	(condCnt: number of random conditions in result)
def createAggrConds(attributes, ranges, condCnt):
	aggrConds = []
	for i in range(0, condCnt):
		## how many attributes?
		attrCnt = random.randint(1, len(attributes))
		aggrAttrs = []
		## copy attribute list so we can delete items that were already picked
		attrCopy = attributes[:]
		for j in range(0, attrCnt):
			## pick random attribute
			attrIndex = random.randint(0, len(attrCopy)-1)
			aggrAttrs.append(attrCopy[attrIndex])
			del attrCopy[attrIndex]
		## which function?
		aggrFct = random.choice(["MIN", "MAX", "AVG"])
		## which limit/range value?
		aggrLimit = random.randint(1, 1000)
		aggrConds.append((aggrFct, aggrAttrs, aggrLimit))


	return aggrConds

## attribute definitions with ranges
## [this are the same values as used in make_sample.py,
## combining both to one definition would be better]
attributes = ["natural1", "natural2", "float1", "integer1"]
ranges = {}
ranges["natural1"] = [0, 1000]
ranges["natural2"] = [0, 10000000]
ranges["float1"] = [-10, 30]
ranges["integer1"] = [-1000, 1000]

## create random conditions
selectConds = createSelectConds(attributes, ranges, runCnt)
aggrConds = createAggrConds(attributes, ranges, runCnt)


## test output
#print("SELECT:")
#print(len(selectConds))
#for c in selectConds:
#	print("\t",str(c))
#print("Aggregate:")
#print(len(aggrConds))
#for c in aggrConds:
#	print("\t",str(c))
 
ds=datasource.DataSource()
#print("id;natural1;natural2;float1;integer1")

## dictionary for saving runtimes per function
runtimes = {}
runtimes["READ"] = []
runtimes["SELECT"] = []
runtimes["PROJECT"] = []
runtimes["AGGREGATE"] = []

for i in range(0, runCnt):
	## READ
	start=time.perf_counter()
	ds.read_data(sys.argv[1])
	stop=time.perf_counter()
	runtimes["READ"].append((stop-start))
	size=ds.get_base_data().get_count()
	#print("read: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms. "
	 #               "(size:" + str(ds.get_base_data().get_count()) + ")")

	## SELECT
	start=time.perf_counter()
	curSelConds = selectConds[i]
	#print(curConds)
	ds.select("selection",curSelConds[0],curSelConds[1],curSelConds[2])
	stop=time.perf_counter()
	runtimes["SELECT"].append((stop-start))
	#print("sel : " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms. "
	#                "(size:" + str(ds.get_data("selection").get_count()) + ")")

	## PROJECT
	start=time.perf_counter()
	ds.project("proj","float1","integer1")
	stop=time.perf_counter()
	runtimes["PROJECT"].append((stop-start))
	#print("proj: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms.")

	## AGGREGATE
	start=time.perf_counter()
	curAggrConds = aggrConds[i]
	#print(curConds)
    ds.aggregate("aggro", curAggrConds[0], limit=curAggrConds[2])
	stop=time.perf_counter()
	runtimes["AGGREGATE"].append((stop-start))
	#print("aggr: " + str((stop-start)*1000) + "ms \tper 1k entries: " + str((stop-start)*1000*1000/size) + "ms.")

## create proper output
output = [sys.argv[1].split(".")[0]] ## file name
## calculate average run time for each function
for k in sorted(runtimes.keys()):
	avg = sum(runtimes[k])/len(runtimes[k])
	output.append(k+":%.6fs"%avg)
##calculate average runtime for 1000 rows in milliseconds
for k in sorted(runtimes.keys()):
	avg = sum(runtimes[k])/len(runtimes[k])/size*1000*1000
	output.append(k+" per 1k:%.6fms"%avg)

print("\t".join(output))
