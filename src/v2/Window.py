import tkinter as tk
from tkinter import filedialog
from tkinter import Scale, HORIZONTAL, Listbox, Spinbox, StringVar

import datasource
import  tkinter.ttk as ttk

from CustomClasses import CustomClasses
from DataTasks import ALL, Calculator
from Histogram import Histogram
from History import HistoryView
from MultiScatter import MultiScatter
from Options import Options
from SimpleScatter import SimpleScatter
from Timeline import Timeline


class VisAnaWindow(tk.Frame):
    timeline=None
    graphs=None


    def __init__(self, master,ds=None):
        super(VisAnaWindow, self).__init__( master)
        self.master=master
        self.ds=ds#TODO
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.title("Visual Analyser - PROTOTYP")

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1,weight=1)
        #self.rowconfigure(0,maxsize=100)
        self.createMenu()

        #self.createTimeline()
        self.drawParts()

        self.calc = Calculator(self)


        ##MUSSWEG TODO
        self.open_file("../../data/dust-32-grain-size-classes-2014.dat")



    def createMenu(self):
        #win = tk.Toplevel(root)
        menubar = tk.Menu(self.master)
        self.master['menu'] = menubar
        menu_file = tk.Menu(menubar,tearoff=False)
        menu_edit = tk.Menu(menubar,tearoff=False)
        menubar.add_cascade(menu=menu_file, label='File')
        #menubar.add_cascade(menu=menu_edit, label='Edit')

        #menu_file.add_command(label='New', command=newFile)
        menu_file.add_command(label='Open...', command=self.open_file)
        menu_file.add_command(label='Quit', command=root.destroy)
        #menu_file.add_command(label='Close', command=closeFile)


    def drawParts(self):
        # draw Timeline
        self.timeline= Timeline(self)
        self.timeline.grid(column=0,row=0,columnspan=2, sticky=(tk.N,tk.W,tk.E))

        #draw Graph Multiview
        self.graphs=ttk.Notebook(self)
        self.graphs.grid(column=0, row=1, sticky=(tk.N,tk.W,tk.E,tk.S))

        #draw history/clusteroptions multiview
        self.sidepane_r=ttk.Notebook(self)
        self.sidepane_r.grid(column=1, row=1, sticky=(tk.N,tk.E,tk.S))
        self.sidepane_r.bind("<Configure>", print)

        #add clustering options
        self.options = Options(self.sidepane_r, self)
        self.sidepane_r.add(self.options, text="Options")

        #add history
        self.history = HistoryView(self.sidepane_r)
        self.sidepane_r.add(self.history,text="History")

        #add custom classes
        self.customclasses= CustomClasses(self.sidepane_r, self)
        self.sidepane_r.add(self.customclasses, text="Custom Grain Classes")

        #simple Scatterplot
        self.scatter = SimpleScatter(self.graphs, self)
        self.graphs.add(self.scatter, text="ScatterPlot")

        #add Histogram
        self.hist = Histogram(self.graphs, self)
        self.graphs.add(self.hist, text="Histogram")

        #add Multiscatter
        self.mscatter = MultiScatter(self.graphs, self)
        self.graphs.add(self.mscatter, text="Small Multiples - Scatterplot")

        self.status=StringVar(self)
        ttk.Label(self,textvariable=self.status, justify="left")\
            .grid(column=0, row=2, columnspan=2, sticky=(tk.E,tk.W,tk.S))


    # def redraw_parts(self):
    #     if not self.timeline is None:
    #         self.timeline.destroy()
    #     if not self.graphs is None:
    #         self.graphs.destroy()
    #     if not self.sidepane_r is None:
    #         self.sidepane_r.destroy()
    #     #TODO draw

    def open_file(self, filename=None):
        if filename is None:
            filename = tk.filedialog.askopenfile("r")
            if filename is None:
                return
        self.ds = datasource.DataSource()
        self.ds.read_data(filename)

        self.calc.ds_changed()

        self.options.ds_changed()
        self.scatter.ds_changed()
        self.hist.ds_changed()
        self.mscatter.ds_changed()

        self.customclasses.destroy()
        self.customclasses= CustomClasses(self.sidepane_r, self)
        self.sidepane_r.add(self.customclasses, text="Custom Grain Classes")
        self.calc.cclasses_changed(dict())

        self.calc.recalc(ALL)

    def redo_plots(self):
        #TODO
        self.timeline.create_timeline()
        self.scatter.cluster_changed("cluster")
        self.hist.cluster_changed("cluster")
        self.mscatter.cluster_changed("cluster")





root = tk.Tk()

app = VisAnaWindow(master=root)
app.mainloop()

