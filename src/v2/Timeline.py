import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.figure import Figure

from datasource import DataSource, COLORS

import matplotlib.dates as mdates
# from Window import VisAnaWindow


# needs base, show, selected
class Timeline(ttk.Frame):

    def __init__(self, master):
        super(Timeline, self).__init__(master, height=100)
        self.window=master #type:VisAnaWindow
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        #self.mininterval=360

        #self.aggregation_amount=self.mininterval
        self.selected_dates = np.ndarray([])
        self.shown_dates = np.ndarray([])
        self.timeline = None

        #df["_color"] = np.asarray(COLORS)[df["_label"]]
        #print("color")


        #draw timeline
    def create_timeline(self):

        base_dates = self.window.ds.df("base").index.values

        start_date = base_dates[0]
        end_date = base_dates[-1]
        ## plot timeline

        self.fig = Figure(figsize=(12,1),dpi=75)
        ax = self.fig.add_subplot(111)

        #draw all shown dates
        c = self.window.ds.get_data("cluster").centroids
        d = self.window.ds.df("cluster")
        if c is not None:
            # we show clustered dates
            # for i in range(len(c)):
            #     d2=d.loc[d["_label"] == i]
            #     dates=d2.index.values
            #     ax.scatter(dates, [1]*len(dates), c=COLORS[i],
            #                marker='|', s=300)#, fontsize=10)
            #change COLORS to a numpy-array and then map each label to its color
            colors = np.asarray(COLORS)[d["_cluster"]]
            dates = d.index.values
            ax.scatter(dates, [1]*len(dates), c=colors,
                            marker='|', s=300)#, fontsize=10)
        else:
            for p in self.window.ds.get_significant_nan_columns():
                d = d.loc[d[p].notnull()]

            # we show normal dates
            dates = d.index.values
            ax.scatter(dates, [1] * len(dates), c="blue",
                       marker='|', s=300)  # , fontsize=10)

        #draw all selected data if neccessary
        if self.window.scatter.has_selection():
            selected_dates = self.window.ds.df("ss_selected").index.values
            ax.scatter(selected_dates, [1] * len(selected_dates), c="black",
                       marker='|', s=300)  # , fontsize=10)

        hfmt = mdates.DateFormatter("1. %b '%y")
        # fig.subplots_adjust(left=0.03, right=0.97, top=1)

        ax.xaxis.set_major_formatter(hfmt)
        self.fig.autofmt_xdate()
        #ax.set_xticklabels(ax.xaxis.get_minorticklabels(), rotation=0)

        #ax.set_xlim([datetime(2014,1,1,0,0,0), datetime(2015,1,1,0,0,0)])
        ax.set_xlim([start_date, end_date])


        ## everything after this is turning off stuff that's plotted by default
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_ticklabels([])
        self.fig.tight_layout(pad=0)

        #print(fig.get_figheight())
        #fig.subplots_adjust(top=1, right=0.99)

        ## add to GUI
        if self.timeline is not None:
            self.timeline.get_tk_widget().destroy()
        self.timeline = FigureCanvasTkAgg(self.fig, self)#, resize_callback=print)

        self.timeline.get_tk_widget().grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W, tk.S))

    # def draw_timeline(self):
    #     ## create value for each day in data,
    #     ## depending on whether it is selected, shown etc.
    #
    #     shown_dates=self.ds.df("shown_dates").index.values
    #
    #     base_dates=self.df("all_days").index.values
    #
    #     ## extract first and last date
    #     #start_date = base_dates[0]
    #     #end_date = base_dates[-1]
    #     #days_diff = ((end_date-start_date) / np.timedelta64(1, 'D'))
    #
    #     ## prepare data for timeline
    #     days = []
    #     values = []
    #
    #     self.ds.filterforvalues("intervals_with_values",[self.param1,self.param2], "AND","base")
    #     self.ds.filterforvalues("intervals_with_values","intervals_with_values")
    #
    #     #self.df("all_days").
    #     for date in self.df("all_days").index.values:
    #         self.df("all_days")
    #         col1_has_values=((self.param1 == self.ds.get_time_colname()) or (self.df("all_days")[self.param1][date]>0))
    #         col2_has_values=((self.param2 == self.ds.get_time_colname()) or (self.df("all_days")[self.param2][date]>0))
    #         if col1_has_values and col2_has_values:
    #             days.append(date)
    #             #if self.dates[self.startSlider.get()] <= day < self.dates[self.endSlider.get()]:
    #             if date in shown_dates:
    #                 if date in selected_dates:
    #                     values.append("red")
    #                 else:
    #                     values.append("blue")
    #             else:
    #                 values.append("lightskyblue")
    #     #print("d:",days, values)
    #
    #     ## plot timeline
    #     fig = Figure(figsize=(12,1), dpi=75)
    #     ax = fig.add_subplot(111)
    #
    #     ax.scatter(days, [1]*len(days), c=values,
    #                marker='|', s=300)#, fontsize=10)
    #     #fig.xt
    #     hfmt = mdates.DateFormatter("1. %b '%y")
    #     # fig.subplots_adjust(left=0.03, right=0.97, top=1)
    #
    #     ax.xaxis.set_major_formatter(hfmt)
    #     fig.autofmt_xdate()
    #     #ax.set_xticklabels(ax.xaxis.get_minorticklabels(), rotation=0)
    #
    #     #ax.set_xlim([datetime(2014,1,1,0,0,0), datetime(2015,1,1,0,0,0)])
    #     ax.set_xlim([start_date, end_date])
    #
    #
    #     ## everything after this is turning off stuff that's plotted by default
    #     ax.yaxis.set_visible(False)
    #     ax.spines['right'].set_visible(False)
    #     ax.spines['left'].set_visible(False)
    #     ax.spines['top'].set_visible(False)
    #     ax.xaxis.set_ticks_position('bottom')
    #     ax.get_yaxis().set_ticklabels([])
    #     fig.tight_layout(pad=0)
    #
    #     #print(fig.get_figheight())
    #     #fig.subplots_adjust(top=1, right=0.99)
    #
    #     ## add to GUI
    #     self.timeline = FigureCanvasTkAgg(fig, self)
    #     self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W, tk.S),columnspan=5)
    #     #print("h:",self.timeline.figure.bbox.height)

    def setAggregation(self,minutes):
        if self.mininterval <= minutes:
            self.aggregation_amount = minutes
        else:
            self.aggregation_amount=self.mininterval
        self.ds.aggregateTime("all_intervals", "COUNT", self.aggregation_amount, "base")

    def selectionChanged(self, isNowSelected=False):
        self.selected_dates=np.ndarray([])

        if isNowSelected:
            #self.ds.groupby2("selected_days", datasource.TIME_ATTR, "COUNT", "selected", bydate=True)
            #self.ds.aggregateTime("selected_days", "COUNT",24*60, "selected")
            #self.ds.aggregateTime("selected_intervals", "COUNT",1, "selected")
            self.selected_dates = self.ds.df("selected_intervals").index.values
        self.draw_timeline()

    def shownDatesChanged(self):
        self.shown_dates=self.ds.df("shown_dates").index.values