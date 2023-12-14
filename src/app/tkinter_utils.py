import tkinter as tk

class StringVarWithMapping(tk.StringVar):
    def __init__(self, mapping, *args, **kwargs):
        super(StringVarWithMapping, self).__init__(*args, **kwargs)
        
        self.mapping = mapping

    def get(self) -> str:
        item = super().get()
        id = self.mapping[item]

        return id