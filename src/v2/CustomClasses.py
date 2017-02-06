from tkinter import E, S, Listbox, END, Message, NORMAL, DISABLED, VERTICAL
from tkinter import N, W
from tkinter.ttk import Frame, Label, Button, Scrollbar


class CustomClasses(Frame):


    def __init__(self, parent, master):
        super(CustomClasses, self).__init__(parent)

        self.grid(column=0, row=0, sticky=(N,E,W,S))
        self.window=master
        if self.window.ds is None:
            return

        label = Label(self, text="Select Sizes for new Class:")
        label.grid(row=0, column=0, columnspan=2)

        ## save results to dictionary
        self.classesDict = {}
        ## name for next class
        self.classLabel = 1
        ## is the result a valid&complete dictionary?
        self.success = False
        ## list with columns that have not yet been selected
        self.remaining_grains = self.window.ds.get_grain_columns()

        ## selection box with all grain sizes
        self.grainListBox = Listbox(self, selectmode="extended", height=20, width=15)
        for col in self.window.ds.get_grain_columns():
            self.grainListBox.insert(END, col)
        self.grainListBox.grid(row=1, column=0, rowspan=10)
        scrbar = Scrollbar(self, orient=VERTICAL, command=self.grainListBox.yview)
        scrbar.grid(row=1, column=1, rowspan=10,sticky=(N, W, S))
        self.grainListBox["yscrollcommand"] = scrbar.set

        ## button to add selected sizes to new class
        self.b_add = Button(self, text='Add to new Class', width=19)
        self.b_add['command'] = self.add_class
        self.b_add.grid(row=11, column=0, columnspan=2)

        ## button to add all remaining entries to a new class
        self.b_remaining = Button(self, text='Add remaining to Class', width=19)
        self.b_remaining['command'] = self.add_remaining
        self.b_remaining.grid(row=12, column=0, columnspan=2)

        ## button to reset all previous selections
        self.b_reset = Button(self, text='Reset', width=17)
        self.b_reset['command'] = self.reset
        self.b_reset.grid(row=13, column=0, columnspan=2)

        # self.b_accept = Button(self, text='Save')
        # self.b_accept['command'] = self.accept
        # self.b_accept.grid(row=14, column=0)

        # ## button to cancel selection process and return to main window
        # self.b_cancel = Button(self, text='Cancel', width=17)
        # self.b_cancel['command'] = self.top.destroy
        # self.b_cancel.grid(row=15, column=0)

        self.print_classes()

    ## reset state to initial state, i.e. forget about selections
    def reset(self):
        self.classesDict = {}
        self.remaining_grains = self.window.ds.get_grain_columns()
        ## reset listbox
        self.grainListBox.delete(0, END)
        for col in self.remaining_grains:
            self.grainListBox.insert(END, col)

        ## remove all widgets in result column...
        for label in self.grid_slaves():
            if int(label.grid_info()["column"]) == 2:
                label.destroy()
        ##reset ClassLabel
        self.classLabel=1

        ## ... and paint them all new!
        self.print_classes()


    ## add selected grain sizes to new class
    def add_class(self):
        selected = self.grainListBox.curselection()
        #print(selected)
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
            newlabel="Class{}".format(self.classLabel)
            self.classesDict[newlabel] = selectedCols
            self.classLabel += 1

            self.print_classes()
            self.window.calc.cclasses_changed(self.classesDict)

    def add_remaining(self):
        newlabel = "Class{}".format(self.classLabel)
        self.classesDict[newlabel] = [rg for rg in self.remaining_grains]
        self.remaining_grains = []
        self.classLabel += 1

        self.grainListBox.delete(0, END)

        self.print_classes()

        self.window.calc.cclasses_changed(self.classesDict)

    def print_classes(self):
        frm=Frame(self)
        frm.grid(column=2, row=1,rowspan=20, sticky = (N,E,W,S))

        rowOffset = 0
        label = Label(self, text="Grain Classes:")
        label.grid(row=rowOffset, column=2)
        for k in sorted(self.classesDict.keys()):
            rowOffset += 1
            classDescr = "" + k + ":"
            for grain in self.classesDict[k]:
                classDescr = classDescr + "\n" + grain
            classMsg = Message(frm, text=classDescr)#, width=100)
            classMsg.grid(column=0, row=rowOffset, sticky = (N,W))

        #print("GRAIN_COLS:")
        #print(GRAIN_COLS)
        self.window.calc.cclasses_changed(self.classesDict)


        if len(self.remaining_grains) == 0:
            #self.b_accept.config(state = NORMAL)
            self.b_remaining.config(state = DISABLED)
            self.b_add.config(state = DISABLED)
        else:
            self.b_add.config(state=NORMAL)
            self.b_remaining.config(state = NORMAL)
            #self.b_accept.config(state = DISABLED)

        if len(self.classesDict) == 0:
            self.b_reset.config(state = DISABLED)
        else:
            self.b_reset.config(state = NORMAL)


    # def accept(self):
    #     self.success = True
    #     #TODO write to calc
    #     self.window.history.add("Set Custom Classes to "+str(self.classesDict))
    #     self.window.calc.cclasses_changed(self.classesDict)

