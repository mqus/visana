from copy import deepcopy
from tkinter import Label,LabelFrame, Button, W, N, S, E

class Selector(LabelFrame):
    LIMIT=1000
    def __init__(self,parent,param_list, apply_action):
        super(Selector,self).__init__(parent)
        self.plist=param_list
        self.apply_action=apply_action
        self.draw_base()
        self.outer_clauses=dict()
        self.public_outer_clauses=dict()
        self.lastOuter=0

        self.all_outer_labels=dict()
        self.all_outer_addbuttons=dict()
        self.all_outer_delbuttons=dict()
        self.all_outer_frames=dict()

        self.all_inner_columns=dict()
        self.all_inner_operators=dict()
        self.all_inner_values=dict()

    def draw_base(self):
        self.add1= Button(self,text="OR [..]", command=self.add_outer_clause)
        self.add1.grid(column=0, row=self.LIMIT, sticky=(S,W))

        self.applybutton=Button(self,text="Apply",command=self.apply)
        self.applybutton.grid(column=1, row=self.LIMIT, sticky=(S,W,E))

    def add_outer_clause(self) -> int:
#        label=Label(self )# ,text="OR:")
        id=self.lastOuter
        self.lastOuter += 1
        frame=LabelFrame(self)
        addbutton=Button(frame,text="And [...]", command=lambda j=id: self.add_inner_clause(j) )
        delbutton=Button(frame,text="Remove", command=lambda j=id: self.delete_outer_clause(j) )
        frame.grid(column=0,row=id, columnspan=2)
        addbutton.grid(column=0, row=self.LIMIT)
        delbutton.grid(column=1, row=self.LIMIT)

        self.all_outer_addbuttons[id]=addbutton
        self.all_outer_delbuttons[id]=delbutton
        self.all_outer_frames[id]=frame
        self.outer_clauses[id]=dict()

        self.add_inner_clause(id)
        print("added 1clause")
        return id

    def add_inner_clause(self,i) -> int:


        print("fun",i)

    def delete_outer_clause(self,i):
        #self.all_outer_addbuttons[id]
        #self.all_outer_delbuttons[id]
        frame=self.all_outer_frames[i]
        del self.all_outer_frames[i]
        del self.outer_clauses[i]
        frame.destroy()

        print("nofun",i)




    def apply(self):
        self.public_outer_clauses = deepcopy(self.outer_clauses)


        self.apply_action()