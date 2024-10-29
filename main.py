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
        self.tab.pack(expand=1, fill='both')

    def draw(self):
        pass

class TabGroup:
    def __init__(self, parent):
        self.parent = parent
        self.nb = ttk.Notebook(parent)
        self.tabs = []

    def add_tab(self, obj: Tab, name):
        tab = obj(self.nb, name)
        self.tabs.append(tab)
        self.nb.add(tab.tab, text=name)
        self.nb.pack(expand=1, fill='both')

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
            person[role] = False

class RotaTemplateSheet:
    def __init__(self, parent, names=None, roles=None):
        self.rT = RotaTemplate(names, roles)
        self.parent = parent
        self.sheet = Sheet(parent,
            header=roles,
            index=names,
            theme="light green",
            width=600,
            height=240
        )
        self.sheet.enable_bindings()
        self.sheet.grid(row=2, column=0, columnspan=4)

    def add_name(self, name):
        self.rT.add_name(name)
        self.sheet.insert_row_position()
        self.sheet.set_index_data(self.rT.names)
        self.sheet.pack()

    def add_role(self, name):
        self.rT.add_role(name)
        self.sheet.insert_column_position()
        self.sheet.set_header_data(self.rT.roles)
        self.sheet.pack()

class RotaTab(Tab):
    def draw(self):
        names = ["Adam", "Beth", "Charlie", "Dave"]
        self.addNameButton = Button(self.tab, text="Add Name")
        self.addNameButton.grid(column=0, row=0)
        
        self.addNameEntry = ttk.Entry(self.tab)
        self.addNameEntry.grid(column=1, row=0)
        
        self.addRoleButton = Button(self.tab, text="Add Role")
        self.addRoleButton.grid(column=2, row=0)
        
        self.addRoleEntry = ttk.Entry(self.tab)
        self.addRoleEntry.grid(column=3, row=0)
        
        self.rts = RotaTemplateSheet(self.tab, names)
        self.addNameButton.bind("<Button>", self.add_name)
        self.addRoleButton.bind("<Button>", self.add_role)

    def add_name(self, *args):
        name = self.addNameEntry.get()
        self.rts.add_name(name)

    def add_role(self, *args):
        role = self.addRoleEntry.get()
        self.rts.add_role(role)

class Window(Tk):
    def __init__(self):
        super().__init__()

        self.rota = Rota()

        self.title("Rota Manager")
        # pdb.set_trace()

        self.tabs = TabGroup(self)
        self.tabs.add_tab(RotaTab, "Rota")
        self.tabs.add_tab(Tab, "Availability")

        # Create Exit button
        self.button = Button(text="Exit")
        self.button.bind("<Button>", self.handle_button_press)
        self.button.pack()

    def handle_button_press(self, event):
        self.destroy()


# Start the event loop.
window = Window()
window.mainloop()
