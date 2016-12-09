import tkinter as tk
from tkinter import Scale, HORIZONTAL, X, Listbox
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
from time import time




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

        ## save data source
        self.ds = ds
        self.df=None
        ## dictionary describing which days are contained in base data
        ## (for timeline)
        self.dates_contained = self.build_contained_dict(self.ds.get_base_data().df())

        ## save time of last update to prevent too many
        ## updates when using sliders
        self.last_action = time()
        ## delay after last data update and action (in ms)
        self.UPDATE_DELAY = 500
        ## was there an action triggering an update?
        self.unprocessed_action = False
        ## calls check_for_update() method after delay has passed
        self.after(self.UPDATE_DELAY, self.check_for_update)
        ## dummy variable to ignore first update. sliders trigger an 
        ## event at startup, which would lead to redundant update of data
        self.ignore_start_trigger = True

        ## parameter variables
        self.param_list = ["Small", "Large", "Humidity", "Temperature"]
        self.param1 = 0
        self.param2 = 1


        self.create_widgets()
        root.title("Visual Analyser - Gui")
        ## draw data at startup
        self.trigger_update()

    ## is called regularly, after the given delay
    def check_for_update(self):
        ## if there is an unprocessed action older than
        ## the given delay, update data
        #self.check_listbox_changes()
        if self.unprocessed_action and \
            (time() - self.last_action) > self.UPDATE_DELAY/1000:
            ## simply block the very first update...
            ## (there might be prettier solutions)
            if self.ignore_start_trigger:
                self.ignore_start_trigger = False
            else:
                ## update data
                self.trigger_update()
            self.unprocessed_action = False
        #print("checking for updates...")
        self.after(self.UPDATE_DELAY, self.check_for_update)

    #

    ## creates all GUI elements
    def create_widgets(self):
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
        self.filter.columnconfigure(1, weight=0)
        self.filter.columnconfigure(0, weight=5)

