import tkinter as tk
from tkinter import N,E,W,S

from Selector import Selector


class Options(tk.Frame):
    cluster_limit=10
    aggreg_limit=1440#24h*60min
    def __init__(self, parent,master):
        super(Options, self).__init__(parent)
        self.window=master
        self.ds=master.ds
        self.columnconfigure(1, weight=1)
        self.columnconfigure(0,weight=1)


        self.select=Selector(self, self.ds, self.apply_select)
        self.select.grid(column=0, row=0, sticky=(E, W,N), columnspan=2)

        # draw #cluster setter
        nlbl=tk.Label(self,text="# of Clusters, k=")
        nlbl.grid(column=0, row=1, sticky=(E,N))

        self.k = tk.StringVar(self)
        self.k.set(str(3))
        self.k_spin = tk.Spinbox(self, from_=1, to=self.cluster_limit, textvariable=self.k ,width=4)
        self.k_spin.grid(column=1, row=1, sticky=(W, N))

        # draw aggregation setter
        klbl=tk.Label(self,text="aggregated Minutes, n=")
        klbl.grid(column=0, row=2, sticky=(E, N))

        self.n = tk.StringVar(self)
        self.n.set(str(360))
        self.n_spin = tk.Spinbox(self, from_=1, to=self.cluster_limit, textvariable=self.n ,width=4)
        self.n_spin.grid(column=1, row=2, sticky=(W, N))



        self.refrbutton = tk.Button(self)
        self.refrbutton["text"] = "refresh"
        self.refrbutton["command"] = self.handle_refresh_btn
        self.refrbutton.grid(column=0, row=3, sticky=(W, N,E), columnspan=2)




    def handle_refresh_btn(self):
        #TODO
        return

    def apply_select(self, clause):
        pass

    def ds_changed(self):
        self.ds=self.window.ds
        self.select.destroy()
        self.select=Selector(self, self.ds, self.apply_select)
        self.select.grid(column=0, row=0, sticky=(E, W,N), columnspan=2)



