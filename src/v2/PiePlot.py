from tkinter import Frame, Label, StringVar, N, E, W, S, Spinbox
from tkinter.ttk import Combobox, LabelFrame, Checkbutton, Button

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LinearRegression

import util
from datasource import DataSource, COLORS


# from v2.Window import VisAnaWindow



class Pie(Frame):
    def __init__(self, parent, master):
        super(Pie, self).__init__(parent)
        self.window = master  # type:VisAnaWindow
        self.parent = parent


        self.ds = self.window.ds  # type:DataSource

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.mainwidget=Label(self,text="No data, please open a file via File -> Open")
        self.mainwidget.grid(column=0, row=0, sticky=(S, W, N, E))

        if self.ds is not None:
            self.draw_plot()

        # self.settings = PControls(self, self.ds.base().get_attr_names())
        # self.settings.grid(column=0, row=0, sticky=(S, W, N, E))
        # self.apply_settings()

    #### Handle Signals from Outside

    # the underlying data changed, called by VisAnaWindow.openFile
    def ds_changed(self):
        self.ds = self.window.ds

    # a cluster recalculation was processed, called by VisAnaWindow.redo_plots
    def cluster_changed(self, in_table):

        self.ds.link("pc_show", in_table)

        self.redraw_plot()

    def redraw_plot(self):
        self.window.status.set("Redraw PieChart...")
        self.draw_plot()
        self.window.status.set("")

    def draw_plot(self):
        self.mainwidget.destroy()

        tabl = self.ds.get_data("pc_show")
        d = tabl.df()                       #type:DataFrame
        if tabl.centroids is not None:
            fig = Figure(figsize=(5, 5), dpi=100)  # type:Figure
            ax = fig.add_subplot(111)

            ax.clear()
            ax.grid(True)
            k = len(tabl.centroids)
            g = d.groupby(["_cluster"]).count()["Daytime"]

            lbls = ["Cluster "+str(i) for i in range(k)]
            ax.pie(g,colors=COLORS,labels=lbls,autopct="%2.2f %%",pctdistance=0.8)
            ax.axis("equal")
            fig.suptitle("Cluster-Occurence in Data")


            self.canvas = FigureCanvasTkAgg(fig, self)  # type:FigureCanvasTkAgg

            self.mainwidget=self.canvas.get_tk_widget()
        else:
            self.mainwidget = Label(self, text="No cluster calculated; therefore,\n no data can be shown here.")
        self.mainwidget.grid(column=0, row=0, sticky=(S, W, N, E))



