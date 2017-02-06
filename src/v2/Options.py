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


        self.select= Selector(self, self.ds, self.apply_select)
        self.select.grid(column=0, row=0, sticky=(E, W,N), columnspan=2)

        # draw aggregation setter
        nlbl=tk.Label(self,text="2: aggregated Minutes, n=")
        nlbl.grid(column=0, row=1, sticky=(E, N))

        self.n = tk.StringVar(self)
        self.n.set(str(1))
        self.n_spin = tk.Spinbox(self, from_=1, to=self.aggreg_limit, textvariable=self.n ,width=4)
        self.n_spin.grid(column=1, row=1, sticky=(W, N))

        #Normalize?
        nolbl=tk.Label(self, text='3: Normalize grain sizes/\ncalculate with histograms:')
        nolbl.grid(column=0, row=2, sticky=(E, N))
        self.novar = tk.StringVar(value="0")
        nocb = ttk.Checkbutton(self, text="", variable=self.novar)
        nocb.grid(column=1, row=2, sticky=(W, N))

        # draw #cluster setter
        klbl=tk.Label(self,text="4: # of Clusters, k=")
        klbl.grid(column=0, row=3, sticky=(E,N))

        self.k = tk.StringVar(self)
        self.k.set(str(1))
        self.k_spin = tk.Spinbox(self, from_=1, to=self.cluster_limit, textvariable=self.k ,width=4)
        self.k_spin.grid(column=1, row=3, sticky=(W, N))

        #TODO: Clusterparams
        # select params on which the cluster is calculated
        #self.clusterparams = tk.Listbox(self, selectmode="multiple", height=32)
        #for col in self.window.ds.get_grain_columns():
        #    self.clusterparams.insert(END, col)
        #self.clusterparams.grid(row=1, column=0, rowspan=10)


        self.refrbutton = tk.Button(self)
        self.refrbutton["text"] = "refresh"
        self.refrbutton["command"] = self.handle_refresh_btn
        self.refrbutton.grid(column=0, row=4, sticky=(W, N,E), columnspan=2)






    def handle_refresh_btn(self):
        self.window.calc.recalc(AGGREGATOR)
        return

    def apply_select(self, clause):
        self.clause = clause
        self.window.calc.recalc(SELECTOR)

    def ds_changed(self):
        self.ds=self.window.ds
        self.select.destroy()
        self.select= Selector(self, self.ds, self.apply_select)
        self.select.grid(column=0, row=0, sticky=(E, W,N), columnspan=2)

    def get_n(self):
        return int(self.n.get())
    def get_k(self):
        return int(self.k.get())
    def shouldNormalize(self):
        return not self.novar.get() == "0"


class ScrollableOptions(tk.Canvas):
    pass#TODO