from tkinter import Frame, Label, StringVar, N, E, W, S, Spinbox
from tkinter.font import Font
from tkinter.ttk import Combobox, LabelFrame, Checkbutton, Button, Notebook

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

import util
from datasource import DataSource, COLORS


#from v2.Window import VisAnaWindow



class SimpleScatter(Frame):
    def __init__(self,parent,master):
        super(SimpleScatter,self).__init__(parent)
        self.window=master #type:VisAnaWindow
        self.parent=parent

        self.param_y=None;self.param_x=None

        self.ds=self.window.ds #type:DataSource

        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)

        self.sidebar=Notebook(self)
        self.sidebar.grid(column=0, row=0, sticky=(S,W,N,E))


        if self.ds is None:
            self.settings=SSControls(self.sidebar, self,None)
            self.sidebar.add(self.settings, text="Settings")

            #self.settings.grid(column=1, row=0, sticky=(S,W,N,E))

        else:
            self.settings=SSControls(self.sidebar, self,self.ds.base().get_attr_names())
            self.sidebar.add(self.settings, text="Settings")
            #self.settings.grid(column=0, row=0, sticky=(S,W,N,E))
            self.param_x=self.settings.getX()
            self.param_y = self.settings.getY()

        self.create_tooltip_frame(destroy=False)

        self.was_normalized_before=False

        self.create_plot()

        self.select_rect=None



    def create_plot(self):
        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure
        self.ax = self.fig.add_subplot(111) #type:Axes
        #self.ax2 = self.fig.add_subplot(212)
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, self) #type:FigureCanvasTkAgg

        self.canvas.mpl_connect('motion_notify_event', self.handle_hover)
        self.canvas.mpl_connect('button_press_event', self.handle_mouse_down)
        self.canvas.mpl_connect('button_release_event', self.handle_mouse_up)
        #self.canvas.mpl_connect('pick_event', self.draw_tooltip)

        self.canvas.get_tk_widget().grid(column=1, row=0, sticky=(N, E, W, S), rowspan=2)

        # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        #self.ctbwidget=tk.Frame(self)
        #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
        #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)

        #self.ax.callbacks.connect('xlim_changed', self.handle_changed_axes)
        #self.ax.callbacks.connect('ylim_changed', self.handle_changed_axes)

        util.zoom_factory(self.ax)


    #### Handle Graph signals

    ###################
    # PLOT-EVENT HANDLER
    def handle_changed_axes(self, ev=None):
 
        self.clean_tooltip()
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.xmin=xlim[0]
        self.xmax=xlim[1]
        self.ymin=ylim[0]
        self.ymax=ylim[1]
        text = "Focus changed to: x=[{:.1f};{:.1f}] and y=[{:.1f};{:.1f}]".format(xlim[0], xlim[1], ylim[0], ylim[1])

        self.window.history.add(text)

    ## is called by the plot to confirm if the mouseevent was inside/on a plotted line or a marker
    def handle_pick(self, line, mouseevent):

        if mouseevent.button == 1:
            return self.handle_mouse_event(mouseevent)
        else:
            return False, dict()

    ## is called to to do something when the mouse hovers over the plot and has changed its position.
    ## if no mousebutton is pressed and no points were selected, a hover-tooltip is shown.
    ## if the left button is pressed, (re-)draw the selection indicator
    def handle_hover(self, mouseevent):
        if self.ds is None:
            return;
        if not mouseevent.button in [1, 3] and self.select_rect is None:
            isover, props = self.handle_mouse_event(mouseevent)

            if isover:
                self.draw_tooltip(mouseevent, props["ind"])

        elif mouseevent.button in [1, 3]:
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
            bbox = (xmin, ymin, xmax, ymax)
            self.clean_tooltip(True, emit=False)
            bbox2 = self.ax.transData.transform(bbox)
            c_height = self.canvas.figure.bbox.height
            bbox3 = (bbox2[0], c_height - bbox2[1], bbox2[2], c_height - bbox2[3])
            self.select_rect = self.canvas.get_tk_widget().create_rectangle(bbox3, dash=".", outline=self.fgcol)

    ## is called whenever a mousebutton is clicked while the mouse is over the plot.
    ##  if the left button is pushed, we begin to draw a selection area
    def handle_mouse_down(self, mouseevent):
        if mouseevent.button in [1, 3]:
            self.clean_tooltip(True)
            self.mouse_pressed = (mouseevent.xdata, mouseevent.ydata)

    ## is called whenever a mouse button is released while hovering over the plot
    ## if the left button was pressed and there are points within the selection area, select those points and show a
    ##  tooltip containing information about those selected points. If not, clean up.
    def handle_mouse_up(self, mouseevent):
        if mouseevent.button in [1, 3]:
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
                    if self.param_x == self.ds.get_time_colname():
                        xmin = mdates.num2date(xmin)
                        xmax = mdates.num2date(xmax)
                    if self.param_y == self.ds.get_time_colname():
                        ymin = mdates.num2date(ymin)
                        ymax = mdates.num2date(ymax)
                    self.ds.select("ss_selected", self.param_x, xmin, xmax, "ss_show")
                    self.ds.select("ss_selected", self.param_y, ymin, ymax, "ss_selected")
                    ind = self.ds.df("ss_selected").index.values
                    if len(ind) > 0:
                        text = "Selected area from ({:.1f}; {:.1f})\n\t to ({:.1f}; {:.1f})"\
                                                        .format(xmin,ymin,xmax,ymax)
                        self.draw_tooltip(mouseevent, ind, True)
                        self.window.history.add(text)
                        # MAYBE
                        #self.trigger_update(level=self.TIMELINE_SELECTION)
                    else:
                        self.clean_tooltip(True)
                else:
                    self.clean_tooltip(True, emit=False)
                    self.ax.set_xlim((xmin, xmax), emit=False)
                    self.ax.set_ylim((ymin, ymax))
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

        if self.ds is None:
            return False, dict()

        # print("PICKER")
        # print(mouseevent, vars(mouseevent))
        if self.param_x == self.ds.get_time_colname() or self.param_y == self.ds.get_time_colname():
            return False, dict()
        xydata = self.ax.transData.transform(self.ds.df("ss_show")[[self.param_x, self.param_y]]).transpose()
        try:
            mxy = self.ax.transData.transform([mouseevent.xdata, mouseevent.ydata])
        except ValueError:
            return False, dict()
        xdata = xydata[0]
        ydata = xydata[1]
        mousex = mxy[0]
        mousey = mxy[1]
        if mouseevent.xdata is None:
            return False, dict()

        d = pd.np.sqrt((xdata - mousex) ** 2. + (ydata - mousey) ** 2.)
        ind = self.ds.df("ss_show").index.values[pd.np.nonzero(pd.np.less_equal(d, radius))[0]]

        if len(ind) > 0:
            props = dict(ind=ind)
            return True, props
        else:
            return False, dict()

    ## draws a tooltip and generates the information it contains from an event with/and a list of index values
    def draw_tooltip(self, event, ind=None, selected=False):
        if ind is None:
            ind = event.ind
            #event = event.mouseevent

        # Generate the Tooltip-String
        selstr = ""
        if selected:
            selstr = "selected "

        if len(ind) is 1:
            text = selstr + "value:"
            self.ds.select_ids("ss_selected", ind, "ss_show")
            for col, cdata in self.ds.df("ss_selected").iteritems():
                text += '\n{}: {}'.format(col, cdata[ind[0]])
        else:
            text = selstr + "%s values:" % len(ind)
            if not selected:
                self.ds.select_ids("ss_selected", ind, "ss_show")
            self.ds.aggregate("ss_sel_aggremin", "MIN", in_table="ss_selected")
            self.ds.aggregate("ss_sel_aggremax", "MAX", in_table="ss_selected")

            for col, cdata in self.ds.df("ss_sel_aggremin").iteritems():
                #text += '\n{}:\n  min:\t{}\n  max:\t{}'.format(col, cdata[0], self.ds.df("ss_sel_aggremax")[col][0])
                text += '\n{}: {} to {}'.format(col, cdata[0], self.ds.df("ss_sel_aggremax")[col][0])


        # write the tooltip
        self.tooltip.set(text)


        # # Draw the box and write the string on it
        #
        # c_height = self.canvas.figure.bbox.height
        # c_width = self.canvas.figure.bbox.width
        # y = c_height - event.y
        # x = event.x
        #
        # # get bounding box of a possible tooltip
        # self.plot_tooltip = self.canvas.get_tk_widget().create_text(x + 2, y, anchor=tk.NW, text=text)
        # bbox = self.canvas.get_tk_widget().bbox(self.plot_tooltip)
        # self.canvas.get_tk_widget().delete(self.plot_tooltip)
        #
        # # print("bbox:", bbox)
        #
        # # make sure the tooltip is within bounds
        # if bbox[2] > c_width:
        #     adj = -2
        #     if bbox[3] > c_height:
        #         anchor = tk.SE
        #     else:
        #         anchor = tk.NE
        # else:
        #     adj = 2
        #     if bbox[3] > c_height:
        #         anchor = tk.SW
        #     else:
        #         anchor = tk.NW
        # # get the new bounding box
        # if anchor is not tk.NW:  # =^= the anchor had to be modified
        #     self.plot_tooltip = self.canvas.get_tk_widget().create_text(x + adj, y, anchor=anchor, text=text)
        #     bbox = self.canvas.get_tk_widget().bbox(self.plot_tooltip)
        #     self.canvas.get_tk_widget().delete(self.plot_tooltip)
        #
        # self.plot_tooltip_rect = self.canvas.get_tk_widget().create_rectangle(bbox, fill="yellow")
        # self.plot_tooltip = self.canvas.get_tk_widget().create_text(x + adj, y, anchor=anchor, text=text)

    ## remove the tooltip if shown
    def clean_tooltip(self, with_select_rect=False, emit=True):
        self.tooltip.set("")
        if with_select_rect and self.select_rect is not None:
            self.canvas.get_tk_widget().delete(self.select_rect)
            self.select_rect = None
            #if emit:
                #self.action_str = None
                #TODO
                #self.trigger_update(self.TIMELINE_SELECTION)


    #### Handle Signals from Outside

    #the selection changed, called by SSControls
    def params_changed(self,event=None):
        self.param_x=self.settings.getX()
        self.param_y = self.settings.getY()

        self.window.history.add("scatterplot: axes changed to ({},{})".format(self.param_x, self.param_y))

        # Set Bounding Box for the plot
        #widen plot box by 2% on each side
        padding=0.02# 2%
        x_all = self.ds.get_data("ss_show").get_column(self.param_x)
        y_all = self.ds.get_data("ss_show").get_column(self.param_y)

        self.xmin = x_all.min() - padding*(x_all.max()-x_all.min())
        self.xmax = x_all.max() + padding*(x_all.max()-x_all.min())
        self.ymin = y_all.min() - padding*(y_all.max()-y_all.min())
        self.ymax = y_all.max() + padding*(y_all.max()-y_all.min())

        self.apply_settings()

    # a cluster recalculation was processed, called by VisAnaWindow.redo_plots
    def apply_settings(self, ev=None):
        if self.settings.do_white_on_black():
            self.bgcol="black"
            self.fgcol="white"
        else:
            self.fgcol="black"
            self.bgcol="white"

        self.alpha=self.settings.get_alpha()
        self.s=self.settings.get_s()
        self.should_connect = self.settings.do_connect()

        self.redraw_plot()


    def redraw_plot(self):
        self.window.status.set("Redraw Plot...")
        self.draw_plot()
        self.window.status.set("")

    # the underlying data changed, called by VisAnaWindow.openFile
    def ds_changed(self):
        olds=self.ds
        self.ds = self.window.ds


        if olds is None:
            self.settings.destroy()
            newcols = self.window.calc.get_all_columns(with_custom=False)
            self.settings = SSControls(self.sidebar, self, newcols)
            self.sidebar.add(self.settings, text="Settings")

            self.create_tooltip_frame(destroy=True)
            #self.settings.grid(column=0, row=0, sticky=(S, W, N, E))

        self.settings.set_new_cluster(0)
            #self.cluster_changed("base")

    def cluster_changed(self, in_table):
        #TODO what to do when graph not seen?
        #TODO multiple Graphs
        newcols=self.window.calc.get_all_columns(with_time=True, after_calc=True)
        self.ds.link("ss_show", in_table)

        self.settings.set_new_cols(newcols)
        #number of clusters
        if self.ds.get_data("ss_show").centroids is not None:
            k=len(self.ds.get_data("ss_show").centroids)
            self.settings.set_new_cluster(k)

        if self.param_x is None or self.param_x not in newcols or self.param_y not in newcols \
                or not self.window.options.shouldNormalize() == self.was_normalized_before:
            self.params_changed()
        else:
            self.redraw_plot()
        self.was_normalized_before = self.window.options.shouldNormalize()
        #sync settings and redraw plot
        #self.create_plot()

    ## update view with specified data
    def draw_plot(self):
        #ax.plot(self.df[self.param_x], self.df[self.param_y], marker="o", linewidth=0, picker=self.line_picker)
        self.clean_tooltip(True)
        self.ax.clear()
        self.ax.grid(True)
        #if self.param_x == self.ds.get_time_colname() or self.param_y == self.ds.get_time_colname():
        #    #self.plot=self.ax.plot(x, y,picker=self.handle_pick)#, marker="o", linewidths=0,picker=self.handle_pick)
        #    self.plot = self.ax.scatter(x=x, y=y, picker=self.handle_pick)
        #else:
        x_all = self.ds.get_data("ss_show").get_column(self.param_x)
        y_all = self.ds.get_data("ss_show").get_column(self.param_y)
        c = self.ds.get_data("ss_show").centroids


        if c is not None:
            for i in range(len(c)):
                if self.settings.clusel.draw_cluster(i):
                    d=self.ds.df("ss_show")
                    d2=d.loc[d["_cluster"] == i]
                    if self.param_x == self.ds.get_time_colname():
                        x = d2.index.values
                    else:
                        x = d2[self.param_x]
                    if self.param_y == self.ds.get_time_colname():
                        y = d2.index.values
                    else:
                        y = d2[self.param_y]
                    self.ax.scatter(x=x, y=y, marker="o",color=COLORS[i], s=self.s,
                                    alpha=self.alpha, linewidths=0, picker=self.handle_pick)
            #TOO SLOW
            # colors = self.ds.get_data("ss_show").get_column("_color")
            # self.ax.scatter(x=x_all, y=y_all, marker="o",color=colors, s=1,
            #                 alpha=0.4, linewidths=0, picker=self.handle_pick)
        else:
            self.ax.scatter(x=x_all, y=y_all, marker="o",color=self.fgcol, s=self.s, alpha=self.alpha,linewidths=0,
                                  picker=self.handle_pick)

        if self.should_connect:
            #print("HAI", type(x_all), type(y_all))

            self.ax.plot(x=list(x_all),y=list(y_all), alpha=1, linewidth=5)#, color=self.fgcol, linewidth=5, ls="solid")

        util.set_backgroundcolor(self.ax,self.bgcol)
        self.ax.grid(color=self.fgcol)
        #util.set_foregroundcolor(self.ax,fgcol)

        self.ax.set_xlabel(self.param_x)
        self.ax.set_ylabel(self.param_y)

        self.ax.set_xlim(self.xmin, self.xmax, emit=False)
        self.ax.set_ylim(self.ymin, self.ymax, emit=False)
        self.ax.callbacks.connect('xlim_changed', self.handle_changed_axes)
        self.ax.callbacks.connect('ylim_changed', self.handle_changed_axes)

        self.fig.tight_layout(pad=0)

        if self.settings.doRegr() and not (self.param_y == self.ds.get_time_colname()):
            self.draw_regression()
        self.canvas.draw()

    def draw_regression(self):
        ## we need to remove rows with NaNs first
        completedf = self.ds.df("ss_show")
        completedf = completedf[pd.notnull(completedf[self.param_x])]
        completedf = completedf[pd.notnull(completedf[self.param_y])]
        if self.param_x == self.ds.get_time_colname():
            completedf["delta_time"] = (completedf[self.ds.get_time_colname()] - completedf[self.ds.get_time_colname()].min()) / np.timedelta64(1, "m")
            X = completedf["delta_time"].to_frame()
        else:
            X = completedf[self.param_x].to_frame()
        y = completedf[self.param_y].to_frame()

        lr = LinearRegression()
        lr.fit(X,y)
        print(lr.coef_)
        if self.param_x == self.ds.get_time_colname():
            self.ax.plot(completedf[self.ds.get_time_colname()], lr.predict(X), color="red")
        else:
            self.ax.plot(X, lr.predict(X), color="red")

    def has_selection(self)->bool:
        return self.select_rect is not None

    def create_tooltip_frame(self, destroy):
        if destroy:
            self.tframe.destroy()

        self.tframe = Frame(self.sidebar)
        self.sidebar.add(self.tframe, text="Details")
        #self.tframe.grid(column=0, row=0, sticky=(S,W,N,E))
        self.tframe.rowconfigure(0,weight=1)
        self.tframe.columnconfigure(0,weight=1)
        self.tooltip = StringVar(self.tframe)
        self.tlabel=Label(self.tframe, textvariable=self.tooltip, justify="left", anchor="nw", wraplength=200)
        font = Font(font=self.tlabel['font'])
        font["size"] = 7
        self.tlabel["font"]=font
        self.tlabel.grid(column=0, row=0, sticky=(W, N))



