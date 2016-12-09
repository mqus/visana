import tkinter as tk
from tkinter import Scale, HORIZONTAL, X, Listbox, Spinbox, StringVar
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
        #tk.LabelFrame.__init__(self, master, bg="#ff6600")
        tk.LabelFrame.__init__(self, master, bg="red")
        #self.pack()
        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3,weight=1)
        #self.rowconfigure(2,weight=2)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.plot_tooltip=None
        self.configure(background="red")

        ## save data source
        self.ds = ds
        self.df=None

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

        ## parameter variables for listboxes
        self.param_list = ["Small", "Large", "OutdoorTemp", "RelHumidity"]
        self.param1 = "Small"
        self.param2 = "Large"

        ## simple string to describe last action (for history)
        self.action_str = "Show base data"

        ## dictionary describing which days are contained in base data
        ## (for timeline)
        self.dates_contained = self.build_contained_dict(self.ds.get_base_data().df())

        self.create_widgets()
        root.title("Visual Analyser - Gui")

        ## draw data at startup
        self.trigger_update()

    ## is called regularly, after the given delay
    def check_for_update(self):
        ## if there is an unprocessed action older than
        ## the given delay, update data
        self.check_listbox_changes()
        if self.unprocessed_action and \
            (time() - self.last_action) > self.UPDATE_DELAY/1000:
            print("redraw data")
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

    ## check if listbox params have changed
    def check_listbox_changes(self):
        cur_param1 = self.param_list[self.param1box.curselection()[0]]
        cur_param2 = self.param_list[self.param2box.curselection()[0]]
        if not (cur_param1 == self.param1 and cur_param2 == self.param2):
            ## values have changed!
            print("listboxes have changed!")
            self.param1 = cur_param1
            self.param2 = cur_param2
            self.unprocessed_action = True
            self.action_str = "New parameters: "+self.param1+" & "+self.param2

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

        #self.filter = tk.LabelFrame(self, bg="#0066ff")
        self.filter = tk.LabelFrame(self, bg="red")
        self.filter.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)
        self.f1 = tk.Label(self.filter, text="HIER STEHT Dann EIN FILTER!!!")
        self.filter.columnconfigure(1, weight=0)
        self.filter.columnconfigure(0, weight=5)

#        self.timeline = tk.Label(self, text="HIER STEHT NE TIMELINE!!!", bg="#0066ff")
#        self.timeline.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)


        #self.projector = tk.LabelFrame(self, bg="#0066ff")
        self.projector = tk.LabelFrame(self, bg="red")
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

    def aggregate_values(self):
        limit_val = int(self.noise_spin.get())

        self.ds.store_df(df=self.df, name="tmp")
        self.ds.aggregate(out_table="aggregate", mode="AVG", attr_names=["MasterTime", self.param1, self.param2], limit=limit_val, in_table="tmp")
        base_df = self.df
        self.df = self.ds.get_data(name="aggregate").df()

        self.display_data()
        self.draw_timeline(df=base_df)
        self.action_str = "Aggregated values: "+str(limit_val)

        self.add_to_history(self.action_str)

    def add_listboxes(self):
        ## listboxes for parameter selection
        self.param1box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param1box.insert("end", item)
        param1_index = self.param_list.index(self.param1)
        self.param1box.select_set(param1_index)
        self.param1box.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W))

        self.param2box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param2box.insert("end", item)
        param2_index = self.param_list.index(self.param2)
        self.param2box.select_set(param2_index)
        self.param2box.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W))

        var = StringVar(self.projector)
        var.set("10")
        self.noise_spin = Spinbox(self.projector, from_=0, to=1440, textvariable=var)
        self.noise_spin.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.testbutton = tk.Button(self.projector)
        self.testbutton["text"] = "Aggregate values (minutes)"
        self.testbutton["command"] = self.aggregate_values
        self.testbutton.grid(column=0, row=4, sticky=(tk.W, tk.N))

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

        self.add_to_history(self.action_str)

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
        self.action_str = "New time interval: "+str(self.dates[fromVal])+" - "+str(self.dates[endVal])

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
    def display_data(self):
        print(self.df.describe())
        print("data size = "+str(len(self.df)))
        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        #df.plot.scatter(x=attr_name1, y=attr_name2, ax=ax, grid=True, picker=True)
        print("param1="+str(self.param1)+" param2="+str(self.param2))

        ax.plot(self.df[self.param1], self.df[self.param2], marker="o", linewidth=0, picker=True)#, grid=True)
        ax.grid(True)
        ax.set_xlabel(self.param1)
        ax.set_ylabel(self.param2)
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
        ## create a dict for each parameter which encodes the
        ## information for each day if there is at least one
        ## valid measurement
        date_contained =  {}
        df_params = df.columns.values
        for param in self.param_list:
            date_contained[param] = {}
        for dt in rrule.rrule(rrule.DAILY,
            dtstart=datetime(2014,1,1,0,0,0),
            until=datetime(2014,12,31,23,59,0)):
            for param in self.param_list:
                date_contained[param][dt.date()] = False
        ## only check for values in 'Small' and 'Large'
        #df = df[["MasterTime", "Small", "Large"]]
        ## iterate through tuples and check for each day
        ## if there are non-missing values
        #print(df)
        for row in df.itertuples():
            day = row.MasterTime.date()
            if "Small" in df_params and not pd.isnull(row.Small):
                date_contained["Small"][day] = True
            if "Large" in df_params and not pd.isnull(row.Large):
                date_contained["Large"][day] = True
            if "OutdoorTemp" in df_params and not pd.isnull(row.OutdoorTemp):
                date_contained["OutdoorTemp"][day] = True
            if "RelHumidity" in df_params and not pd.isnull(row.RelHumidity):
                date_contained["RelHumidity"][day] = True

        return date_contained


    def draw_timeline(self, df=None, selected_dates=[]):
        if df is None:
            df = self.df
        ## create value for each day in data,
        ## depending on whether it is selected, shown etc.
        shown_dates = self.build_contained_dict(df)

        ## prepare data for timeline
        days = []
        values = []
        for day in sorted(self.dates):
            if self.dates_contained[self.param1][day] and \
                self.dates_contained[self.param2][day]:
                days.append(day)
                ##if random() < 0.01:
                if shown_dates[self.param1][day] and shown_dates[self.param2][day]:
                    values.append("blue")
                    if day in selected_dates:
                    #if random() < 0.05:
                        values.append("red")
                else:
                    values.append("lightskyblue")


        ## plot timeline
        fig = Figure(figsize=(10,2), dpi=100)
        ax = fig.add_subplot(111)

        ax.scatter(days, [1]*len(days), c=values,
                   marker='|', s=200)#, fontsize=10)
        hfmt = mdates.DateFormatter('%m')
        fig.autofmt_xdate()

        ax.xaxis.set_major_formatter(hfmt)

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
        self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W, tk.S),columnspan=5)




## select data from datasource in this time range
#def filter_data(ds, start_time, end_time):
#    ds.select(out_table="time_filter", attr_name="MasterTime",
#        a=start_time, b=end_time)
#    return ds.get_data("time_filter").df()



## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
print("read")
print(ds.get_base_data().df())
root = tk.Tk()

app = VisAnaGUI(master=root, ds=ds)

app.mainloop()
