import tkinter as tk
from tkinter import Scale, HORIZONTAL, Listbox, Spinbox, StringVar
import matplotlib

import datasource

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
from dateutil import rrule
from time import time
import util




class VisAnaGUI(tk.LabelFrame):
    def __init__(self, master=None, ds=None):

        self.dates = []
        for dt in rrule.rrule(rrule.DAILY,
            dtstart=datetime(2014,1,1,0,0,0),
            until=datetime(2015,1,1,0,0,0)):
            self.dates.append(dt.date())


        ## save data source
        self.ds = ds #type:datasource.DataSource
        self.ds.groupby("all_days", "MasterTime", "COUNT","base", bydate=True)
        #self.ds.link("show")
        #self.df=ds.get_base_data().df()

        ## parameter variables for listboxes
        self.param_list = ["Small", "Large", "OutdoorTemp","RelHumidity"]
        self.param2 = "Small"
        self.param1 = "Large"
        self.aggregation_limit=1

        ## simple string to describe last action (for history)
        self.action_str = "Show base data"

        self.plot_tooltip=None
        self.select_rect=None

        self.draw_frame(master)

        self.mouse_pressed=None

        ## save time of last update to prevent too many
        ## updates when using sliders
        self.last_action = time()
        ## delay after last data update and action (in ms)
        self.UPDATE_DELAY = 500
        ## was there an action triggering an update?
        # (0=no, 1=only the timeline, 2=axes and timeline, 3=with selection, 4 with tidyup)
        self.unprocessed_action = 4
        ## calls check_for_update() method after delay has passed
        self.after(self.UPDATE_DELAY, self.check_for_update)
        ## dummy variable to ignore first update. sliders trigger an
        ## event at startup, which would lead to redundant update of data
        self.ignore_start_trigger = True

        ## draw data at startup
        self.update_plot()

    #######################
    # UI CREATION

    def draw_frame(self, master):
        tk.LabelFrame.__init__(self, master, bg="red")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.title("Visual Analyser - Gui")

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(2,minsize=100)
        self.configure(background="red")

        self.create_widgets()

    ## creates all GUI elements
    def create_widgets(self):
        self.toolbar=tk.LabelFrame(self)
        self.toolbar.grid(column=0, row=0, sticky=(tk.W, tk.N, tk.E), columnspan=5)


        self.QUIT = tk.Button(self.toolbar, text="QUIT", fg="red", command=root.destroy)
        self.QUIT.grid(column=0, row=0, sticky=(tk.W, tk.N))

        self.reset_view_btn = tk.Button(self.toolbar)
        self.reset_view_btn["text"] = "Reset the View"
        self.reset_view_btn["command"] = self.reset_to_start
        self.reset_view_btn.grid(column=1, row=0, sticky=(tk.W, tk.N))

        self.tdvar = tk.StringVar(value="0")
        self.tidy_up = tk.Checkbutton(self.toolbar, text='Tidy Up Data', command=self.handle_tidy_up,
                                      variable=self.tdvar)
        self.tidy_up.grid(column=2, row=0, sticky=(tk.W, tk.N))

        self.projector = tk.LabelFrame(self, bg="red")
        self.projector.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.paramlabel = tk.Label(self.projector, text="Choose Parameters")
        self.paramlabel.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W))

        self.create_listboxes()

        self.history = tk.Text(self, width=45)
        self.history.grid(column=2, row=3, sticky=(tk.N, tk.E, tk.S), rowspan=2)
        self.history.insert('end', "\n")

        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=3, row=3, sticky=(tk.N, tk.S), rowspan=2)
        self.history['yscrollcommand'] = self.historyslider.set

        self.create_plot()

        self.create_sliders()

    def create_listboxes(self):
        ## listboxes for parameter selection
        self.param1box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param1box.insert("end", item)
        param1_index = self.param_list.index(self.param1)
        self.param1box.select_set(param1_index)
        self.param1box.bind('<<ListboxSelect>>', self.handle_paramsChanged)
        self.param1box.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W))

        self.param2box = Listbox(self.projector, exportselection=0)
        for item in self.param_list:
            self.param2box.insert("end", item)
        param2_index = self.param_list.index(self.param2)
        self.param2box.select_set(param2_index)
        self.param2box.bind('<<ListboxSelect>>', self.handle_paramsChanged)
        self.param2box.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W))

        self.var = StringVar(self.projector)
        self.var.set(str(self.aggregation_limit))
        self.noise_spin = Spinbox(self.projector, from_=1, to=1440, textvariable=self.var)
        self.noise_spin.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.testbutton = tk.Button(self.projector)
        self.testbutton["text"] = "Aggregate values (minutes)"
        self.testbutton["command"] = self.handle_aggregate_btn
        self.testbutton.grid(column=0, row=4, sticky=(tk.W, tk.N))

    ## add sliders to GUI
    def create_sliders(self):
        ## init sliders

        #self.filter = tk.LabelFrame(self, bg="#0066ff")
        self.filter = tk.LabelFrame(self, bg="red")
        self.filter.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)
        self.filter.columnconfigure(1, weight=1)
        self.filter.columnconfigure(0, weight=0)

        self.startSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.update_start)
        self.startSlider.set(0)
        self.endSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.update_end)
        self.endSlider.set(365)

        ## add sliders and labels to GUI
        self.startSlider.grid(column=1, row=0, sticky=(tk.W, tk.N, tk.E))
        self.startlabel = tk.Label(self.filter, text="FROM \tVALUE")
        self.startlabel.grid(column=0, row=0, sticky=(tk.W))
        self.endSlider.grid(column=1, row=1, sticky=(tk.W, tk.S, tk.E))
        self.endlabel = tk.Label(self.filter, text="TO \tVALUE")
        self.endlabel.grid(column=0, row=1, sticky=(tk.W))

    #add an empty plot to the GUI
    def create_plot(self):
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, self)

        self.canvas.mpl_connect('motion_notify_event', self.handle_hover)
        self.canvas.mpl_connect('button_press_event', self.handle_mouse_down)
        self.canvas.mpl_connect('button_release_event', self.handle_mouse_up)

        #self.canvas.mpl_connect('pick_event', self.draw_tooltip)

        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))

        # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        #self.ctbwidget=tk.Frame(self)
        #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
        #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)

        util.zoom_factory(self.ax)


    ############################
    # UI HANDLER

    ## dummy method
    def reset_to_start(self):
        self.clean_tooltip(True)
        self.param1box.select_set("Large")
        self.param2box.select_set("Small")
        self.startSlider.set(0)
        self.endSlider.set(365)
        self.var.set(0)


        self.action_str = "Show base data"
        #print("hi there, everyone!")


    def handle_aggregate_btn(self):
        self.aggregation_limit = int(self.noise_spin.get())

        self.action_str = "Aggregated values: "+str(self.aggregation_limit)

        self.unprocessed_action=max(self.unprocessed_action, 3)

    def handle_tidy_up(self):
        if self.tdvar.get() is "0":
            self.action_str="show raw data"
        else:
            self.action_str="tidy up data, remove all points where:" \
                            "\n  OutdoorTemp>40 or Small<0 or Large<0 or " \
                            "\n  RelHumidity<0 or RelHumidity>100"
        self.unprocessed_action=max(self.unprocessed_action, 4)

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
        self.startlabel["text"] = "FROM \t"+str(self.dates[fromVal])
        self.endlabel["text"] = "TO \t"+str(self.dates[endVal])
        self.unprocessed_action = max(self.unprocessed_action, 3)
        self.last_action = time()
        self.action_str = "New time interval: "+str(self.dates[fromVal])+" - "+str(self.dates[endVal])

    ## a different parameter was chosen
    def handle_paramsChanged(self, e):
        print("params Changed!")
        self.param1 = self.param_list[self.param1box.curselection()[0]]
        self.param2 = self.param_list[self.param2box.curselection()[0]]

        self.action_str = "New parameters: " + self.param1 + " & " + self.param2
        self.unprocessed_action= max(self.unprocessed_action, 2)



    ###################
    # PLOT-EVENT HANDLER

