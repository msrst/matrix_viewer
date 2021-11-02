
import tkinter as tk

from ._tab import ViewerTab

class ViewerTabText(ViewerTab):
    """
    Viewer tab that displays the str(.) representation of an object.
    """
    def __init__(self, viewer, object, title="data"):
        self.viewer = viewer
        self.object = object

        ViewerTab.__init__(self)

        self.top_frame = tk.Frame(self.viewer.paned)

        f1a = tk.Frame(self.top_frame)
        f1a.grid(column=0, row=0, sticky="nsew")
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)

        self.xscrollbar = tk.Scrollbar(self.top_frame, orient=tk.HORIZONTAL)
        self.xscrollbar.grid(column=0, rows=1, sticky="ew")
        self.yscrollbar = tk.Scrollbar(f1a, orient=tk.VERTICAL)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_display = tk.Text(f1a, width=20, wrap=tk.NONE, xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_display.insert('1.0', str(self.object))
        self.text_display.configure(state='disabled')  # TODO allow the user to select and copy text

        self.xscrollbar.config(command=self.text_display.xview)
        self.yscrollbar.config(command=self.text_display.yview)

        self.viewer.register(self, self.top_frame, title)

    def on_destroy(self):
        self.viewer.unregister(self)