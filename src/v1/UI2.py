import tkinter as tk
from tkinter import Spinbox, StringVar
from tkinter.ttk import Combobox

import GrainSelection
import analytics
import matplotlib

import datasource
from datasource import COLORS
import Selector_old

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
from time import time
import util
import numpy as np

from sklearn.linear_model import LinearRegression





class VisAnaGUI(tk.LabelFrame):

    ## constants for current mode
    PLOT_MODE = 10
    ANALYTICS_MODE = 11
    ## constants for shown cluster plot
    SMALL_MULTIPLES = 20
    SMALL_HISTOS = 21

    #update levels, each level includes all lower ones
    NOTHING=0
    TIMELINE_SELECTION=1
    TIMELINE_DAYSINPLOT=2
    PLOT=3
    PLOT_DATA=4
    DATA_TIDYUP=5






    def __init__(self, master=None, ds=None):

        #self.dates = []
        #for dt in rrule.rrule(rrule.DAILY,
        #                      dtstart=datetime(2014,1,1,0,0,0),
        #                      until=datetime(2015,1,1,0,0,0)):
        #    self.dates.append(dt.date())
        self.mode = self.PLOT_MODE
        self.cluster_k = 4

        self.mininterval=60


        ## save data source
        self.ds = ds #type:datasource.DataSource
        # self.ds.groupby("all_days", datasource.TIME_ATTR, "COUNT","base", bydate=True)
        #self.ds.aggregateTime("all_days", "COUNT",60,"base")
        # self.ds.aggregateTime("all_days", "COUNT",24*60,"base")
        #self.ds.link("show")
        #self.df=ds.get_base_data().df()

        ## parameter variables for listboxes
        self.param_list = list(ds.get_data("base").get_attr_names())#["MasterTime", "Small", "Large", "OutdoorTemp","RelHumidity"]

        self.param2 = self.param_list[1]
        self.param1 = self.param_list[2]
        self.aggregation_limit=360

        ## simple string to describe last action (for history)
        self.action_str = "Show base data"

        self.plot_tooltip=None
        self.select_rect=None

        self.draw_frame(master)

        self.mouse_pressed=None
        self.clause=dict()

        ## save time of last update to prevent too many
        ## updates when using sliders
        self.last_action = time()
        ## delay after last data update and action (in ms)
        self.UPDATE_DELAY = 500
        ## was there an action triggering an update?
        # (0=no, 1=only the timeline, 2=axes and timeline, 3=with selection, 4 with tidyup)
        self.unprocessed_action = self.DATA_TIDYUP
        ## calls check_for_update() method after delay has passed
        self.after(self.UPDATE_DELAY, self.check_for_update)
        ## dummy variable to ignore first update. sliders trigger an
        ## event at startup, which would lead to redundant update of data
        self.ignore_start_trigger = True

        ## draw data at startup
        self.update_data()

    #######################
    # UI CREATION

    def draw_frame(self, master):
        tk.LabelFrame.__init__(self, master)#, bg="red")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.title("Visual Analyser - Gui")

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(2,minsize=100)
        #self.configure(background="red")

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

        self.toggle_hist_btn = tk.Button(self.toolbar)
        self.toggle_hist_btn["text"] = "Toggle History"
        self.toggle_hist_btn["command"] = self.toggle_history
        self.toggle_hist_btn.grid(column=4, row=0, sticky=(tk.W, tk.N))

        #        self.tdvar = tk.StringVar(value="0")
        #        self.tidy_up = tk.Checkbutton(self.toolbar, text='Tidy Up Data', command=self.handle_tidy_up,
        #                                      variable=self.tdvar)
        #        self.tidy_up.grid(column=2, row=0, sticky=(tk.W, tk.N))

        self.rgvar = tk.StringVar(value="0")
        self.regression = tk.Checkbutton(self.toolbar, text='Draw Regression', command=self.handle_regression,
                                         variable=self.rgvar)
        self.regression.grid(column=3, row=0, sticky=(tk.W, tk.N))

        self.left_sidebar = tk.Frame(self)
        self.left_sidebar.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.projector = self.create_listboxes(self.left_sidebar)
        self.projector.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W))

        self.selector = Selector_old.Selector_old(self.left_sidebar, self.ds, self.handle_selector_change)
        self.selector.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W))



        self.history_text = "::LOG::\n"
        self.create_history()

        self.create_plot()

    def create_history(self):
        self.history_shown = True

        self.history = tk.Text(self, width=45)
        self.history.grid(column=2, row=3, sticky=(tk.N, tk.E, tk.S), rowspan=2)
        self.history.insert('end', self.history_text)

        self.history.see("end")

        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=3, row=3, sticky=(tk.N, tk.S), rowspan=2)
        self.history['yscrollcommand'] = self.historyslider.set



    def create_listboxes(self, parent) -> tk.LabelFrame:
        frame=tk.LabelFrame(parent)#, bg="red")


        self.paramlabel = tk.Label(frame, text="Choose Parameters")
        self.paramlabel.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.W), columnspan=2)

        ## listboxes for parameter selection
        self.param1lbl = tk.Label(frame, text="X-Axis:")
        self.param1lbl.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W))
        self.param1var = StringVar()
        self.param1var.set(self.param1)
        self.param1box=Combobox(frame, textvariable=self.param1var, state="readonly")
        self.param1box['values'] = self.param_list
        self.param1box.bind('<<ComboboxSelected>>', self.handle_paramsChanged)
        self.param1box.grid(column=1, row=1, sticky=(tk.N, tk.E, tk.W))


        self.param1lbl = tk.Label(frame, text="Y-Axis:")
        self.param1lbl.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W))
        self.param2var = StringVar()
        self.param2var.set(self.param2)
        self.param2box = Combobox(frame, textvariable=self.param2var, state="readonly")
        self.param2box['values'] = self.param_list
        self.param2box.bind('<<ComboboxSelected>>', self.handle_paramsChanged)
        self.param2box.grid(column=1, row=2, sticky=(tk.N, tk.E, tk.W))

        #        self.param2box = Listbox(self.projector, exportselection=0)
        #        for item in self.param_list:
        #            self.param2box.insert("end", item)
        #        param2_index = self.param_list.index(self.param2)
        #        self.param2box.select_set(param2_index)
        #        self.param2box.bind('<<ComboboxSelected>>', self.handle_paramsChanged)
        #        self.param2box.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W))

        self.var = StringVar(frame)
        self.var.set(str(self.aggregation_limit))
        self.noise_spin = Spinbox(frame, from_=1, to=1440, textvariable=self.var ,width=4)
        self.noise_spin.grid(column=0, row=3, sticky=(tk.E, tk.W))

        self.testbutton = tk.Button(frame)
        self.testbutton["text"] = "Aggregate values (minutes)"
        self.testbutton["command"] = self.handle_aggregate_btn
        self.testbutton.grid(column=1, row=3, sticky=(tk.W, tk.N))
        return frame

    # ## add sliders to GUI
    # def create_sliders(self):
    #     ## init sliders
    #
    #     #self.filter = tk.LabelFrame(self, bg="#0066ff")
    #     self.filter = tk.LabelFrame(self, bg="red")
    #     self.filter.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)
    #     self.filter.columnconfigure(1, weight=1)
    #     self.filter.columnconfigure(0, weight=0)
    #
    #     self.startSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.update_start)
    #     self.startSlider.set(0)
    #     self.endSlider = Scale(self.filter, from_=0, to=365, orient=HORIZONTAL, command=self.update_end)
    #     self.endSlider.set(365)
    #
    #     ## add sliders and labels to GUI
    #     self.startSlider.grid(column=1, row=0, sticky=(tk.W, tk.N, tk.E))
    #     self.startlabel = tk.Label(self.filter, text="FROM \tVALUE")
    #     self.startlabel.grid(column=0, row=0, sticky=(tk.W))
    #     self.endSlider.grid(column=1, row=1, sticky=(tk.W, tk.S, tk.E))
    #     self.endlabel = tk.Label(self.filter, text="TO \tVALUE")
    #     self.endlabel.grid(column=0, row=1, sticky=(tk.W))

    #add an empty plot to the GUI
    def create_plot(self):
        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure
        self.ax = self.fig.add_subplot(111) #type:Axes
        #self.ax2 = self.fig.add_subplot(212)
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, self) ##type:FigureCanvasTkAgg

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

    ## generate clusters and asks for custom grain classes
    def create_clusters(self, in_table="base"):
        ## call dialogue window to ask for custom grain classes
        Mbox = GrainSelection.Mbox
        Mbox.root = root
        mbox = Mbox()
        ## wait for answer
        root.wait_window(mbox.top)
        ## -> result is in mbox.classesDict

        ## ask if valid answer has been submitted
        if mbox.success:
            ## fetch answers in dict with changed labels
            custom_classes_dict = {}
            #print(mbox.classesDict)
            for k,v in mbox.classesDict.items():
                col = "GRAIN_CLASS_"+str(k)
                custom_classes_dict[col] = v
            self.c_param_list = sorted(list(custom_classes_dict.keys()))

            #print("CREATE CLUSTERS")

            ## call analytics functions
            analytics.create_distributions(in_table, "out", self.ds, custom_classes_dict=custom_classes_dict)
            self.centroids = analytics.calc_clusters(in_table="cluster_distr", out_table="clustered", datasource=self.ds, k=self.cluster_k, colNames=self.c_param_list)
            #print("\tCLUSTERED")

            ## change state variables so the proper graph is displayed
            self.mode = self.ANALYTICS_MODE
            #self.plot_type = self.SMALL_HISTOS
            self.plot_type = self.SMALL_MULTIPLES
            #print("change mode to ",self.mode)

            ## TODO: might need to be changed?!
            self.unprocessed_action=self.PLOT_DATA

            self.add_to_history("generate clusters")
            self.action_str = "Generate clusters"
            #print("\tCLUSTERING FINISHED")

    ## dummy method
    def reset_to_start(self):
        self.create_clusters()


        self.clean_tooltip(True)
        #self.param1box.select_set(self.param_list.index("Large"))
        #self.param2box.select_set(self.param_list.index("Small"))
        #        self.startSlider.set(0)
        #        self.endSlider.set(365)
        self.var.set("1")
        self.handle_aggregate_btn()
        #self.tdvar.set("0")
        self.unprocessed_action=self.DATA_TIDYUP

        self.add_to_history("reset to basedata")
        self.action_str = "Show base data"
        #print("hi there, everyone!")

    def toggle_history(self):
        if self.history_shown:
            self.destroy_history()
        else:
            self.create_history()

    def destroy_history(self):
        self.history_shown = False
        self.history.destroy()
        self.historyslider.destroy()
    #self.history_text = self.history.

    def handle_aggregate_btn(self):
        self.aggregation_limit = int(self.noise_spin.get())

        self.action_str = "Aggregated values: "+str(self.aggregation_limit)+"min"

        self.trigger_update(level=self.PLOT_DATA)

    #    def handle_tidy_up(self):
    #        if self.tdvar.get() is "0":
    #            self.action_str="show raw data"
    #        else:
    #            self.action_str="tidy up data, remove all points where:" \
    #                            "\n  OutdoorTemp>40 or Small<0 or Large<0 or " \
    #                            "\n  RelHumidity<0"
    #        self.trigger_update(level=self.DATA_TIDYUP)

    def handle_regression(self):
        if self.rgvar.get() is "0":
            self.action_str="hide regression"
        else:
            self.action_str="draw regression"
        self.trigger_update(level=self.PLOT)

    def handle_view_change(self,ax=None):
        if ax is None:
            ax=self.ax
        self.handle_changed_axes()
        print("viewport changed to", ax.get_xlim(), ax.get_ylim())

    #########
    ## SLIDER METHODS
    ## we need separate update functions for the sliders, 
    ## as we could otherwise not distinguish between changing
    ## the first or second slider
    #########

    # ## triggered by changing startslider value
    # def update_start(self, event):
    #     fromVal = self.startSlider.get()
    #     endVal = self.endSlider.get()
    #     if endVal < fromVal:
    #         self.endSlider.set(fromVal)
    #
    #     self.handle_slider_update()
    #
    # ## triggered by changing endslider value
    # def update_end(self, event):
    #     fromVal = self.startSlider.get()
    #     endVal = self.endSlider.get()
    #     if endVal < fromVal:
    #         self.startSlider.set(endVal)
    #
    #     self.handle_slider_update()
    #
    # ## handle data update event, i.e. a slider changed.
    # def handle_slider_update(self):
    #     fromVal = self.startSlider.get()
    #     endVal = self.endSlider.get()
    #     self.startlabel["text"] = "FROM \t"+str(self.dates[fromVal])
    #     self.endlabel["text"] = "TO \t"+str(self.dates[endVal])
    #     self.trigger_update(level=self.PLOT_DATA)
    #     self.last_action = time()
    #     self.action_str = "New time interval: "+str(self.dates[fromVal])+" - "+str(self.dates[endVal])

    ## handle data update event, i.e. a slider changed.
    def handle_selector_change(self,clause):
        self.clause=clause

        self.trigger_update(level=self.PLOT_DATA)
        self.last_action = time()
        self.action_str = "New selection: "+str(clause)



    ## a different parameter was chosen
    def handle_paramsChanged(self, e):
        #self.param1 = self.param_list[self.param1box.curselection()[0]]
        self.param1 = self.param1var.get()
        self.param1box.select_clear()


        self.param2 = self.param2var.get()
        self.param2box.select_clear()
        #        self.param2 = self.param_list[self.param2box.curselection()[0]]

        self.action_str = "New parameters: " + self.param1 + " & " + self.param2
        self.trigger_update(level=self.PLOT)



    ###################
    # PLOT-EVENT HANDLER

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
    i=1
    def handle_hover(self, mouseevent):
        if not mouseevent.button in [1,3] and self.select_rect is None:
            isover, props = self.handle_mouse_event(mouseevent)

            if isover:
                self.draw_tooltip(mouseevent, props["ind"])

        elif mouseevent.button in [1,3]:
            ## handle case if mouse is outside the canvas
            if mouseevent.xdata == None:
                xmin = self.mouse_pressed[0]
                xmax = self.mouse_pressed[0]
                ymin = self.mouse_pressed[1]
                ymax = self.mouse_pressed[1]
            else:
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
            ## handle case if mouse is outside the canvas
            if mouseevent.xdata == None:
                xmin = self.mouse_pressed[0]
                xmax = self.mouse_pressed[0]
                ymin = self.mouse_pressed[1]
                ymax = self.mouse_pressed[1]
            else:
                xmin = min(mouseevent.xdata, self.mouse_pressed[0])
                xmax = max(mouseevent.xdata, self.mouse_pressed[0])
                ymin = min(mouseevent.ydata, self.mouse_pressed[1])
                ymax = max(mouseevent.ydata, self.mouse_pressed[1])
            if xmin == xmax and ymin == ymax:
                self.clean_tooltip(True)
            else:
                if mouseevent.button == 1:
                    if self.param1 == datasource.TIME_ATTR:
                        xmin = mdates.num2date(xmin)
                        xmax = mdates.num2date(xmax)
                    if self.param2 == datasource.TIME_ATTR:
                        ymin = mdates.num2date(ymin)
                        ymax = mdates.num2date(ymax)
                    self.ds.select("selected", self.param1, xmin, xmax, "show")
                    self.ds.select("selected", self.param2, ymin, ymax, "selected")
                    ind=self.df("selected").index.values
                    if len(ind)>0:
                        self.action_str="Selected area from ({:.1f}; {:.1f})\n\t to ({:.1f}; {:.1f})".format(xmin,ymin,xmax,ymax)
                        #self.add_to_history(text)
                        self.draw_tooltip(mouseevent,ind, True)
                        self.trigger_update(level=self.TIMELINE_SELECTION)
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
        if self.param1 == datasource.TIME_ATTR or self.param2 == datasource.TIME_ATTR:
            return False,dict()
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
        if self.aggregation_limit <= self.mininterval:
            self.ds.aggregateTime("all_days", "COUNT", self.mininterval, "base")
        else:
            self.ds.aggregateTime("all_days", "COUNT", self.aggregation_limit, "base")

        selected_dates=[]
        if self.select_rect is not None:
            print("b",self.ds.exists("selected"))
            #self.ds.groupby2("selected_days", datasource.TIME_ATTR, "COUNT", "selected", bydate=True)
            #self.ds.aggregateTime("selected_days", "COUNT",24*60, "selected")
            self.ds.aggregateTime("selected_days", "COUNT",1, "selected")
            selected_dates = self.df("selected_days").index.values
        shown_dates=self.df("shown_dates").index.values

        base_dates=self.df("all_days").index.values

        ## extract first and last date
        start_date = base_dates[0]
        end_date = base_dates[-1]
        #days_diff = ((end_date-start_date) / np.timedelta64(1, 'D'))

        ## prepare data for timeline
        days = []
        values = []
        #print(self.df("all_days").head(2))

        #self.df("all_days").
        for date in self.df("all_days").index.values:
            self.df("all_days")
            col1_has_values=((self.param1 == datasource.TIME_ATTR) or (self.df("all_days")[self.param1][date]>0))
            col2_has_values=((self.param2 == datasource.TIME_ATTR) or (self.df("all_days")[self.param2][date]>0))
            if col1_has_values and col2_has_values:
                days.append(date)
                ##if random() < 0.01:
                #if self.dates[self.startSlider.get()] <= day < self.dates[self.endSlider.get()]:
                if date in shown_dates:
                    values.append("blue")
                    if date in selected_dates:
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
        hfmt = mdates.DateFormatter("1. %b '%y")
        # fig.subplots_adjust(left=0.03, right=0.97, top=1)

        ax.xaxis.set_major_formatter(hfmt)
        fig.autofmt_xdate()
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
        fig.tight_layout(pad=0)

        #print(fig.get_figheight())
        #fig.subplots_adjust(top=1, right=0.99)

        ## add to GUI
        self.timeline = FigureCanvasTkAgg(fig, self)
        self.timeline.get_tk_widget().grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W, tk.S),columnspan=5)
        #print("h:",self.timeline.figure.bbox.height)

    #####################
    # UPDATE-FUNCTIONS

    ## is called regularly, after the given delay
    def check_for_update(self):
        ## if there is an unprocessed action older than
        ## the given delay, update data

        #self.check_listbox_changes()

        if self.unprocessed_action>self.NOTHING and \
                        (time() - self.last_action) > self.UPDATE_DELAY/1000:
            ## simply block the very first update...
            ## (there might be prettier solutions)
            if self.ignore_start_trigger:
                self.ignore_start_trigger = False
            else:
                ## update data
                self.update_data()
        #print("checking for updates...")
        self.after(self.UPDATE_DELAY, self.check_for_update)

    """
     general data tasks:
     after_tidyup [-> apply sliders ->]
     time-limited [-> (don't) aggregate ->]
     show

     show [-> select ->]
     selected [-> get min and max ->]



    """
    ## draw new data according to current positions of date sliders and the aggregation limit
    def update_data(self):
        #if self.unprocessed_action >= self.DATA_TIDYUP:
            #if self.tdvar.get() is "0":
            #    self.ds.link("after_tidyup","base")
            #else:
            #    self.ds.select("after_tidyup", "Large",a=0, in_table="base")
            #    self.ds.select("after_tidyup", "OutdoorTemp",b=40, in_table="after_tidyup")
            #    self.ds.select("after_tidyup", "RelHumidity",a=0, in_table="after_tidyup")
            #    self.ds.select("after_tidyup", "Small",a=0, in_table="after_tidyup")
                #self.action_str = "tidy up data, remove all points where:" \
                #                  "\n\tOutdoorTemp>40 or Small<0 or Large<0 or " \
                #                  "\n\tRelHumidity<0 or RelHumidity>100"

        if self.unprocessed_action >=self.PLOT_DATA:
            #fromVal = self.startSlider.get()
            #endVal = self.endSlider.get()

            #self.ds.link("time-limited","after_tidyup")
            #self.ds.select(out_table="time-limited", attr_name=datasource.TIME_ATTR,
            #    a=self.dates[fromVal], b=self.dates[endVal], in_table="after_tidyup")
            #self.df = self.ds.get_data("time_filter").df()
            self.ds.select_complex("sel",self.clause, "base")
            if self.aggregation_limit==1:
                self.ds.link("show", "sel")
            else:
                self.ds.aggregateTime(out_table="show", mode="AVG", minutes=self.aggregation_limit, in_table="sel")
                #self.ds.aggregate(out_table="show", mode="AVG", limit=self.aggregation_limit, in_table="base")
            #self.ds.groupby("shown_dates",datasource.TIME_ATTR, "COUNT", "show", bydate=True)
            self.ds.aggregateTime("shown_dates","COUNT", self.aggregation_limit, in_table="sel")
            #self.ds.aggregateTime("shown_dates","COUNT", 24*60,"show")
        #        try:
        if self.unprocessed_action>=self.PLOT:
            if self.mode == self.PLOT_MODE:
                print("draw normal plots")
                self.draw_plot()
            elif self.mode == self.ANALYTICS_MODE:
                print("draw cluster plots")
                if self.plot_type == self.SMALL_MULTIPLES:
                    print("\tdraw small multiples")
                    self.create_multiple_plots()
                elif self.plot_type == self.SMALL_HISTOS:
                    print("\tdraw small histograms")
                    self.create_distr_plots()

        self.draw_timeline()
        #print("add_to_history:",self.action_str)
        if self.action_str is not None:
            self.add_to_history(self.action_str)
        #        except:
        #            pass
        self.unprocessed_action=self.NOTHING

    def create_distr_plots(self):
        self.clean_tooltip(True)
        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure
        self.ax = self.fig.add_subplot(111) #type:Axes

        #subplot_num = 0
        #print(self.centroids)
        y_pos = np.arange(len(self.c_param_list))
        #print(y_pos)
        width = 0.95/self.cluster_k
        #colors = ["#d62728", "blue", "green", "brown"]
        for c in range(0, self.cluster_k):
            #subplot_num += 1
            ystdev = []
            one_value_cluster = self.df("clustered").loc[self.df("clustered")['clusterlabels'] == c]

            #for i in range(0, len(datasource.GRAIN_COLS)):
            for i in range(0, len(self.c_param_list)):
                col = one_value_cluster[self.c_param_list[i]]
                stdev = np.std(col)
                ystdev.append(stdev)

            cen = [self.centroids[c][i] for i in range(0, len(self.c_param_list))]
            ## cluster label for legend 
            c_label = "Cluster "+str(c)
            self.ax.bar(y_pos + width*(c-(self.cluster_k/2.3)), cen, width, align="center", alpha=0.75, color=COLORS[c], ecolor="black", yerr=ystdev, label=c_label)
        self.ax.grid(True)
        #self.ax.set_xticklabels
        #self.ax.set_ylim(0, 1, emit=False)
        max_y_val = max(map(max, self.centroids))
        self.ax.set_ylim(0, max_y_val+0.1, emit=False)

        self.ax.set_xticks(y_pos + width / 4)
        self.ax.set_xticklabels(self.c_param_list)

        self.ax.callbacks.connect('xlim_changed', self.handle_view_change)
        self.ax.callbacks.connect('ylim_changed', self.handle_view_change) 
        
        ## add legend
        self.ax.legend(loc="upper right", shadow=True)

        self.canvas = FigureCanvasTkAgg(self.fig, self) ##type:FigureCanvasTkAgg

        #self.canvas.mpl_connect('motion_notify_event', self.handle_hover)
        #self.canvas.mpl_connect('button_press_event', self.handle_mouse_down)
        #self.canvas.mpl_connect('button_release_event', self.handle_mouse_up)
        #self.canvas.mpl_connect('pick_event', self.draw_tooltip)

        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))

        # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        #self.ctbwidget=tk.Frame(self)
        #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
        #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)

        util.zoom_factory(self.ax)

        self.fig.tight_layout(pad=0)
        self.canvas.draw()

        #print("DISTRIBUTIONS PLOTTED")


    #add an empty plot to the GUI
    def create_multiple_plots(self):
        self.clean_tooltip(True)
        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure

        param_combos = []
        subplot_num = 0
        paraLen = len(self.c_param_list)
        axarr = [[]]
        dummy = [[]]
        sharey = {}

        for qi in range(0, paraLen):
            q = self.c_param_list[qi]
            #subplot_num = ((subplot_num%10)*10)+111
            #print("subplot_num=",str(subplot_num))
            for pi in range(0, paraLen):
                #print("qi =",str(qi))
                p = self.c_param_list[pi]
                #subplot_num += 1
                if pi < qi:#not p == q: 
                    subplot_num = (qi-1)*(paraLen-1) + (pi+1)
                    print(subplot_num)
                    #print("\tsubplot_num=",str(subplot_num))
                    param_combos.append((p,q))
                    x = self.df("clustered")[p]
                    y = self.df("clustered")[q]
                    print("pi=",str(pi),"qi=",str(qi))
                    #if qi>0 & pi>0:
                    #    self.ax = self.fig.add_subplot(paraLen-1, paraLen-1, subplot_num, sharex=axarr[0][pi-1], sharey=axarr[qi][0])
                    #if qi>1:
                    #    ax1 = self.fig.add_subplot(paraLen-1, paraLen-1, subplot_num, sharex=sharex[pi])
                    #if pi>1:
                    #    ax1 = self.fig.add_subplot(paraLen-1, paraLen-1, subplot_num, sharey=sharey[qi])
                    #else:
                    ax1 = self.fig.add_subplot(paraLen-1, paraLen-1, subplot_num) 

                    #if pi==0:
                    #    print("add sharey for",str(qi))
                    #    sharey[qi] = ax1

                    #print(self.centroids[1,0])
                    for i in range(self.cluster_k):
                        one_value_cluster = self.df("clustered").loc[self.df("clustered")['clusterlabels'] == i]
                        ax1.scatter(one_value_cluster[self.c_param_list[pi]], one_value_cluster[self.c_param_list[qi]], color=COLORS[i], marker=".", alpha=0.1, s=2)
                        #print("i:",str(i),"pi:",str(pi),"qi:",str(qi))
                        ax1.plot(self.centroids[i][pi],self.centroids[i][qi],'kx')

                    #self.plot=self.ax.scatter(x=x, y=y, marker="o", linewidths=0,picker=self.handle_pick)

                    if qi == paraLen-1:
                        paraLabel = p
                        if "GRAIN_CLASS" in p: #custom class
                            paraLabel = "CLASS"+p[-1]
                        ax1.set_xlabel(paraLabel)
                    else:
                        ax1.set_xticklabels([])

                    if pi == 0:
                        paraLabel = q
                        if "GRAIN_CLASS" in q: #custom class
                            paraLabel = "CLASS"+q[-1]
                        ax1.set_ylabel(paraLabel)
                    else:
                        ax1.set_yticklabels([])

                    ax1.grid(True)
                    ax1.set_xlim(x.min(), x.max(), emit=False)
                    ax1.set_ylim(y.min(), y.max(), emit=False)
                    #ax1.callbacks.connect('xlim_changed', self.handle_view_change)
                    #ax1.callbacks.connect('ylim_changed', self.handle_view_change) 
                    #axarr[-1].append(ax1)
                    #dummy[-1].append(0)
                    #if pi == paraLen-1:
                    #    axarr.append([])
                    #    dummy.append([])
                    #print(axarr)


        self.canvas = FigureCanvasTkAgg(self.fig, self) ##type:FigureCanvasTkAgg

        #self.canvas.mpl_connect('motion_notify_event', self.handle_hover)
        #self.canvas.mpl_connect('button_press_event', self.handle_mouse_down)
        #self.canvas.mpl_connect('button_release_event', self.handle_mouse_up)
        #self.canvas.mpl_connect('pick_event', self.draw_tooltip)

        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))

        # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        #self.ctbwidget=tk.Frame(self)
        #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
        #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)

        util.zoom_factory(self.ax)

        self.fig.tight_layout(pad=0)
        self.canvas.draw()

    ## update view with specified data
    def draw_plot(self):
        #ax.plot(self.df[self.param1], self.df[self.param2], marker="o", linewidth=0, picker=self.line_picker)
        self.clean_tooltip(True)
        self.ax.clear()
        self.ax.grid(True)
        x=self.ds.get_data("show").get_column(self.param1)
        y=self.ds.get_data("show").get_column(self.param2)
        #if self.param1 == datasource.TIME_ATTR or self.param2 == datasource.TIME_ATTR:
        #    #self.plot=self.ax.plot(x, y,picker=self.handle_pick)#, marker="o", linewidths=0,picker=self.handle_pick)
        #    self.plot = self.ax.scatter(x=x, y=y, picker=self.handle_pick)
        #else:
        self.plot=self.ax.scatter(x=x, y=y, marker="o",color="black", s=4, alpha=0.2,linewidths=0,
                                  picker=self.handle_pick)

        self.ax.set_xlabel(self.param1)
        self.ax.set_ylabel(self.param2)
        self.ax.set_xlim(x.min(), x.max(), emit=False)
        self.ax.set_ylim(y.min(), y.max(), emit=False)
        self.ax.callbacks.connect('xlim_changed', self.handle_view_change)
        self.ax.callbacks.connect('ylim_changed', self.handle_view_change)
        #self.canvas.
        self.fig.tight_layout(pad=0)

        if self.rgvar.get() is not "0" and not (self.param2 == datasource.TIME_ATTR):
            self.draw_regression()
        self.canvas.draw()

    def draw_regression(self):
        ## we need to remove rows with NaNs first
        completedf = self.df("show")
        completedf = completedf[pd.notnull(completedf[self.param1])]
        completedf = completedf[pd.notnull(completedf[self.param2])]
        if self.param1 == datasource.TIME_ATTR:
            completedf["delta_time"] = (completedf[datasource.TIME_ATTR] - completedf[datasource.TIME_ATTR].min()) / np.timedelta64(1, "m")
            X = completedf["delta_time"].to_frame()
        else:
            X = completedf[self.param1].to_frame()
        y = completedf[self.param2].to_frame()

        lr = LinearRegression()
        lr.fit(X,y)
        print(lr.coef_)
        if self.param1 == datasource.TIME_ATTR:
            self.ax.plot(completedf[datasource.TIME_ATTR], lr.predict(X), color="red")
        else:
            self.ax.plot(X, lr.predict(X), color="red")

    #################
    # helper-functions

    def df(self, name=None) -> pd.DataFrame:
        return self.ds.get_data(name).df()

    ## add line to history window
    def add_to_history(self, text):
        self.history_text += "\n" + text
        if self.history_shown:
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
                self.action_str = None
                self.trigger_update(self.TIMELINE_SELECTION)

    def trigger_update(self,level):
        self.unprocessed_action = max(self.unprocessed_action,level)



## select data from datasource in this time range
#def filter_data(ds, start_time, end_time):
#    ds.select(out_table="time_filter", attr_name="MasterTime",
#        a=start_time, b=end_time)
#    return ds.get_data("time_filter").df()



## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-32-grain-size-classes-2014.dat")
print("read")
#print(ds.get_base_data().df())
root = tk.Tk()

app = VisAnaGUI(master=root, ds=ds)

app.mainloop()