#TODO currently unused, but should be used to write zoom and pan events to the history
    def handle_changed_axes(self):
        self.clean_tooltip()
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_xlim()

        text="Focus changed to: x=[{:.1f};{:.1f}] and y=[{:.1f};{:.1f}]".format(xlim[0], xlim[1], ylim[0], ylim[1])
        self.add_to_history(text)
    ## is called by the plot to confirm if the mouseevent was inside/on a plotted line or a marker
    def handle_pick(self, line, mouseevent):

        if mouseevent.button == 1:
            return self.handle_mouse_event(mouseevent)
        else:
            return False,dict()

    ## is called to to do something when the mouse hovers over the plot and has changed its position.
    ## if no mousebutton is pressed and no points were selected, a hover-tooltip is shown.
    ## if the left button is pressed, (re-)draw the selection indicator
    def handle_hover(self, mouseevent):
        if not mouseevent.button in [1,3] and self.select_rect is None:
            isover, props = self.handle_mouse_event(mouseevent)

            if isover:
                self.draw_tooltip(mouseevent, props["ind"])

        elif mouseevent.button in [1,3]:
            xmin = min(mouseevent.xdata, self.mouse_pressed[0])
            xmax = max(mouseevent.xdata, self.mouse_pressed[0])
            ymin = min(mouseevent.ydata, self.mouse_pressed[1])
            ymax = max(mouseevent.ydata, self.mouse_pressed[1])
            bbox=(xmin, ymin, xmax, ymax)
            self.clean_tooltip(True, emit=False)
            bbox2=self.ax.transData.transform(bbox)
            c_height = self.canvas.figure.bbox.height
            bbox3=(bbox2[0], c_height-bbox2[1], bbox2[2],c_height-bbox2[3])
            self.select_rect = self.canvas.get_tk_widget().create_rectangle(bbox3, dash=".")

    ## is called whenever a mousebutton is clicked while the mouse is over the plot.
    ##  if the left button is pushed, we begin to draw a selection area
    def handle_mouse_down(self, mouseevent):
        if mouseevent.button in [1,3]:
            self.clean_tooltip(True)
            self.mouse_pressed=(mouseevent.xdata, mouseevent.ydata)

    ## is called whenever a mouse button is released while hovering over the plot
    ## if the left button was pressed and there are points within the selection area, select those points and show a
    ##  tooltip containing information about those selected points. If not, clean up.
    def handle_mouse_up(self, mouseevent):
        if mouseevent.button in [1,3]:
            xmin = min(mouseevent.xdata, self.mouse_pressed[0])
            xmax = max(mouseevent.xdata, self.mouse_pressed[0])
            ymin = min(mouseevent.ydata, self.mouse_pressed[1])
            ymax = max(mouseevent.ydata, self.mouse_pressed[1])
            if xmin == xmax and ymin == ymax:
                self.clean_tooltip(True)
            else:
                if mouseevent.button == 1:
                    self.ds.select("selected", self.param1, xmin, xmax, "show")
                    self.ds.select("selected", self.param2, ymin, ymax, "selected")
                    ind=self.df("selected").index.values
                    if len(ind)>0:
                        text="Selected area from ({:.1f}; {:.1f})\n\t to ({:.1f}; {:.1f})".format(xmin,ymin,xmax,ymax)
                        self.add_to_history(text)
                        self.draw_tooltip(mouseevent,ind, True)
                        self.unprocessed_action=max(self.unprocessed_action, 1)
                    else:
                        self.clean_tooltip(True)
                else:
                    self.clean_tooltip(True, emit=False)
                    self.ax.set_xlim((xmin,xmax))
                    self.ax.set_ylim((ymin,ymax))
                    self.canvas.draw()

    ## handle any mouse event where it has to be clarified whether there's a marker under the mouse or not. If so,
    ##  return all index values of the concerning markers.
    def handle_mouse_event(self, mouseevent, radius=5):
        """
        find the points within a certain radius from the mouse in
        data coords and attach the index numbers of the found elements
        which are the data points that were picked
        """
        self.clean_tooltip()

        #print("PICKER")
        #print(mouseevent, vars(mouseevent))
        xydata=self.ax.transData.transform(self.df("show")[[self.param1, self.param2]]).transpose()
        try:
            mxy= self.ax.transData.transform([mouseevent.xdata,mouseevent.ydata])
        except ValueError:
            return False,dict()
        xdata=xydata[0]
        ydata=xydata[1]
        mousex=mxy[0]
        mousey=mxy[1]
        if mouseevent.xdata is None:
            return False, dict()

        d = pd.np.sqrt((xdata - mousex)**2. + (ydata - mousey)**2.)
        ind = self.df("show").index.values[pd.np.nonzero(pd.np.less_equal(d, radius))[0]]

        if len(ind) >0:
            props = dict(ind=ind)
            return True, props
        else:
            return False, dict()

    ## draws a tooltip and generates the information it contains from an event with/and a list of index values
    def draw_tooltip(self, event, ind=None, selected=False):
        if ind is None:
            ind=event.ind
            event=event.mouseevent

        # Generate the Tooltip-String
        selstr=""
        if selected:
            selstr= "selected "

        if len(ind) is 1:
            text=selstr + "value:"
            self.ds.select_ids("selected", ind, "show")
            for col,cdata in self.df("selected").iteritems():
                text += '\n {}: \t{}'.format(col, cdata[ind[0]])
        else:
            text = selstr + "%s values:" % len(ind)
            if not selected:
                self.ds.select_ids("selected", ind, "show")
            self.ds.aggregate("sel_aggremin", "MIN", in_table="selected")
            self.ds.aggregate("sel_aggremax", "MAX", in_table="selected")

            for col,cdata in self.df("sel_aggremin").iteritems():
                text += '\n {}: \t{} to {}'.format(col, cdata[0], self.df("sel_aggremax")[col][0])

        # Draw the box and write the string on it

        c_height=self.canvas.figure.bbox.height
        c_width=self.canvas.figure.bbox.width
        y=c_height-event.y
        x=event.x

        #get bounding box of a possible tooltip
        self.plot_tooltip=self.canvas.get_tk_widget().create_text(x+2, y, anchor=tk.NW,text=text)
        bbox=self.canvas.get_tk_widget().bbox(self.plot_tooltip)
        self.canvas.get_tk_widget().delete(self.plot_tooltip)

        # print("bbox:", bbox)

        #make sure the tooltip is within bounds
        if bbox[2]>c_width:
            adj = -2
            if bbox[3]>c_height:
                anchor=tk.SE
            else:
                anchor=tk.NE
        else:
            adj = 2
            if bbox[3]>c_height:
                anchor=tk.SW
            else:
                anchor=tk.NW
        #get the new bounding box
        if anchor is not tk.NW: # =^= the anchor had to be modified
            self.plot_tooltip=self.canvas.get_tk_widget().create_text(x+adj, y, anchor=anchor,text=text)
            bbox=self.canvas.get_tk_widget().bbox(self.plot_tooltip)
            self.canvas.get_tk_widget().delete(self.plot_tooltip)

        self.plot_tooltip_rect = self.canvas.get_tk_widget().create_rectangle(bbox, fill="yellow")
        self.plot_tooltip=self.canvas.get_tk_widget().create_text(x+adj, y, anchor=anchor,text=text)


    # draws a timeline (as a plot)
    def draw_timeline(self):

        #df = self.df("show")
        ## create value for each day in data,
        ## depending on whether it is selected, shown etc.
        #shown_dates = self.build_contained_dict(df)

        selected_dates=[]
        if self.select_rect is not None:
            print("b",self.ds.exists("selected"))
            self.ds.groupby("selected_days", "MasterTime", "COUNT", "selected", bydate=True)
            selected_dates = self.df("selected_days").index.values
        shown_dates=self.df("shown_dates").index.values
        ## prepare data for timeline
        days = []
        values = []

        for day in self.df("all_days").index.values:
            if self.df("all_days")[self.param1][day]>0 and self.df("all_days")[self.param2][day]>0:
                days.append(day)
                ##if random() < 0.01:
                #if self.dates[self.startSlider.get()] <= day < self.dates[self.endSlider.get()]:
                if day in shown_dates:
                    values.append("blue")
                    if day in selected_dates:
                    #if random() < 0.05:
                        values.append("red")
                else:
                    values.append("lightskyblue")
        #print("d:",days, values)

        ## plot timeline
        fig = Figure(figsize=(12,1), dpi=75)
        ax = fig.add_subplot(111)

        ax.scatter(days, [1]*len(days), c=values,
                   marker='|', s=300)#, fontsize=10)
        #fig.xt
        hfmt = mdates.DateFormatter("%b '%y")
        # fig.subplots_adjust(left=0.03, right=0.97, top=1)

        ax.xaxis.set_major_formatter(hfmt)
        fig.autofmt_xdate()
        #ax.set_xticklabels(ax.xaxis.get_minorticklabels(), rotation=0)
        ax.set_xlim([datetime(2014,1,1,0,0,0), datetime(2015,1,1,0,0,0)])

        ## everything after this is turning off stuff that's plotted by default
        ax.yaxis.set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_ticklabels([])
        fig.tight_layout(pad=0)

        print(fig.get_figheight())
        #fig.subplots_adjust(top=1, right=0.99)

        ## add to GUI
        self.timeline = FigureCanvasTkAgg(fig, self)
        self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W, tk.S),columnspan=5)
        print("h:",self.timeline.figure.bbox.height)

    #####################
    # UPDATE-FUNCTIONS

    ## is called regularly, after the given delay
    def check_for_update(self):
        ## if there is an unprocessed action older than
        ## the given delay, update data

        #self.check_listbox_changes()

        if self.unprocessed_action>0 and \
            (time() - self.last_action) > self.UPDATE_DELAY/1000:
            print("redraw data")
            ## simply block the very first update...
            ## (there might be prettier solutions)
            if self.ignore_start_trigger:
                self.ignore_start_trigger = False
            else:
                ## update data
                self.update_plot()
        #print("checking for updates...")
        self.after(self.UPDATE_DELAY, self.check_for_update)

    """
     general data tasks:
     base [-> apply sliders ->]
     time-limited [-> (don't) aggregate ->]
     show

     show [-> select ->]
     selected [-> get min and max ->]



    """
    ## draw new data according to current positions of date sliders and the aggregation limit
    def update_plot(self):
        if self.unprocessed_action >= 4:
            if self.tdvar.get() is "0":
                self.ds.link("after_tidyup","base")
            else:
                self.ds.select("after_tidyup", "Large",a=0, in_table="base")
                self.ds.select("after_tidyup", "OutdoorTemp",b=40, in_table="after_tidyup")
                self.ds.select("after_tidyup", "RelHumidity",0,100, in_table="after_tidyup")
                self.ds.select("after_tidyup", "Small",a=0, in_table="after_tidyup")
                #self.action_str = "tidy up data, remove all points where:" \
                #                  "\n\tOutdoorTemp>40 or Small<0 or Large<0 or " \
                #                  "\n\tRelHumidity<0 or RelHumidity>100"

        if self.unprocessed_action >=3:
            fromVal = self.startSlider.get()
            endVal = self.endSlider.get()

            self.ds.select(out_table="time-limited", attr_name="MasterTime",
                a=self.dates[fromVal], b=self.dates[endVal], in_table="after_tidyup")
            #self.df = self.ds.get_data("time_filter").df()
            if self.aggregation_limit==1:
                self.ds.link("show", "time-limited")
            else:
                self.ds.aggregate(out_table="show", mode="AVG", limit=self.aggregation_limit, in_table="time-limited")
            self.ds.groupby("shown_dates","MasterTime", "COUNT", "show", bydate=True)
