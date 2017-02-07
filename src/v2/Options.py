import tkinter as tk
from tkinter import N,E,W,S
from tkinter import ttk

from Selector import Selector
from DataTasks import AGGREGATOR, SELECTOR
#from v2.Window import VisAnaWindow


class Options(tk.Frame):
    cluster_limit=10
    aggreg_limit=1440#24h*60min
    def __init__(self, parent,master):
        super(Options, self).__init__(parent)
        self.window=master #type:VisAnaWindow
        self.ds=master.ds
        self.columnconfigure(1, weight=1)
        self.columnconfigure(0,weight=1)
        self.clause = None


        # draw aggregation setter
        nlbl=tk.Label(self,text="1: aggregated Minutes, n=")
        nlbl.grid(column=0, row=1, sticky=(E, N))

        self.n = tk.StringVar(self)
        self.n.set(str(1))
        self.n_spin = tk.Spinbox(self, from_=1, to=self.aggreg_limit, textvariable=self.n ,width=4)
        self.n_spin.grid(column=1, row=1, sticky=(W, N))

        #Normalize?
        #nolbl=tk.Label(self, text='3: Normalize grain sizes/\ncalculate with histograms:')
        nolbl=tk.Label(self, text='2: Take relative count per Grainsize-Class:')
        nolbl.grid(column=0, row=2, sticky=(E, N))
        self.novar = tk.StringVar(value="0")
        nocb = ttk.Checkbutton(self, text="", variable=self.novar)
        nocb.grid(column=1, row=2, sticky=(W, N))

        # draw #cluster setter
        klbl=tk.Label(self,text="3: # of Clusters, k=")
        klbl.grid(column=0, row=3, sticky=(E,N))

        self.k = tk.StringVar(self)
        self.k.set(str(1))
        self.k_spin = tk.Spinbox(self, from_=1, to=self.cluster_limit, textvariable=self.k ,width=4)
        self.k_spin.grid(column=1, row=3, sticky=(W, N))

        #TODO: Clusterparams
        frm = tk.LabelFrame(self, text="4. Select features to cluster with")
        frm.grid(column=0, row=4, sticky=(W, N,E), columnspan=2)
        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(0,weight=1)
        # select params on which the cluster is calculated
        self.cluvar = tk.StringVar("")
        self.clusterparams = tk.Listbox(frm, selectmode="extended", height=20, listvariable=self.cluvar)
        self.clusterparams.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W, tk.S))
        cluscrbar= tk.Scrollbar(frm, orient=tk.VERTICAL, command=self.clusterparams.yview)
        cluscrbar.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S))
        self.clusterparams["yscrollcommand"] = cluscrbar.set

        #for col in self.window.ds.get_grain_columns():
        #    self.clusterparams.insert(END, col)
        #self.clusterparams.grid(row=1, column=0, rowspan=10)


        self.refrbutton = tk.Button(self)
        self.refrbutton["text"] = "recalculate (takes up to 20sec)"
        self.refrbutton["command"] = self.handle_refresh_btn
        self.refrbutton.grid(column=0, row=5, sticky=(W, N,E), columnspan=2)




    def classes_changed(self):
        self.cluvar.set(list(self.window.calc.get_all_columns()))

    def handle_refresh_btn(self):
        self.window.calc.recalc(AGGREGATOR)
        return

    def get_n(self):
        return int(self.n.get())
    def get_k(self):
        return int(self.k.get())
    def shouldNormalize(self):
        return not self.novar.get() == "0"

    def get_cluster_params(self):
        selected = self.clusterparams.curselection()
        if len(selected) is 0:
            return None
        return [self.clusterparams.get(i) for i in selected]

    def ds_changed(self):
        self.ds = self.window.ds
        self.classes_changed()



class ScrollableOptions(tk.Canvas):
    pass#TODO