import tkinter as tk
#import datasource as ds

class VisAnaGUI(tk.LabelFrame):
    def __init__(self, master=None, ds=None):
        tk.LabelFrame.__init__(self, master, bg="#ff6600")
        #self.pack()
        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

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


        self.timeline = tk.Label(self, text="HIER STEHT NE TIMELINE!!!", bg="#0066ff")
        self.timeline.grid(column=0, row=1, sticky=(tk.N, tk.E, tk.W),columnspan=5)

        #for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()

app = VisAnaGUI(master=root)
app.mainloop()