#        try:
        if self.unprocessed_action>=2:
            self.draw_data()
            self.draw_timeline()
            self.add_to_history(self.action_str)
        else:
            self.draw_timeline()
#        except:
#            pass
        self.unprocessed_action=0


    ## update view with specified data
    def draw_data(self):
        #ax.plot(self.df[self.param1], self.df[self.param2], marker="o", linewidth=0, picker=self.line_picker)
        self.clean_tooltip(True)
        self.ax.clear()
        self.ax.grid(True)
        x=self.df("show")[self.param1]
        y=self.df("show")[self.param2]
        self.plot=self.ax.scatter(x=x, y=y, marker="o", linewidths=0,picker=self.handle_pick)

        self.ax.set_xlabel(self.param1)
        self.ax.set_ylabel(self.param2)
        #self.ax.set_xlim(x.min(), x.max(), emit=False)
        #self.ax.set_ylim(y.min(), y.max(), emit=False)
        #self.canvas.
        self.fig.tight_layout(pad=0)
        self.canvas.draw()

    #################
    # helper-functions

    def df(self, name=None) -> pd.DataFrame:
        return self.ds.get_data(name).df()

    ## add line to history window
    def add_to_history(self, text):
        self.history.insert('end', "\n" + text)  # + "\n")
        self.history.see("end")

    ## remove the tooltip if shown
    def clean_tooltip(self, with_select_rect=False, emit=True):
        if self.plot_tooltip is not None:
            self.canvas.get_tk_widget().delete(self.plot_tooltip)
            self.canvas.get_tk_widget().delete(self.plot_tooltip_rect)
            self.plot_tooltip = None
        if with_select_rect and self.select_rect is not None:
            self.canvas.get_tk_widget().delete(self.select_rect)
            self.select_rect=None
            if emit:
                self.unprocessed_action=max(self.unprocessed_action, 1)



## select data from datasource in this time range
#def filter_data(ds, start_time, end_time):
#    ds.select(out_table="time_filter", attr_name="MasterTime",
#        a=start_time, b=end_time)
#    return ds.get_data("time_filter").df()



## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
print("read")
#print(ds.get_base_data().df())
root = tk.Tk()

app = VisAnaGUI(master=root, ds=ds)

app.mainloop()
