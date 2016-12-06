import tkinter as tk
import datasource
## matplotlibs
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt




class VisAnaGUI(tk.LabelFrame):
    def __init__(self, master=None, ds=None):
        tk.LabelFrame.__init__(self, master, bg="#ff6600")
        #self.pack()
        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3,weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.plot_tooltip=None
        self.createWidgets()
        root.title("Visual Analyser - Gui")


    def createWidgets(self):
        self.toolbar=tk.LabelFrame(self)
        self.toolbar.grid(column=0, row=0, sticky=(tk.W, tk.N, tk.E), columnspan=5)

        self.QUIT = tk.Button(self.toolbar, text="QUIT", fg="red",
                              command=root.destroy)
        self.QUIT.grid(column=0, row=0, sticky=(tk.W, tk.N))

        self.hi_there = tk.Button(self.toolbar)
        self.hi_there["text"] = "Hello World\\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.grid(column=1, row=0, sticky=(tk.W, tk.N))

        self.filter = tk.LabelFrame(self, bg="#0066ff")
        self.filter.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)
        self.f1 = tk.Label(self.filter, text="HIER STEHT Dann EIN FILTER!!!")
        self.f1.pack()


        self.timeline = tk.Label(self, text="HIER STEHT NE TIMELINE!!!", bg="#0066ff")
        self.timeline.grid(column=0, row=2, sticky=(tk.N, tk.E, tk.W),columnspan=5)

        self.projector = tk.Label(self, text="HIER KANN MAN\n EIGENSCHAFTEN\n AUSWAEHLEN\n\n\nbis hier")
        self.projector.grid(column=0, row=3, sticky=(tk.N, tk.E, tk.W))

        self.history = tk.Text(self, width=50)
        self.history.grid(column=2, row=3, sticky=(tk.N, tk.E, tk.S))
        for i in range(1,101):
            self.add_to_history('Line %d of 100' % i)
        self.history["state"]="disabled"
        #self.history.insert('end', "Das hier ist mal passiert!!!!\n")
        
        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=3, row=3, sticky=(tk.N, tk.S))
        self.history['yscrollcommand'] = self.historyslider.set

        #for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
    def say_hi(self):
        print("hi there, everyone!")

    def add_to_history(self, text):
        self.history.insert('end', text + "\n")




    ## update view with specified data
    def display_data(self, df, attr_name1="Large", attr_name2="Small"):
        fig = Figure(figsize=(5,5), dpi=100)
        ax = fig.add_subplot(111)
        #df.plot.scatter(x=attr_name1, y=attr_name2, ax=ax, grid=True, picker=True)
        ax.plot(df[attr_name1], df[attr_name2], marker="o", linewidth=0, picker=True)#, grid=True)
        ax.grid(True)
        #df.plot(x="MasterTime", y="Large", ax=ax)

        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.mpl_connect('button_press_event', lambda event: self.canvas._tkcanvas.focus_set())
        self.canvas.mpl_connect('pick_event', self.draw_tooltip)
        #self.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.get_tk_widget().grid(column=1, row=3, sticky=(tk.N, tk.E, tk.W, tk.S))
    def draw_tooltip(self, event):
        if self.plot_tooltip is not None:
            self.canvas.get_tk_widget().delete(self.plot_tooltip)
            self.canvas.get_tk_widget().delete(self.plot_tooltip_rect)
        print("dasEvent: "+ str(vars(event)))
        print("ind: "+ str(event.ind))
        print("artist: "+ str(vars(event.artist)))
        print("me: "+ str(vars(event.mouseevent)))
        y=self.canvas.figure.bbox.height-event.mouseevent.y
        x=event.mouseevent.x
        text="time:\nsmall\nbig\ntemp\nhumidity"
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




## read data
ds = datasource.DataSource()
ds.read_data("../data/dust-2014.dat")
print("read")
root = tk.Tk()

app = VisAnaGUI(master=root)
## display base data at startup
app.display_data(ds.get_base_data().df())


app.mainloop()
