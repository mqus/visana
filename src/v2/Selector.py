from copy import deepcopy
from tkinter import Label,LabelFrame, Button, W, N, S, E, StringVar
from tkinter.ttk import Combobox, Entry


class Selector(LabelFrame):
    LIMIT=1000
    COMPARATORS=("<","<=","=","=>",">", "!=")
    def __init__(self,parent,ds, apply_action):
        super(Selector,self).__init__(parent, text="1: restrict/tidy up data")

        if ds is None:
            lbl = Label(self,text="Keine Datei geöffnet!")
            lbl.grid(column=0,row=0, sticky=(N,E,W,S))
            return
        self.plist=[col for col in ds.base().get_attr_names() if not col==ds.get_time_colname()]

        self.apply_action=apply_action
        self.draw_base()
        self.entire_clause=dict()
        #self.public_outer_clauses=dict()
        self.lastOuter=0

        #self.all_outer_labels=dict()
        #self.all_outer_addbuttons=dict()
        #self.all_outer_delbuttons=dict()
        self.all_outer_frames=dict()

        self.all_inner_clauses=dict()
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)

    def draw_base(self):
        self.add1= Button(self,text="OR [..]", command=self.add_outer_clause)
        self.add1.grid(column=0, row=self.LIMIT, sticky=(S,W))

        self.applybutton=Button(self,text="Apply",command=self.apply)
        self.applybutton.grid(column=1, row=self.LIMIT, sticky=(S,W,E))

    def add_outer_clause(self) -> int:
#        label=Label(self )# ,text="OR:")
        id=self.lastOuter
        self.lastOuter += 1
        frame=LabelFrame(self, text="OR")
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)
        addbutton=Button(frame,text="AND [...]", command=lambda j=id: self.add_inner_clause(j) )
        delbutton=Button(frame,text="remove", command=lambda j=id: self.delete_outer_clause(j) )
        frame.grid(column=0,row=id, columnspan=2, sticky=(N,E,W))
        addbutton.grid(column=0, row=self.LIMIT, sticky=(N,W))
        delbutton.grid(column=1, row=self.LIMIT, sticky=(N,E))

        #self.all_outer_addbuttons[id]=addbutton
        #self.all_outer_delbuttons[id]=delbutton
        self.all_outer_frames[id]=frame
        self.entire_clause[id]=dict()
        self.all_inner_clauses[id]=dict()
        self.all_inner_clauses[id]["lastInner"] = 0

        ##self.add_inner_clause(id)
        print("added 1clause")
        return id

    def add_inner_clause(self,i) -> int:
        id=self.all_inner_clauses[i]["lastInner"]
        self.all_inner_clauses[i]["lastInner"]= id + 1

        frame=LabelFrame(self.all_outer_frames[i])
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=1)
        frame.columnconfigure(2,weight=1)
        lbl=Label(frame,text="AND")
        delbutton=Button(frame,text="remove", command=lambda j=i, k=id: self.delete_inner_clause(j,k) )
        frame.grid(column=0,row=id, columnspan=2, sticky=(N,W,E))
        lbl.grid(column=0, row=0, sticky=(N,W))
        delbutton.grid(column=2, row=0, sticky=(N,E))


        parambox=Combobox(frame, state="readonly", width=10)
        parambox['values'] = self.plist
        parambox.bind('<<ComboboxSelected>>', lambda ev,j=i, k=id: self.param_changed(j,k))
        parambox.grid(column=0, row=1, sticky=(N, E, W))


        compbox=Combobox(frame, state="readonly", width=2)
        compbox['values'] = self.COMPARATORS
        compbox.bind('<<ComboboxSelected>>', lambda ev,j=i, k=id: self.comparator_changed(j,k))
        compbox.grid(column=1, row=1, sticky=(N, E, W))

        #TODO:validate
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv, i=i, j=id: self.value_changed(sv,i,j))
        cval=Entry(frame, width=10, textvariable=sv)
        cval.grid(column=2, row=1, sticky=(N, E, W))
        #cval.bind('<Key>', lambda ev,j=i, k=id: self.value_changed(j,k))


        #save all widgets:
        lookup=dict()
        lookup["frame"]=frame
        lookup["param"]=parambox
        lookup["comp"]=compbox
        lookup["value"]=cval
        self.all_inner_clauses[i][id] =lookup
        self.entire_clause[i][id]=dict()


        #print("fun",i, "and" , id)
        return id

    def delete_outer_clause(self,i):
        #self.all_outer_addbuttons[id]
        #self.all_outer_delbuttons[id]
        frame=self.all_outer_frames[i]
        del self.all_outer_frames[i]
        del self.entire_clause[i]
        del self.all_inner_clauses[i]

        frame.destroy()

        #print("nofun",i)


    def delete_inner_clause(self,i,j):
        frame=self.all_inner_clauses[i][j]["frame"]
        del self.entire_clause[i][j]
        del self.all_inner_clauses[i][j]
        frame.destroy()

    def apply(self):
#        print(type(c),c)
        self.apply_action()

    def get_clause(self):
        return deepcopy(self.entire_clause)


    def param_changed(self,i,j):
        pb = self.all_inner_clauses[i][j]["param"] #type:Combobox
        self.entire_clause[i][j]["param"] = pb.get()

    def comparator_changed(self, i, j):
        cb = self.all_inner_clauses[i][j]["comp"]  # type:Combobox
        self.entire_clause[i][j]["comp"] = cb.get()

    def value_changed(self,sv, i, j):
        self.entire_clause[i][j]["val"] = sv.get()



def tostr(clause):
    s = "("
    once1=True
    for i in clause:
        if once1:
            once1=False
        else:
            s += ") OR ("
        once2=True
        for j in clause[i]:
            if once2:
                once2 = False
            else:
                s += " AND "
            s+= clause[i][j]["param"]
            s+= clause[i][j]["comp"]
            s+= clause[i][j]["val"]
    s += ")"
    return s