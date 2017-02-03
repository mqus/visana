import tkinter as tk

HEADER = "::LOG::\n"


class HistoryView(tk.Frame):
    def __init__(self, master):
        super(HistoryView, self).__init__( master)

        self.history_text = ""


        self.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0,weight=1)

        self.history = tk.Text(self, width=45)
        self.history.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S))

        self.historyslider = tk.Scrollbar(self,orient=tk.VERTICAL, command=self.history.yview)
        self.historyslider.grid(column=1, row=0, sticky=(tk.N, tk.S))
        self.history['yscrollcommand'] = self.historyslider.set

        self.add(HEADER,False)


    def add(self,text, with_newline=True):
        if with_newline:
            self.history_text += "\n"
            self.history.insert('end', "\n")
        self.history_text += text
        self.history.insert('end', text)
        self.history.see("end")

    def get_text(self):
        return self.history_text


