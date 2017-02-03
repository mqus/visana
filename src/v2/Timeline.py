import tkinter as tk
import numpy as np

# needs base, show, selected
from datasource import DataSource
#from v2.Window import VisAnaWindow


class Timeline(tk.Frame):

    def __init__(self, master):
        super(Timeline, self).__init__( master)

        self.window=master #type:VisAnaWindow

        self.mininterval=360

        self.aggregation_amount=self.mininterval
        self.selected_dates = np.ndarray([])
        self.shown_dates = np.ndarray([])

        #draw timeline



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