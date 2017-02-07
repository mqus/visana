from tkinter import Frame, Label, StringVar, N, E, W, S, Spinbox
from tkinter.ttk import Combobox, LabelFrame, Checkbutton, Button, Notebook

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import pandas as pd
from sklearn.linear_model import LinearRegression

import util
from SimpleScatter import ClusterSelect
from datasource import DataSource, COLORS


#from v2.Window import VisAnaWindow



class MultiScatter(Frame):
    def __init__(self,parent,master):
        super(MultiScatter,self).__init__(parent)
        self.window=master #type:VisAnaWindow
        self.parent=parent

        self.param_y=None;self.param_x=None

        self.ds=self.window.ds #type:DataSource

        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)

        # self.sidebar=Notebook(self)
        # self.sidebar.grid(column=0, row=0, sticky=(S,W,N,E))
        #
        #
        # self.tframe = Frame(self.sidebar)
        # self.sidebar.add(self.tframe, text="Tooltip")
        # self.tframe.grid(column=0, row=0, sticky=(S,W,N,E))
        # self.tframe.rowconfigure(0,weight=1)
        # self.tframe.columnconfigure(0,weight=1)
        # self.tooltip = StringVar(self.tframe)
        # self.tlabel=Label(self.tframe, textvariable=self.tooltip, justify="left", anchor="nw", wraplength=200)
        # self.tlabel.grid(column=0, row=0, sticky=(W, N))


        self.select_rect=None
        #MAYBE: retain plot view when switching regression on/off
        #self.plotbox=(None,None,None,None)

        if self.ds is None:
            self.settings=Label(self,text="No data, please open a file via File -> Open")
            #self.settings.grid(column=1, row=0, sticky=(S,W,N,E))
            return

        self.settings=MSControls(self, self,self.ds.base().get_attr_names())
        # self.sidebar.add(self.settings, text="Settings")
        self.settings.grid(column=0, row=0, sticky=(S,W,N,E))


    #### Handle Graph signals

    ###################
    # PLOT-EVENT HANDLER

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
        #self.tooltip.set("")
        if with_select_rect and self.select_rect is not None:
            self.canvas.get_tk_widget().delete(self.select_rect)
            self.select_rect = None
            #if emit:
                #self.action_str = None
                #TODO
                #self.trigger_update(self.TIMELINE_SELECTION)


    #### Handle Signals from Outside

    def apply_settings(self, ev=None):
        #TODO get new params for graph
        if self.settings.do_white_on_black():
            self.bgcol="black"
            self.fgcol="white"
        else:
            self.fgcol="black"
            self.bgcol="white"

        self.alpha=self.settings.get_alpha()
        self.s=self.settings.get_s()

        self.redraw_plot()


    def redraw_plot(self):
        self.window.status.set("Redraw Small Multiples...")
        self.draw_plot()
        self.window.status.set("")



    # the underlying data changed, called by VisAnaWindow.openFile
    def ds_changed(self):
        olds=self.ds
        self.ds = self.window.ds
        if olds is None:
            self.settings.destroy()
            newcols = self.window.calc.get_all_columns(with_time=True)
            self.settings = MSControls(self, self, newcols)
            #self.sidebar.add(self.settings, text="Settings")
            self.settings.grid(column=0, row=0, sticky=(S, W, N, E))


            #self.cluster_changed("base")

    def cluster_changed(self, in_table):
        #TODO what to do when graph not seen?
        #TODO multiple Graphs
        newcols=self.window.calc.get_all_columns(with_time=True)
        self.ds.link("ss_show", in_table)

        self.settings.set_new_cols(newcols)
        #number of clusters
        if self.ds.get_data("ss_show").centroids is not None:
            k=len(self.ds.get_data("ss_show").centroids)
            self.settings.set_new_cluster(k)

        #if self.param_x is None or self.param_x not in newcols or self.param_y not in newcols:
        #    self.params_changed()
        #else:
        self.apply_settings()

        #sync settings and redraw plot
        #self.create_plot()

    ## update view with specified data
    def draw_plot(self):
        self.clean_tooltip(True)
        self.fig = Figure(figsize=(5, 5), dpi=100) #type:Figure

        tabl = self.ds.get_data("cluster")
        d = tabl.df()
        if tabl.centroids is not None:
            k=len(tabl.centroids)
            cluster_params=self.window.calc.cluster_params

            param_combos = []
            subplot_num = 0
            paraLen = min(len(cluster_params),6)
            axarr = [[]]
            dummy = [[]]
            sharey = {}

            for qi in range(0, paraLen):
                q = cluster_params[qi]
                #subplot_num = ((subplot_num%10)*10)+111
                #print("subplot_num=",str(subplot_num))
                for pi in range(0, paraLen):
                    #print("qi =",str(qi))
                    p = cluster_params[pi]
                    #subplot_num += 1
                    if pi < qi:#not p == q:
                        subplot_num = (qi-1)*(paraLen-1) + (pi+1)
                        #print(subplot_num)
                        #print("\tsubplot_num=",str(subplot_num))
                        param_combos.append((p,q))
                        x = d[p]
                        y = d[q]
                        #print("pi=",str(pi),"qi=",str(qi))
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
                        for i in range(k):
                            if self.settings.clusel.draw_cluster(i):
                                one_value_cluster = d.loc[d['_cluster'] == i]
                                ax1.scatter(one_value_cluster[cluster_params[pi]], one_value_cluster[cluster_params[qi]],
                                            color=COLORS[i], marker=".", alpha=self.alpha, s=self.s)
                            #print("i:",str(i),"pi:",str(pi),"qi:",str(qi))
                            ax1.plot(tabl.centroids[i][pi],tabl.centroids[i][qi],'kx')

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
                        util.set_backgroundcolor(ax1, self.bgcol)
                        ax1.grid(True, color=self.fgcol)
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

        self.canvas.get_tk_widget().grid(column=1, row=0, sticky=(N, E, W, S), rowspan=2)

        # self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.canvas.get_tk_widget())
        #self.ctbwidget=tk.Frame(self)
        #self.ctbwidget.grid(column=1, row=4, sticky=(tk.N, tk.E, tk.W, tk.S))
        #self.canvas_tb = NavigationToolbar2TkAgg(self.canvas, self.ctbwidget)
        if tabl.centroids is not None:
            self.fig.tight_layout(pad=0)
        # util.zoom_factory(self.ax)

        self.canvas.draw()



