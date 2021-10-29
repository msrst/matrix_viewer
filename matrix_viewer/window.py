
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
from . import manager
from .utils import clip
from .tab import ViewerTab

class Viewer():
    def __init__(self, title="Matrix Viewer"):

        self.window  = tk.Tk()
        self.window.title(title)
        self.window.geometry('500x500')
        self.window['bg'] = '#AC99F2'

        self.paned = ttk.Notebook(self.window)
        f2 = tk.Frame(self.window)

        self.paned.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        f2.grid(column=0, row=2, sticky="n")
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

        self._event_loop_id = None
        self._destroyed = False
        self.window.bind("<Destroy>", self.destroy)  # this will fire multiple times on destroy
        manager.register(self)

    def show(self, block=True):
        if block:
            self.window.mainloop()
        else:
            pass

    def pause(self, timeout):
        # timeout: in seconds

        milliseconds = int(1000 * timeout)
        if milliseconds > 0:
            self._event_loop_id = self.window.after(milliseconds, self.stop_event_loop)
        else:
            self._event_loop_id = self.window.after_idle(self.stop_event_loop)

        self.window.mainloop()

    def stop_event_loop(self):
        if self._event_loop_id:
            self.window.after_cancel(self._event_loop_id)
            self._event_loop_id = None
        self.window.quit()

    def destroy(self, *args):
        print("destroy")
        if not self._destroyed:
            if self._event_loop_id:
                self.window.after_cancel(self._event_loop_id)
            manager.unregister(self)
            self._destroyed = True

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
        manager.any_viewer().show(block)

def pause(timeout):
    if len(manager.registered_viewers) > 0:
        manager.any_viewer().pause(timeout)
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