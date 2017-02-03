import tkinter as tk
from tkinter import filedialog
from tkinter import Scale, HORIZONTAL, Listbox, Spinbox, StringVar

import datasource
import  tkinter.ttk as ttk

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
        self.rowconfigure(2,minsize=100)
        self.createMenu()

        #self.createTimeline()
        self.drawParts()

        ##MUSSWEG TODO
        self.openFile("../../data/dust-2014-v2.dat")

    def createMenu(self):
        #win = tk.Toplevel(root)
        menubar = tk.Menu(self.master)
        self.master['menu'] = menubar
        menu_file = tk.Menu(menubar,tearoff=False)
        menu_edit = tk.Menu(menubar,tearoff=False)
        menubar.add_cascade(menu=menu_file, label='File')
        #menubar.add_cascade(menu=menu_edit, label='Edit')

        #menu_file.add_command(label='New', command=newFile)
        menu_file.add_command(label='Open...', command=self.openFile)
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

        #add history
        self.history = HistoryView(self.sidepane_r)
        self.sidepane_r.add(self.history,text="History")

        #add clustering options
        self.options = Options(self.sidepane_r,self)
        self.sidepane_r.add(self.options, text="Options")

        self.scatter = SimpleScatter(self.graphs, self)
        self.graphs.add(self.scatter, text="ScatterPlot")


    def redrawParts(self):
        if not self.timeline is None:
            self.timeline.destroy()
        if not self.graphs is None:
            self.graphs.destroy()
        if not self.sidepane_r is None:
            self.sidepane_r.destroy()
        #TODO draw

    def openFile(self, filename=None):
        if filename is None:
            filename = tk.filedialog.askopenfile("r")
            if filename is None:
                return
        self.ds = datasource.DataSource()
        self.ds.read_data(filename)

        self.options.ds_changed()
        self.scatter.ds_changed()






root = tk.Tk()

app = VisAnaWindow(master=root)
app.mainloop()

