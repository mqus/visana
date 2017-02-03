from tkinter import Frame, Label, StringVar, N, E, W, S
from tkinter.ttk import Combobox, LabelFrame

from datasource import DataSource
#from v2.Window import VisAnaWindow


class SimpleScatter(Frame):
    def __init__(self,parent,master):
        super(SimpleScatter,self).__init__(parent)
        self.window=master #type:VisAnaWindow
        self.parent=parent

        self.ds=self.window.ds #type:DataSource

        self.columnconfigure(1,weight=1)
        self.rowconfigure(1,weight=1)

        self.tframe = LabelFrame(self, text="Tooltip")
        self.tframe.grid(column=0, row=1, sticky=(S,W,N,E))
        self.tframe.rowconfigure(0,weight=1)
        self.tframe.columnconfigure(0,weight=1)
        self.tooltip=Label(self.tframe , text="EinTooltip")
        self.tooltip.grid(column=0, row=0, sticky=(S,W,N,E))

        if self.ds is None:
            self.settings=Label(self,text="No data, please open a file via File -> Open")
            self.settings.grid(column=1, row=1, sticky=(S,W,N,E))
            return

        self.settings=SSControls(self,self.ds.base().get_attr_names())
        self.settings.grid(column=0, row=0, sticky=(S,W,N,E))


    #the selection changed, called by SSControls
    def params_changed(self):
        print("didIt!",self.settings.getX(), self.settings.getY())

    # the underlying data changed, called by VisAnaWindow.openFile
    def ds_changed(self):
        self.ds = self.window.ds
        self.settings.destroy()
        self.settings=SSControls(self,self.ds.base().get_attr_names())
        self.settings.grid(column=0, row=0, sticky=(S,W,N,E))




class SSControls(LabelFrame):
    def __init__(self, parent, params):
        super(SSControls, self).__init__(parent,text="Scatterplot-Options")
        self.params=params
        self.parent=parent #type:SimpleScatter


        self.param1lbl = Label(self, text="X-Axis:")
        self.param1lbl.grid(column=0, row=1, sticky=(N, E, W))
        self.param1var = StringVar()
        self.param1var.set(params[1])
        self.param1box=Combobox(self, textvariable=self.param1var, state="readonly")
        self.param1box['values'] = self.params
        self.param1box.bind('<<ComboboxSelected>>', self.parent.params_changed)
        self.param1box.grid(column=1, row=1, sticky=(N, E, W))


        self.param1lbl = Label(self, text="Y-Axis:")
        self.param1lbl.grid(column=0, row=2, sticky=(N, E, W))
        self.param2var = StringVar()
        self.param2var.set(params[1])
        self.param2box = Combobox(self, textvariable=self.param2var, state="readonly")
        self.param2box['values'] = self.params
        self.param2box.bind('<<ComboboxSelected>>', self.parent.params_changed)
        self.param2box.grid(column=1, row=2, sticky=(N, E, W))

    def getX(self):
        return self.param1var.get()

    def getY(self):
        return self.param2var.get()



