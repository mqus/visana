

# update levels, each level includes all lower ones
# Controls on the left
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

        #change after each save
        self.custom_classes=[]

        #change only after recalc
        self.cluster_params=[]
        self.class_params=dict()





    def ds_changed(self):
        self.ds = self.window.ds
        #do all calculations


    def recalc(self,level):
        i=0 # just a small counter on what operations have been done.
        if level>=SELECTOR:
            i+=1
            self.window.status.set(str(i)+": Apply Selector...")
            clause = self.window.options.clause
            if clause is None:
                self.ds.link("selector","base")
            else:
                print("select",clause)
                self.ds.select_complex("selector", clause, "base" )

        if level >= AGGREGATOR:
            i+=1
            agg_level = self.window.options.get_n()
            if agg_level <= 1:
                self.ds.link("aggregator","selector")
            else:
                print("aggre",agg_level)
                self.window.status.set("{}: Aggregate Values over {} minutes".format(i, agg_level))
                self.ds.aggregateTime("aggregator", "AVG", agg_level, "selector")

        if level >= NORMALIZE:
            i+=1
            params = self.ds.get_grain_columns()
            if self.window.options.shouldNormalize():
                print("norm",params)
                self.window.status.set("{}: normalize all grainsize columns".format(i))
                self.ds.normalize("normalize", params, "aggregator")
            else:
                self.ds.link("normalize", "aggregator")
        if level >= CLASSBUILDER:
            i+=1
            params = self.custom_classes
            self.class_params = params
            if params is None or len(params)==0:
                self.ds.link("newclasses","normalize")
            else:
                print("newclass",params)
                self.window.status.set("{}: Create merge parameters into {} new classes".format(i, len(params)))
                self.ds.newcols("newclasses","SUM",params, "normalize")

        if level >= CLUSTER:
            i+=1
            k = self.window.options.get_k()
            # TODO get PARAMS #UI Issue
            # temporarily take customclasses or get_all_columns
            # if self.custom_classes is None or len(self.custom_classes)==0:
            #     params=self.get_all_columns()
            # else:
            #     params=[k for k in self.custom_classes]
            #params = ["small", "large"]
            params = self.window.options.get_cluster_params()
            if k<=1 or params is None or len(params) == 0:
                self.cluster_params=[]
                self.ds.link("cluster","newclasses")
            else:
                print("cluster",k,params)
                self.cluster_params=params
                self.window.status.set("{}: Search for k={} clusters by applying k-means on {} parameters"
                                        .format(i, k, len(params)))
                self.ds.cluster("cluster",k,params,"newclasses")
        if level >= PLOT:
            self.window.redo_plots()


    def get_all_columns(self, with_time=False):
        # add all colnames of base (except time, if wanted)
        cols = [col for col in self.ds.base().get_attr_names() if with_time or not col==self.ds.get_time_colname() ]
        # add all custom names
        if self.custom_classes is not None:
            cols.extend([cc for cc in self.custom_classes])
        return cols

    def cclasses_changed(self, newclasses):
        self.custom_classes=newclasses
        self.window.options.classes_changed()