class MSControls(Frame):
    def __init__(self, parent,plot, params, k=1):
        super(MSControls, self).__init__(parent)#,text="Scatterplot-Options")
        self.params=params
        self.plot=plot #type:SimpleScatter
        self.k=k
        self.clusel=Label(self)


        apply_changes=self.plot.apply_settings


        #background
        self.wbvar = StringVar(value="0")
        self.whibla = Checkbutton(self, text='Black Background', command=apply_changes,
                                         variable=self.wbvar)
        self.whibla.grid(column=0, row=4, sticky=(W, N), columnspan=2)

        #Dot settings
        frm = Frame(self)
        frm.grid(column=0, row=5, sticky=(W, N, E), columnspan=2)
        frm.columnconfigure(2,weight=1)
        Label(frm,text="alpha:").grid(column=0, row=0, sticky=(N, E))
        Label(frm,text="dotsize:").grid(column=3, row=0, sticky=(N, E))

        self.alpha=StringVar(self,value="0.2")
        self.s=StringVar(self,value="4")

        Spinbox(frm,from_=0.05, to=1, increment=0.05, command=apply_changes, textvariable=self.alpha,width=4)\
            .grid(column=1, row=0, sticky=(W, E))
        Spinbox(frm,from_=0.5, to=20, increment=0.5 , command=apply_changes, textvariable=self.s,width=4)\
            .grid(column=4, row=0, sticky=(W, E))




        Button(frm,text="Apply", command=apply_changes)\
            .grid(column=0, row=1, sticky=(N, E,W), columnspan=5)

    def set_new_cols(self, newcols):
        self.params=newcols

    def set_new_cluster(self, k):
        if self.k == k or (self.k<=1 and k<=1):
            return
        self.clusel.destroy()
        self.clusel=ClusterSelect(self,self.plot,k)
        self.clusel.grid(column=0, row=6, sticky=(N, E,W), columnspan=2)

    def do_white_on_black(self):
        return self.wbvar.get() is not "0"

    def get_alpha(self):
        return float(self.alpha.get())

    def get_s(self):
        return float(self.s.get())

    def get_cols(self):
        pass


