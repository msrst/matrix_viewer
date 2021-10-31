
import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import math
import time
import os
import platform
from .manager import manager
from .utils import clip
from .tab import ViewerTab
from .custom_notebook import CustomNotebook

class Viewer():
    def __init__(self, title="Matrix Viewer"):
        self.window  = tk.Toplevel(manager.get_or_create_root())
        self.window.title(title)
        self.window.geometry('500x500')
        self.window['bg'] = '#AC99F2'

        self.paned = CustomNotebook(self.window)
        f2 = tk.Frame(self.window)

        self.paned.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        f2.grid(column=0, row=2, sticky="n")
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

        self._event_loop_id = None
        self._destroyed = False
        self.window.bind("<Destroy>", self.on_destroy)
        manager.register(self)

        self.tabs = []

    def on_destroy(self, event):
        if event.widget == self.window:  # we also get destroy events for childs so we need to filter them
            if not self._destroyed:
                manager.unregister(self)
                self._destroyed = True
            else:
                print('Error: double destroyed', self.window)

    def register(self, tab):
        self.tabs.append(tab)

    def unregister(self, tab):
        self.tabs.pop(self.tabs.index(tab))
        if len(self.tabs) == 0:
            self.window.destroy()  # close if all tabs were closed by the user

def viewer(title="Matrix Viewer"):
    return Viewer(title)

def view(matrix):
    viewer = manager.last_viewer
    if viewer is None:
        viewer = Viewer()
    viewer_tab = ViewerTab(viewer, matrix)
    return viewer_tab

def show(block=True):
    if len(manager.registered_viewers) > 0:
        manager.show(block)

def pause(timeout):
    if len(manager.registered_viewers) > 0:
        manager.pause(timeout)
    else:
        time.sleep(timeout)

def show_with_pyplot():
    import matplotlib
    import matplotlib.pyplot

    show(block=False)

    if matplotlib.get_backend() == 'TkAgg':  # matplotlib is also using tkinter
        matplotlib.pyplot.show()  # this will also show matrix_viewer windows
        if len(manager.registered_viewers) > 0:  # pyplot.show() returns if all pyplot figures were closed
            show()  # Therefore, we have to continue running the event loop until all matrix_viewer windows are closed, too
    else:
        matplotlib.pyplot.show(block=False)
        # this implementation is a bit laggy, eventually there is a better one
        while (len(manager.registered_viewers) > 0) or (len(matplotlib.pyplot.get_fignums()) > 0):
            # run both event loops in sequence, fast enough for acceptable delay
            pause(0.02)
            matplotlib.pyplot.pause(0.02)