import tkinter as tk
from tkinter import Scale, HORIZONTAL, X
import datasource
## matplotlibs
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import date, datetime
import pandas as pd
from random import random
from dateutil import rrule
import matplotlib.pyplot as plt




class VisAnaGUI(tk.LabelFrame):
    def __init__(self, master=None, ds=None):
        tk.LabelFrame.__init__(self, master, bg="#ff6600")
        #self.pack()
        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3,weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.plot_tooltip=None
        self.createWidgets()
        root.title("Visual Analyser - Gui")


    def createWidgets(self):
        self.toolbar=tk.LabelFrame(self)
        self.toolbar.grid(column=0, row=0, sticky=(tk.W, tk.N, tk.E), columnspan=5)

        self.QUIT = tk.Button(self.toolbar, text="QUIT", fg="red",
                              command=root.destroy)
        self.QUIT.grid(column=0, row=0, sticky=(tk.W, tk.N))

        self.hi_there = tk.Button(self.toolbar)
        self.hi_there["text"] = "Hello World\\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.grid(column=1, row=0, sticky=(tk.W, tk.N))

        self.filter = tk.LabelFrame(self, bg="#0066ff")
        self.filter.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)
        self.f1 = tk.Label(self.filter, text="HIER STEHT Dann EIN FILTER!!!")
        #self.f1.pack()


        self.timeline = tk.Label(self, text="HIER STEHT NE TIMELINE!!!", bg="#0066ff")
        self.timeline.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)

        self.projector = tk.Label(self, text="HIER KANN MAN\n EIGENSCHAFTEN\n AUSWAEHLEN\n\n\nbis hier")
        self.projector.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.history = tk.Text(self, width=50)
        self.history.grid(column=2, row=3, sticky=(tk.N, tk.E, tk.S))
        for i in range(1,101):
            self.add_to_history('Line %d of 100' % i)
        self.history["state"]="disabled"
        #self.history.insert('end', "Das hier ist mal passiert!!!!\n")
        
        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=3, row=3, sticky=(tk.N, tk.S))
        self.history['yscrollcommand'] = self.historyslider.set

        #for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
    def say_hi(self):
        print("hi there, everyone!")

    def add_to_history(self, text):
        self.history.insert('end', text + "\n")

    ## triggered by changing startslider value
    def updateStart(self, event):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        if endVal < fromVal:
            self.endSlider.set(self.startSlider.get())
        self.f1label["text"] = "FROM "+str(self.dates[endVal])

    ## triggered by changing startslider value
    def updateEnd(self, event):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        if endVal < fromVal:
            self.startSlider.set(self.endSlider.get())
        self.f2label["text"] = "TO "+str(self.dates[endVal])

    ## add sliders to GUI
    def add_sliders(self):
        self.dates = []
        for dt in rrule.rrule(rrule.DAILY,
            dtstart=datetime(2014,1,1,0,0,0),
            until=datetime(2014,12,31,23,59,0)):
            self.dates.append(dt.date())

        self.startSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.updateStart)
        self.endSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.updateEnd)
        self.f1 = self.startSlider
        self.f1.pack(fill=X)
        self.f1label = tk.Label(self.filter, text="FROM VALUE")
        self.f1label.pack()
        self.f2 = self.endSlider
        self.f2.pack(fill=X)
        self.f2label = tk.Label(self.filter, text="TO VALUE")
        self.f2label.pack()


    ## update view with specified data
    def display_data(self, df, attr_name1="Large", attr_name2="Small"):
        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        #df.plot.scatter(x=attr_name1, y=attr_name2, ax=ax, grid=True, picker=True)
        ax.plot(df[attr_name1], df[attr_name2], marker="o", linewidth=0, picker=True)#, grid=True)
        ax.grid(True)
        #df.plot(x="MasterTime", y="Large", ax=ax)

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.mpl_connect('button_press_event', lambda event: self.canvas._tkcanvas.focus_set())
        self.canvas.mpl_connect('pick_event', self.draw_tooltip)
        #self.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))

    def draw_tooltip(self, event):
        if self.plot_tooltip is not None:
            self.canvas.get_tk_widget().delete(self.plot_tooltip)
            self.canvas.get_tk_widget().delete(self.plot_tooltip_rect)
        print("dasEvent: "+ str(vars(event)))
        print("ind: "+ str(event.ind))
        #print("artist: "+ str(vars(event.artist)))
        print("me: "+ str(vars(event.mouseevent)))
        y=self.canvas.figure.bbox.height-event.mouseevent.y
        x=event.mouseevent.x
        text="time:\nsmall\nbig\ntemp\nhumidity"
        self.plot_tooltip=self.canvas.get_tk_widget().create_text(x+2, y, anchor=tk.NW,
                                                                  text=text)
        self.plot_tooltip_rect = self.canvas.get_tk_widget().create_rectangle(
            self.canvas.get_tk_widget().bbox(self.plot_tooltip), fill="yellow")
        self.canvas.get_tk_widget().delete(self.plot_tooltip)
        self.plot_tooltip=self.canvas.get_tk_widget().create_text(x+2, y, anchor=tk.NW,
                                                                  text=text)

        #mouseev = event.mouseevent
        #xdata = mouseev.x_data
        #ydata = mouseev.y_data
        ##ind = event.ind
        #points = tuple(zip(xdata[ind], ydata[ind]))
        #print('onpick point:', points)

    def draw_timeline(self, date_contained, shown_dates={}, selected_dates=[]):
        ## create value for each day in data,
        ## depending on whether it is selected, shown etc.
        days = []
        values = []
        for day in sorted(date_contained.keys()):
            if date_contained[day]:
                days.append(day)
                ##if random() < 0.01:
                if shown_dates[day]:
                    values.append("blue")
                    ##if day in selected_dates:
                    if random() < 0.05:
                        values.append("red")
                else:
                    values.append("lightskyblue")


        #print(days)
        #print(values)
        #print(len(values))

        fig = Figure(figsize=(6,1), dpi=100)
        ax = fig.add_subplot(111)

        ax.scatter(days, [1]*len(days), c=values,
                   marker='|', s=200, fontsize=10)
        fig.autofmt_xdate()

        ax.set_xlim([datetime(2014,1,1,0,0,0), datetime(2014,12,31,0,0,0)])

        ## everything after this is turning off stuff that's plotted by default
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_ticklabels([])

        self.timeline = FigureCanvasTkAgg(fig, self)
        self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)




