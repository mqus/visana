import tkinter as tk
from tkinter import Listbox, END, Message, NORMAL, DISABLED
from datasource import COLORS
from datasource import GRAIN_COLS

class Mbox(object):

    root = None

    def __init__(self):
        self.top = tk.Toplevel(Mbox.root)

        self.frm = tk.Frame(self.top, borderwidth=4, relief='ridge')
        self.frm.grid(column=0, row=0)

        label = tk.Label(self.frm, text="Select Sizes for new Class:")
        label.grid(row=1, column=0)

        ## save results to dictionary
        self.classesDict = {}
        ## name for next class
        self.classLabel = 1
        ## is the result a valid&complete dictionary?
        self.success = False
        ## list with columns that have not yet been selected
        self.remaining_grains = [col for col in GRAIN_COLS]

        ## selection box with all grain sizes
        self.grainListBox = Listbox(self.frm, selectmode="multiple", height=32)
        for col in GRAIN_COLS:
            self.grainListBox.insert(END, col)
        self.grainListBox.grid(row=2, column=0, rowspan=10)

        ## button to add selected sizes to new class
        self.b_add = tk.Button(self.frm, text='Add to Class', width=17)
        self.b_add['command'] = self.add_class
        self.b_add.grid(row=12, column=0)

        ## button to add all remaining entries to a new class
        self.b_remaining = tk.Button(self.frm, text='Add remaining to Class', width=17)
        self.b_remaining['command'] = self.add_remaining
        self.b_remaining.grid(row=13, column=0)

        ## button to reset all previous selections
        self.b_reset = tk.Button(self.frm, text='Reset', width=17)
        self.b_reset['command'] = self.reset
        self.b_reset.grid(row=14, column=0)

        ## button to cancel selection process and return to main window
        self.b_cancel = tk.Button(self.frm, text='Cancel', width=17)
        self.b_cancel['command'] = self.top.destroy
        self.b_cancel.grid(row=15, column=0)

        self.print_classes()

    ## reset state to initial state, i.e. forget about selections
    def reset(self):
        self.classesDict = {}
        self.remaining_grains = [col for col in GRAIN_COLS]
        ## reset listbox
        self.grainListBox.delete(0, END)
        for col in GRAIN_COLS:
            self.grainListBox.insert(END, col)

        ## remove all widgets in result column...
        for label in self.frm.grid_slaves():
            if int(label.grid_info()["column"]) == 1:
                label.grid_forget() 

        ## ... and paint them all new!
        self.print_classes()

    ## add selected grain sizes to new class
    def add_class(self):
        selected = self.grainListBox.curselection()
        print(selected)
        if len(selected) > 0:
            selectedCols = []
            for i in selected:
                col = self.grainListBox.get(i)
                selectedCols.append(col)
            for i in sorted(selected, reverse=True):
                self.grainListBox.delete(i)

            #print("selected Cols:")
            #print(selectedCols)
            #print(selected)
            #print("remaining:")
            for sel in selectedCols:
                self.remaining_grains.remove(sel)
            #print(self.remaining_grains)
            self.classesDict[self.classLabel] = selectedCols
            self.classLabel += 1

            self.print_classes()

    def add_remaining(self):
        self.classesDict[self.classLabel] = [rg for rg in self.remaining_grains]
        self.remaining_grains = []
        self.classLabel += 1

        self.grainListBox.delete(0, END)

        self.print_classes()

    def print_classes(self):
        rowOffset = 0
        label = tk.Label(self.frm, text="Grain Classes:")
        label.grid(row=rowOffset, column=1)
        for k in sorted(self.classesDict.keys()):
            rowOffset += 1
            classDescr = ""
            for grain in self.classesDict[k]:
                classDescr = classDescr + "\n" + grain
            classMsg = Message(self.frm, text=classDescr, width=100)
            classMsg.grid(column=1, row=rowOffset)

        #print("GRAIN_COLS:")
        #print(GRAIN_COLS)

        b_accept = tk.Button(self.frm, text='Accept')
        b_accept['command'] = self.accept
        b_accept.grid(row=rowOffset+1, column=1)

        if len(self.remaining_grains) == 0:
            b_accept.config(state = NORMAL)
            self.b_remaining.config(state = DISABLED)
            self.b_add.config(state = DISABLED)
        else:
            b_accept.config(state = DISABLED)

        if len(self.classesDict) == 0:
            self.b_reset.config(state = DISABLED)
        else:
            self.b_reset.config(state = NORMAL)


    def accept(self):
        self.success = True
        self.top.destroy()