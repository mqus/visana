import tkinter as tk
from tkinter import filedialog
from tkinter import Scale, HORIZONTAL, Listbox, Spinbox, StringVar

import datasource
import  tkinter.ttk as ttk

from v2.CustomClasses import CustomClasses
from v2.DataTasks import Calculator, ALL
from v2.History import HistoryView
from v2.Options import Options
from v2.SimpleScatter import SimpleScatter
from v2.Timeline import Timeline


class VisAnaWindow(tk.Frame):
    timeline=None
    graphs=None


    def __init__(self, master,ds=None):
        super(VisAnaWindow, self).__init__( master)
        self.master=master
        self.ds=ds#TODO
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        root.title("Visual Analyser - Gui")

        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1,weight=1)
        #self.rowconfigure(2,minsize=20)
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
        self.timeline=Timeline(self)
        self.timeline.grid(column=0,row=0,columnspan=2, sticky=(tk.N,tk.W,tk.E))

        #draw Graph Multiview
        self.graphs=ttk.Notebook(self)
        self.graphs.grid(column=0, row=1, sticky=(tk.N,tk.W,tk.E,tk.S))

        #draw history/clusteroptions multiview
        self.sidepane_r=ttk.Notebook(self)
        self.sidepane_r.grid(column=1, row=1, sticky=(tk.N,tk.E,tk.S))

        #add clustering options
        self.options = Options(self.sidepane_r,self)
        self.sidepane_r.add(self.options, text="Options")

        #add history
        self.history = HistoryView(self.sidepane_r)
        self.sidepane_r.add(self.history,text="History")

        #add custom classes

        self.customclasses= CustomClasses(self.sidepane_r, self)
        self.sidepane_r.add(self.customclasses, text="Custom Grain Classes")

        self.scatter = SimpleScatter(self.graphs, self)
        self.graphs.add(self.scatter, text="ScatterPlot")

        self.status=StringVar(self)
        slbl=ttk.Label(self,textvariable=self.status, justify="left")
        slbl.grid(column=0, row=2, columnspan=2, sticky=(tk.E,tk.W,tk.S))


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

        self.customclasses.destroy()
        self.customclasses= CustomClasses(self.sidepane_r, self)
        self.sidepane_r.add(self.customclasses, text="Custom Grain Classes")

        self.calc.recalc(ALL)

    def redo_plots(self):
        #TODO
        self.scatter.cluster_changed("cluster")





root = tk.Tk()

app = VisAnaWindow(master=root)
app.mainloop()