## select data from datasource in this time range
def filter_data(ds, start_time, end_time):
    ds.select(out_table="time_filter", attr_name="MasterTime",
        a=start_time, b=end_time)
    return ds.get_data("time_filter").df()

## build a dictionary with 365 days as keys
## and boolean values for those days that
## contain non-missing values
def build_contained_dict(df):
    #print(df)
    date_contained = dict()
    for dt in rrule.rrule(rrule.DAILY,
        dtstart=datetime(2014,1,1,0,0,0),
        until=datetime(2014,12,31,23,59,0)):
        date_contained[dt.date()] = False
    ## only check for values in 'Small' and 'Large'
    df = df[["MasterTime", "Small", "Large"]]
    ## iterate through tuples and check for each day
    ## if there are non-missing values
    #print(df)
    for row in df.itertuples():
        if not pd.isnull(row.Small) or not pd.isnull(row.Large):
            day = row.MasterTime.date()
            date_contained[day] = True

    return date_contained



## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
print("read")
root = tk.Tk()

app = VisAnaGUI(master=root)
## display base data at startup
df = ds.get_base_data().df()
## which days are in the data?
date_contained = build_contained_dict(df)
## example: select only dates in december
df = filter_data(ds, start_time=datetime(2014,12,1,0,0,0), end_time=datetime(2014,12,31,23,59,0))
## which days are shown in december?
date_shown = build_contained_dict(df)

## draw data
app.display_data(df)
## draw timeline
app.draw_timeline(date_contained, date_shown)



app.mainloop()
