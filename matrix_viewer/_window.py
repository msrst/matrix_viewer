
import tkinter as tk
import numpy as np
import time
from ._manager import manager
from ._tab_numpy import ViewerTabNumpy, matches_tab_numpy
from ._tab_struct import ViewerTabStruct, matches_tab_struct
from ._tab_text import ViewerTabText
from ._custom_notebook import CustomNotebook

class Viewer():
    """Class representing a matrix viewer window."""

    def __init__(self, title="Matrix Viewer"):
        """Constructs a new viewer window."""
        self.window  = tk.Toplevel(manager.get_or_create_root())
        self.window.title(title)
        self.window.geometry('500x500')
        self.window['bg'] = '#AC99F2'

        self.paned = CustomNotebook(self.window)
        self.paned.bind("<<NotebookTabClosed>>", self._on_tab_closed)  # binding child.destroy does not work on windows because there, destroy is called on window close but not on tab close as on linux
        f2 = tk.Frame(self.window)

        self.paned.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        self._event_loop_id = None
        self._destroyed = False
        self.window.bind("<Destroy>", self._on_destroy)
        self.window.bind("<Key>", self._on_q_pressed)
        manager.register(self)

        self.tabs = []

    def _on_destroy(self, event):
        if event.widget == self.window:  # we also get destroy events for childs so we need to filter them
            if not self._destroyed:
                manager.unregister(self)
                self._destroyed = True
            else:
                print('Error: double destroyed', self.window)

    def _on_q_pressed(self, event):
        if event.char == 'q':
            self.window.destroy()  # this will also call self._on_destroy
        else:
            # tkinter does not auto-focus the currently active window, and I also do not want to manually change the focus. Therefore to manual event propagation
            selected = self.paned.select()
            found = 0
            for tab, top_frame in self.tabs:
                if str(top_frame) == selected:
                    tab._on_key(event)
                    found += 1
            if found != 1:
                print('Error: frame', selected, 'not found', found)

    def _on_tab_closed(self, event):
        new_tab_frames = self.paned.tabs()
        diff = set(new_tab_frames).symmetric_difference(set(self.tab_frames))
        assert len(diff) == 1, f"invalid frame difference {new_tab_frames} vs. {self.tab_frames}"
        closed_tab_top_frame, = diff

        # find the ViewerTab associated with that frame
        found = 0
        for tab, top_frame in self.tabs:
            if str(top_frame) == closed_tab_top_frame:
                found += 1
                tab.on_destroy()
        if found != 1:
            print('Error: frame', closed_tab_top_frame, 'not found', found)

        self.tab_frames = new_tab_frames

    def register(self, tab, top_frame, tab_title):
        """
        This method should only be used by tabs. It adds the tab to the window.
        """
        self.tabs.append((tab, top_frame))
        self.paned.add(top_frame, text=tab_title)
        self.tab_frames = self.paned.tabs()  # update frame list

    def unregister(self, tab):
        """
        This method should only be used by tabs.
        """
        self.tabs.pop(list(zip(*self.tabs))[0].index(tab))
        if len(self.tabs) == 0:
            self.window.destroy()  # close if all tabs were closed by the user

    def view(self, object, tab_title=None, font_size=None, formatter=None):
        """Adds a new tab that visualizes the specified object.

        :param tab_title: The string show in the tab header.
        :param font_size: The font size used in the cells and the row / column headings.
        :param formatter: A function which converts the cells to string. Currently only used for
                          Matrix / Vector viewer.
        """
        if matches_tab_numpy(object):
            return ViewerTabNumpy(self, object, tab_title, font_size, formatter)
        elif matches_tab_struct(object):
            return ViewerTabStruct(self, object, tab_title, font_size)
        else:
            return ViewerTabText(self, object, tab_title, font_size)


def viewer(title="Matrix Viewer"):
    """Creates a new viewer window.

    :param title: The string shown in the window header.
    :return: The newly created viewer window.
    """
    return Viewer(title)


def view(object, tab_title=None, font_size=None, formatter=None):
    """Creates a new tab in the current window, which shows the object.
    Creates a new window if there are no opened windows.

    :param object: the object that is to be visualized.
    :param tab_title: The string show in the tab header.
    :param font_size: The font size used in the cells and the row / column headings.
    :param formatter: A function which converts the cells to string. Currently only used for
                        Matrix / Vector viewer.
    :return: The newly created viewer tab.
    """
    viewer = manager.last_viewer
    if viewer is None:
        viewer = Viewer()
    return viewer.view(object, tab_title, font_size, formatter)


def show(block=True):
    """Runs the event loop until all windows are closed.

    :param block: To keep API similarity to pyplot - if False, this will do nothing; if True, this function will block until all windows are closed."""
    if len(manager.registered_viewers) > 0:
        manager.show(block)


def pause(timeout):
    """Runs the event loop for the specified time interval.

    :param timeout: Time interval in seconds. If 0, it will exit immediately after processing all pending GUI events."""
    if len(manager.registered_viewers) > 0:
        manager.pause(timeout)
    else:
        time.sleep(timeout)


def show_with_pyplot():
    """This function should be used instead of show when you are also using matplotlib.pyplot.
    It concurrently runs the event loop for pyplot and matrix_viewer. It will run until all numpy and
    matrix_viewer windows were closed by the user.

    Note that unfortunately, pyplot and matrix_viewer appear to be slightly laggy if you are using a
    different pyplot backend than tkinter.
    """
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