class SSControls(Frame):
    def __init__(self, parent,plot, params, k=1):
        super(SSControls, self).__init__(parent)#,text="Scatterplot-Options")
        self.params=params
        self.plot=plot #type:SimpleScatter
        self.k=k
        self.clusel=Label(self)

        if params is None:
            Label(self,text="No data, please open a file via File -> Open").grid(row=0, column=0)
            return

        apply_changes=self.plot.apply_settings

        param1lbl = Label(self, text="X-Axis:")
        param1lbl.grid(column=0, row=1, sticky=(N, E, W))
        self.param1var = StringVar()
        self.param1var.set(params[1])
        self.param1box=Combobox(self, textvariable=self.param1var, state="readonly")
        self.param1box['values'] = self.params
        self.param1box.bind('<<ComboboxSelected>>', self.plot.params_changed)
        self.param1box.grid(column=1, row=1, sticky=(N, E, W))


        param2lbl = Label(self, text="Y-Axis:")
        param2lbl.grid(column=0, row=2, sticky=(N, E, W))
        self.param2var = StringVar()
        self.param2var.set(params[2])
        self.param2box = Combobox(self, textvariable=self.param2var, state="readonly")
        self.param2box['values'] = self.params
        self.param2box.bind('<<ComboboxSelected>>', self.plot.params_changed)
        self.param2box.grid(column=1, row=2, sticky=(N, E, W))

        #Regression
        self.rgvar = StringVar(value="0")
        self.regression = Checkbutton(self, text='Draw Regression', command=apply_changes,
                                         variable=self.rgvar)
        self.regression.grid(column=0, row=3, sticky=(W, N), columnspan=2)

        #background
        self.wbvar = StringVar(value="0")
        self.whibla = Checkbutton(self, text='Black Background', command=apply_changes,
                                         variable=self.wbvar)
        self.whibla.grid(column=0, row=4, sticky=(W, N), columnspan=2)

        #connect by line
        self.connvar = StringVar(value="1")
        self.conncb = Checkbutton(self, text='Connect following points', command=apply_changes,
                                         variable=self.connvar)
        #self.conncb.grid(column=0, row=5, sticky=(W, N), columnspan=2)

        #Dot settings
        frm = Frame(self)
        frm.grid(column=0, row=6, sticky=(W, N, E), columnspan=2)
        frm.columnconfigure(2,weight=1)
        Label(frm,text="alpha:").grid(column=0, row=0, sticky=(N, E))
        Label(frm,text="dotsize:").grid(column=3, row=0, sticky=(N, E))

        self.alpha=StringVar(self,value="0.2")
        self.s=StringVar(self,value="4")

        Spinbox(frm,from_=0.05, to=1, increment=0.05, command=apply_changes, textvariable=self.alpha,width=4)\
            .grid(column=1, row=0, sticky=(W, E))
        Spinbox(frm,from_=0.5, to=20, increment=0.5 , command=apply_changes, textvariable=self.s,width=4)\
            .grid(column=4, row=0, sticky=(W, E))




        Button(frm,text="Apply & Reset View", command=self.plot.params_changed)\
            .grid(column=0, row=1, sticky=(N, E,W), columnspan=5)

    def set_new_cols(self, newcols):
        self.params=newcols
        x= self.param1var.get()
        y= self.param2var.get()
        self.param1box['values'] = newcols
        self.param2box['values'] = newcols
        if not x in newcols:
            self.param1var.set(newcols[0])
        if not y in newcols:
            self.param2var.set(newcols[1])

    def set_new_cluster(self, k):
        if self.k == k or (self.k<=1 and k<=1):
            return
        self.clusel.destroy()
        self.clusel=ClusterSelect(self,self.plot,k)
        self.clusel.grid(column=0, row=8, sticky=(N, E,W), columnspan=2)

    def getX(self):
        return self.param1var.get()

    def getY(self):
        return self.param2var.get()

    def doRegr(self):
        return self.rgvar.get() is not "0"

    def do_white_on_black(self):
        return self.wbvar.get() is not "0"

    def do_connect(self):
        return self.connvar.get() is not "0"

    def get_alpha(self):
        return float(self.alpha.get())

    def get_s(self):
        return float(self.s.get())


class ClusterSelect(LabelFrame):
    def __init__(self, parent, plot, k):
        super(ClusterSelect, self).__init__(parent)#,text="Scatterplot-Options")
        self.plot=plot #type:SimpleScatter
        self.ds=plot.ds
        apply = plot.apply_settings

        self.cvars=[]

        for i in range(k):
            cv = StringVar(self,value="1")
            cb = Checkbutton(self,text="Cluster "+str(i), variable=cv, command=apply)
            cb.grid(column=0, row=i, sticky=(N, E,W), columnspan=1)
            self.cvars.append(cv)






    def draw_cluster(self,i):
        return self.cvars[i].get() == "1"


