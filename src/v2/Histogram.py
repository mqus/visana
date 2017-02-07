from tkinter import Frame, Label, StringVar, N, E, W, S, Spinbox
from tkinter.ttk import Combobox, LabelFrame, Checkbutton, Button

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
from sklearn.linear_model import LinearRegression

import util
from datasource import DataSource, COLORS


#from v2.Window import VisAnaWindow



class Histogram(Frame):
    def __init__(self,parent,master):
        super(Histogram,self).__init__(parent)
        self.window=master #type:VisAnaWindow
        self.parent=parent

        self.param_y=None;self.param_x=None

        self.ds=self.window.ds #type:DataSource

        self.columnconfigure(1,weight=1)
        self.rowconfigure(1,weight=1)

        self.tframe = LabelFrame(self, text="Tooltip")
        #self.tframe.grid(column=0, row=1, sticky=(S,W,N,E))
        self.tframe.rowconfigure(0,weight=1)
        self.tframe.columnconfigure(0,weight=1)
        self.tooltip = StringVar(self.tframe)
        self.tlabel=Label(self.tframe, textvariable=self.tooltip, justify="left", anchor="nw", wraplength=200)
        self.tlabel.grid(column=0, row=0, sticky=(W, N))

        #self.create_plot()

        self.select_rect=None
        #MAYBE: retain plot view when switching regression on/off
        #self.plotbox=(None,None,None,None)

        if self.ds is None:
            self.settings=Label(self,text="No data, please open a file via File -> Open")
            self.settings.grid(column=1, row=1, sticky=(S,W,N,E))
            return

        self.settings=HControls(self,self.ds.base().get_attr_names())
        self.settings.grid(column=0, row=0, sticky=(S,W,N,E))
        self.apply_settings()




    # def create_plot(self):
    #     self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure
    #     self.ax = self.fig.add_subplot(111) #type:Axes
    #     #self.ax2 = self.fig.add_subplot(212)
    #
    #     self.canvas = FigureCanvasTkAgg(self.fig, self) #type:FigureCanvasTkAgg
    #
    #     #self.canvas.mpl_connect('motion_notify_event', self.handle_hover)
    #     # self.canvas.mpl_connect('button_press_event', self.handle_mouse_down)
    #     # self.canvas.mpl_connect('button_release_event', self.handle_mouse_up)
    #     # #self.canvas.mpl_connect('pick_event', self.draw_tooltip)
    #
    #     self.canvas.get_tk_widget().grid(column=1, row=0, sticky=(N, E, W, S), rowspan=2)
    #
    #     # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
    #     #self.ctbwidget=tk.Frame(self)
    #     #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
    #     #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)
    #
    #     #self.ax.callbacks.connect('xlim_changed', self.handle_changed_axes)
    #     #self.ax.callbacks.connect('ylim_changed', self.handle_changed_axes)
    #
    #     #util.zoom_factory(self.ax)


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
                        #TODO
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

    def apply_settings(self, ev=None):
        self.lgvar = self.settings.doLog()

        self.redraw_plot()


    def redraw_plot(self):
        self.window.status.set("Redraw Histogram...")
        self.draw_plot()
        self.window.status.set("")



    # the underlying data changed, called by VisAnaWindow.openFile
    def ds_changed(self):
        olds=self.ds
        self.ds = self.window.ds
        if olds is None:
            self.settings.destroy()
            newcols = self.window.calc.get_all_columns(with_time=True, with_custom=False)
            self.settings = HControls(self, newcols)
            self.settings.grid(column=0, row=0, sticky=(S, W, N, E))


    def cluster_changed(self, in_table):
        #TODO what to do when graph not seen?
        #TODO multiple Graphs
        newcols=self.window.calc.get_all_columns(with_time=True, after_calc=True)
        #self.settings.set_new_cols(newcols)

        self.ds.link("ss_show", in_table)

        self.apply_settings()

        #sync settings and redraw plot
        #self.create_plot()



    def draw_plot(self):
        self.clean_tooltip(True)

        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure
        self.ax = self.fig.add_subplot(111) #type:Axes

        self.ax.clear()
        self.ax.grid(True)
        tabl = self.ds.get_data("cluster")
        d = tabl.df()
        if tabl.centroids is not None:

            k=len(tabl.centroids)
            cluster_params=self.window.calc.cluster_params
            print("hist ", cluster_params)

            # subplot_num = 0
            # print(self.centroids)
            y_pos = pd.np.arange(len(cluster_params))
            # print(y_pos)
            width = 0.95 / k
            # colors = ["#d62728", "blue", "green", "brown"]
            max_y_val = 0
            for c in range(0, k):
                # subplot_num += 1
                ystdev = []
                one_value_cluster = d.loc[d['_cluster'] == c]

                # for i in range(0, len(datasource.GRAIN_COLS)):
                for i in range(0, len(cluster_params)):
                    col = one_value_cluster[cluster_params[i]]
                    stdev = pd.np.std(col)
                    ystdev.append(stdev)

                cen = [tabl.centroids[c][i] for i in range(0, len(cluster_params))]
                ## cluster label for legend
                c_label = "Cluster " + str(c)
                self.ax.bar(y_pos + width * (c - (k / 2.3)), cen, width, align="center", log=self.lgvar,#alpha=0.75,
                            color=COLORS[c], ecolor="black", yerr=ystdev, label=c_label)
                for i in range(0, len(cen)):
                    y_val = cen[i] + ystdev[i]
                    #print("y_val:",str(y_val))
                    if y_val > max_y_val:
                        max_y_val = y_val
                        #print("new max_y_val:",str(max_y_val))


                #print("cen:",str(cen))
                #print("ysdtev:",str(ystdev))
                #print("ypos:",str(y_pos))

            self.ax.grid(True)
            # self.ax.set_xticklabels
            # self.ax.set_ylim(0, 1, emit=False)
            #max_y_val = max(map(max, tabl.centroids))
            self.ax.set_ylim(0, max_y_val * 1.05, emit=False)

            self.ax.set_xticks(y_pos + width / 4)
            self.ax.set_xticklabels(cluster_params)

    #        self.ax.callbacks.connect('xlim_changed', self.handle_view_change)
    #        self.ax.callbacks.connect('ylim_changed', self.handle_view_change)

            ## add legend
            self.ax.legend(loc="upper right", shadow=True)
        else:
            cluster_params = [col for col in self.window.calc.get_all_columns(after_calc=True) if col not in ["OutdoorTemp",
                                                                                               "RelHumidity","Daytime"]]
            print("hist ", cluster_params)

            # subplot_num = 0
            # print(self.centroids)
            y_pos = pd.np.arange(len(cluster_params))
            # print(y_pos)
            width = 0.95 / 1
            # colors = ["#d62728", "blue", "green", "brown"]
            # subplot_num += 1
            ystdev = []
            one_value_cluster = d

            # for i in range(0, len(datasource.GRAIN_COLS)):
            for i in range(0, len(cluster_params)):
                col = one_value_cluster[cluster_params[i]]
                stdev = pd.np.std(col)
                ystdev.append(stdev)

            cen = d[cluster_params].mean(axis=0)
            print(type(cen),type(cen.max()),cen.max())
            ## cluster label for legend
            self.ax.bar(y_pos + width * (0 - (1 / 2.3)), cen, width, align="center", log=self.lgvar,  # alpha=0.75,
                        color="blue", ecolor="black", yerr=ystdev)
            self.ax.grid(True)
            # self.ax.set_xticklabels
            # self.ax.set_ylim(0, 1, emit=False)
            max_y_val = cen.max()
            self.ax.set_ylim(0, max_y_val * 1.1, emit=False)

            self.ax.set_xticks(y_pos + width / 4)
            self.ax.set_xticklabels(cluster_params)

            #        self.ax.callbacks.connect('xlim_changed', self.handle_view_change)
            #        self.ax.callbacks.connect('ylim_changed', self.handle_view_change)

            ## add legend
#            self.ax.legend(loc="upper right", shadow=True)

        self.canvas = FigureCanvasTkAgg(self.fig, self) #type:FigureCanvasTkAgg

        self.canvas.get_tk_widget().grid(column=1, row=0, sticky=(N, E, W, S), rowspan=2)




class HControls(LabelFrame):
    def __init__(self, parent, params):
        super(HControls, self).__init__(parent,text="Histogram-Options")
        self.params=params
        self.parent=parent #type:SimpleScatter



        apply_changes=self.parent.apply_settings

        #logarithmic scale
        self.lgvar = StringVar(value="0")
        self.log_cb = Checkbutton(self, text='logarithmic scale', command=apply_changes,
                                         variable=self.lgvar)
        self.log_cb.grid(column=0, row=1, sticky=(W, N), columnspan=2)


    def doLog(self):
        return self.lgvar.get() is not "0"