#        self.timeline = tk.Label(self, text="HIER STEHT NE TIMELINE!!!", bg="#0066ff")
#        self.timeline.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)


        self.projector = tk.LabelFrame(self, bg="#0066ff")
        self.projector.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.paramlabel = tk.Label(self.projector, text="Choose Parameters")
        self.paramlabel.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W))

        self.add_listboxes()

        self.history = tk.Text(self, width=50)
        self.history.grid(column=2, row=3, sticky=(tk.N, tk.E, tk.S))
        #for i in range(1,101):
        #    self.add_to_history('Line %d of 100' % i)
        #self.history["state"]="disabled"
        #self.history.insert('end', "Das hier ist mal passiert!!!!\n")
        
        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=3, row=3, sticky=(tk.N, tk.S))
        self.history['yscrollcommand'] = self.historyslider.set

        #for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.add_sliders()

    ## dummy method
    def say_hi(self):
        print("hi there, everyone!")

    def add_listboxes(self):
        ## listboxes for parameter selection
        self.param1box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param1box.insert("end", item)
        self.param1box.select_set(self.param1)
        self.param1box.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W))

        self.param2box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param2box.insert("end", item)
        self.param2box.select_set(self.param2)
        self.param2box.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W))


    ## add line to history window
    def add_to_history(self, text):
        self.history.insert('end', "\n" + text )#+ "\n")
        self.history.see("end")

    ## draw new data according to current positions of date sliders
    def trigger_update(self):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        self.ds.select(out_table="time_filter", attr_name="MasterTime",
            a=self.dates[fromVal], b=self.dates[endVal])
        self.df = self.ds.get_data("time_filter").df()


        self.display_data()
        self.draw_timeline()

        self.add_to_history("data update "+str(self.dates[fromVal])+" - "+str(self.dates[endVal]))

    #########
    ## SLIDER METHODS
    ## we need separate update functions for the sliders, 
    ## as we could otherwise not distinguish between changing
    ## the first or second slider
    #########

    ## triggered by changing startslider value
    def update_start(self, event):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        if endVal < fromVal:
            self.endSlider.set(fromVal)

        self.handle_slider_update()

    ## triggered by changing startslider value
    def update_end(self, event):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        if endVal < fromVal:
            self.startSlider.set(endVal)

        self.handle_slider_update()

    ## handle data update event, i.e. a slider changed.
    def handle_slider_update(self):
        fromVal = self.startSlider.get()
        endVal = self.endSlider.get()
        self.startlabel["text"] = "FROM "+str(self.dates[fromVal])
        self.endlabel["text"] = "TO "+str(self.dates[endVal])
        self.unprocessed_action = True
        self.last_action = time()

    ## add sliders to GUI
    def add_sliders(self):
        self.dates = []
        for dt in rrule.rrule(rrule.DAILY,
            dtstart=datetime(2014,1,1,0,0,0),
            until=datetime(2014,12,31,23,59,0)):
            self.dates.append(dt.date())

        ## init sliders
        self.startSlider = Scale(self.filter, from_=0, to=364, orient=HORIZONTAL, command=self.update_start)
        self.startSlider.set(0)
        self.endSlider = Scale(self.filter, from_=0, to=364, orient=HORIZONTAL, command=self.update_end)
        self.endSlider.set(364)

        ## add sliders and labels to GUI
        self.startSlider.grid(column=0, row=0, sticky=(tk.W, tk.N, tk.E))
        self.startlabel = tk.Label(self.filter, text="FROM VALUE")
        self.startlabel.grid(column=1, row=0, sticky=(tk.W))
        self.endSlider.grid(column=0, row=1, sticky=(tk.W, tk.S, tk.E))
        self.endlabel = tk.Label(self.filter, text="TO VALUE")
        self.endlabel.grid(column=1, row=1, sticky=(tk.W))

    def graph_changed(self):
        pass

    ## update view with specified data
    def display_data(self, attr_name1="Large", attr_name2="Small"):
        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        #df.plot.scatter(x=attr_name1, y=attr_name2, ax=ax, grid=True, picker=True)
        ax.plot(self.df[attr_name1], self.df[attr_name2], marker="o", linewidth=1, picker=self.line_picker)#, grid=True)
        ax.grid(True)
        #df.plot(x="MasterTime", y="Large", ax=ax)

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.mpl_connect('button_press_event', lambda event: self.canvas._tkcanvas.focus_set())
        self.canvas.mpl_connect('pick_event', self.draw_tooltip)
        #self.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas_tb=NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))

    def line_picker(self, line, mouseevent):
        """
        find the points within a certain distance from the mouseclick in
        data coords and attach some extra attributes, pickx and picky
        which are the data points that were picked
        """
        print("PICKER")
        print(vars(line))
        print(vars(mouseevent))

        if mouseevent.xdata is None:
            return False, dict()
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        maxd = 0.05
        d = pd.np.sqrt((xdata - mouseevent.xdata)**2. + (ydata - mouseevent.ydata)**2.)

        ind = pd.np.nonzero(pd.np.less_equal(d, maxd))
        if len(ind):
            pickx = pd.np.take(xdata, ind)
            picky = pd.np.take(ydata, ind)
            props = dict(ind=ind, pickx=pickx, picky=picky)
            return True, props
        else:
            return False, dict()

    def draw_tooltip(self, event):
        if self.plot_tooltip is not None:
            self.canvas.get_tk_widget().delete(self.plot_tooltip)
            self.canvas.get_tk_widget().delete(self.plot_tooltip_rect)
        print("dasEvent: "+ str(vars(event)))
        print("ind: "+ str(event.ind))
        print("artist: "+ str(vars(event.artist)))
        #print("me: "+ str(vars(event.mouseevent)))
        print(("hi, %d , " % len(event.ind)))

        if len(event.ind) is 1:

            text="Selected Value:"
            for col,cdata in self.df.iteritems():
                text = text + "\n" + str(col) + ": \t" + str(cdata[event.ind[0]])
            print(text)
        else:
            text = "time:\nsmall\nbig\ntemp\nhumidity"
        y=self.canvas.figure.bbox.height-event.mouseevent.y
        x=event.mouseevent.x

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

    ## build a dictionary with 365 days as keys
    ## and boolean values for those days that
    ## contain non-missing values
    def build_contained_dict(self, df):
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


    def draw_timeline(self, selected_dates=[]):
        ## create value for each day in data,
        ## depending on whether it is selected, shown etc.
        shown_dates = self.build_contained_dict(self.df)

        ## prepare data for timeline
        days = []
        values = []
        for day in sorted(self.dates_contained.keys()):
            if self.dates_contained[day]:
                days.append(day)
                ##if random() < 0.01:
                if shown_dates[day]:
                    values.append("blue")
                    if day in selected_dates:
                    #if random() < 0.05:
                        values.append("red")
                else:
                    values.append("lightskyblue")


        ## plot timeline
        fig = Figure(figsize=(6,1), dpi=100)
        ax = fig.add_subplot(111)

        ax.scatter(days, [1]*len(days), c=values,
                   marker='|', s=200)#, fontsize=10)
        fig.autofmt_xdate()

        ax.set_xlim([datetime(2014,1,1,0,0,0), datetime(2014,12,31,0,0,0)])

        ## everything after this is turning off stuff that's plotted by default
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_ticklabels([])

        ## add to GUI
        self.timeline = FigureCanvasTkAgg(fig, self)
        self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)




## select data from datasource in this time range
#def filter_data(ds, start_time, end_time):
#    ds.select(out_table="time_filter", attr_name="MasterTime",
#        a=start_time, b=end_time)
#    return ds.get_data("time_filter").df()



## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
print("read")
root = tk.Tk()

app = VisAnaGUI(master=root, ds=ds)

app.mainloop()
