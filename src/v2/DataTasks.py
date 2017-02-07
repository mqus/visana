

# update levels, each level includes all lower ones
# Controls on the left
from Selector import tostr
from datasource import DataSource
#import v2.Window
ALL=20
SELECTOR = 14
AGGREGATOR = 13
NORMALIZE = 12
CLASSBUILDER = 11
CLUSTER = 10

PLOT=5

NOTHING = 0

# TIMELINE_SELECTION = 1
# TIMELINE_DAYSINPLOT = 2
# PLOT = 3
# PLOT_DATA = 4
# DATA_TIDYUP = 5


class Calculator:




    #def apply_change(self,fromlevel):
    #    if fromlevel>=self.SELECTOR:



    def __init__(self, window):
        self.window=window #type:v2.Window.VisAnaWindow
        self.ds = self.window.ds #type:DataSource

        #change after each change of clusters
        self.custom_classes_before_calculation=dict()

        #change only after recalc
        self.cluster_params=[]
        self.custom_classes_after_calculation=dict()





    def ds_changed(self):
        self.ds = self.window.ds
        self.custom_classes_after_calculation=dict()
        self.custom_classes_before_calculation=dict()
        self.cluster_params=[]
        #do all calculations


    def recalc(self,level):
        i=0 # just a small counter on what operations have been done.
        if level>=SELECTOR:
            i+=1
            self.window.status.set(str(i)+": Apply Selector...")
            clause = self.window.select.get_clause()
            if clause is None:
                self.ds.link("selector","base")
                self.addToHistory(i,SELECTOR,False)
            else:
                print("select",clause)
                self.ds.select_complex("selector", clause, "base" )
                self.addToHistory(i,SELECTOR,True,clause)

        if level >= AGGREGATOR:
            i+=1
            agg_level = self.window.options.get_n()
            if agg_level <= 1:
                self.ds.link("aggregator","selector")
                self.addToHistory(i,AGGREGATOR,False)
            else:
                print("aggre",agg_level)
                self.window.status.set("{}: Aggregate Values over {} minutes".format(i, agg_level))
                self.ds.aggregateTime("aggregator", "AVG", agg_level, "selector")
                self.addToHistory(i,AGGREGATOR,True,agg_level)

        if level >= NORMALIZE:
            i+=1
            params = self.ds.get_grain_columns()
            if self.window.options.shouldNormalize():
                print("norm",params)
                self.window.status.set("{}: normalize all grainsize columns".format(i))
                self.ds.normalize("normalize", params, "aggregator")
                self.addToHistory(i,NORMALIZE, True)
            else:
                self.ds.link("normalize", "aggregator")
                self.addToHistory(i, NORMALIZE, False,)

        if level >= CLASSBUILDER:
            i+=1
            params = self.custom_classes_before_calculation
            self.custom_classes_after_calculation = params
            if params is None or len(params)==0:
                self.ds.link("newclasses","normalize")
                self.addToHistory(i,CLASSBUILDER,False)
            else:
                print("newclass",params)
                self.window.status.set("{}: Merge parameters into {} new classes".format(i, len(params)))
                self.ds.newcols("newclasses","SUM",params, "normalize")
                self.addToHistory(i,CLASSBUILDER,True,params)


        if level >= CLUSTER:
            i+=1
            k = self.window.options.get_k()
            params = self.window.options.get_cluster_params()

            if k<=1 or params is None or len(params) == 0:
                self.cluster_params=[]
                self.ds.link("cluster","newclasses")
                self.addToHistory(i,CLUSTER,False)
            else:
                print("cluster",k,params)
                self.cluster_params=params
                self.window.status.set("{}: Search for k={} clusters by applying k-means on {} parameters"
                                        .format(i, k, len(params)))
                self.ds.cluster("cluster",k,params,"newclasses")
                self.addToHistory(i, CLUSTER, True, k,params)
        if level >= PLOT:
            i+=1
            self.window.redo_plots()
            self.addToHistory(i,PLOT, True)


    def get_all_columns(self, with_time=False, after_calc=False, with_custom=True):
        # add all colnames of base (except time, if wanted)
        cols = [col for col in self.ds.base().get_attr_names() if with_time or not col==self.ds.get_time_colname() ]
        # add all custom names
        if not with_custom:
            return cols
        if self.custom_classes_before_calculation is not None:
            if after_calc:
                cols.extend([cc for cc in self.custom_classes_after_calculation])
            else:
                cols.extend([cc for cc in self.custom_classes_before_calculation])
        return cols

    def cclasses_changed(self, newclasses):
        self.custom_classes_before_calculation=newclasses
        self.window.options.classes_changed()



    def addToHistory(self, i, level, done, s1=None, s2=None):
        if i ==1:
            self.window.history.add("Recalculate Clusters:")
        s = "  "+str(i)+". "
        if level is SELECTOR:
            if done:
                s += "restricted values to: "+tostr(s1)
            else:
                s += "used all of basedata"
        if level is AGGREGATOR:
            if done:
                s += "built average of {} minutes".format(s1)
            else:
                s += "didn't aggregate"
        if level is NORMALIZE:
            if done:
                s += "normalized grainsize columns of each row"
            else:
                s += "used absolute values"
        if level is CLASSBUILDER:
            if done:
                s += "created custom grain classes: {}".format(s1)
            else:
                s += "didn't create any custom classes"
        if level is CLUSTER:
            if done:
                s += "searched for k={} means of the features {}".format(s1,s2)
            else:
                s += "didn't cluster"
        if level is PLOT:
            s+="redrawed Plots"

        self.window.history.add(s)


