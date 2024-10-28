from tkinter import Tk,Button,ttk
import tkinter as tk
from tksheet import Sheet
import pdb

from copy import copy
from collections import defaultdict

class Rota: 
    def __init__(self):
        pass

class Tab:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.tab = ttk.Frame(parent)

        self.draw()
        self.tab.pack()

    def draw(self):
        pass

class TabGroup:
    def __init__(self, parent):
        self.parent = parent
        self.nb = ttk.Notebook(parent)
        self.tabs = []

    def add_tab(self, obj: Tab, *args):
        tab = obj(self.nb, *args)
        self.tabs.append(tab)
        self.nb.pack()

class RotaTemplate:
    def __init__(self, names=None, roles=None):
        self.names = names or []
        self.roles = roles or []
        self.alloc = defaultdict(lambda: defaultdict(bool))

    def add_name(self, name: str):
        self.names.append(name)
        self.alloc[name] = {role: False for role in self.roles}

    def add_role(self, role: str):
        self.roles.append(role)
        for person in self.alloc.values():
            person.insert({role, False})

class RotaTemplateSheet:
    def __init__(self, parent, names=None, roles=None):
        self.rT = RotaTemplate(names, roles)
        self.parent = parent
        self.sheet = Sheet(parent,
            header=copy(roles),
            index=copy(names),
            theme="light green",
            width=600,
            height=240
        )
        self.sheet.enable_bindings()
        self.sheet.pack()

    def add_name(self, name):
        self.rT.add_name(name)
        self.sheet.insert_row([name], row_index=True)
        self.sheet.pack()

class RotaTab(Tab):
    def draw(self):
        names = ["Adam", "Beth", "Charlie", "Dave"]
        self.addName = Button(text="Add Name")
        self.rts = RotaTemplateSheet(self.parent, names)
        
class Window(Tk):
    def __init__(self):
        super().__init__()

        self.rota = Rota()

        self.title("Rota Manager")
        # pdb.set_trace()

        self.tabs = TabGroup(self)
        self.tabs.add_tab(RotaTab, "Rota")

        # Create Exit button
        self.button = Button(text="Exit")
        self.button.bind("<Button>", self.handle_button_press)
        self.button.pack()

        self.tabs.tabs[0].rts.add_name("Erin")

    def handle_button_press(self, event):
        self.destroy()


# Start the event loop.
window = Window()
window.mainloop()
