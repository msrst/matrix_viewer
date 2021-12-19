
import tkinter as tk
import tkinter.font
import numpy as np
import math
import platform
from ._manager import manager

class ViewerTab():
    """Base class for viewer tabs.

    You must also call viewer.register in the __init__ function.

    You must declare on_destroy(self): This method is called by Viewer when the tab is closed by the user. It is not called if the whole window is closed. It must call viewer.unregister(self).
    """

    def _on_key(self, event):
        """
        Called for keyboard events. Can be overriden by subclasses if needed
        """
        pass

    def _calc_font(self, user_font_size):
        """
        sets self.cell_font and self.font_size according to the specified user font and the screen DPI
        """
        dpi = manager.get_or_create_root().winfo_fpixels('1i')
        if user_font_size is None:
            if dpi >= 200:
                self.font_size = 28
            elif dpi >= 150:
                self.font_size = 22
            elif dpi >= 90:
                self.font_size = 16
            else:
                self.font_size = 14
        else:
            self.font_size = user_font_size

        # default root window needed to create font. -size -> size in pixels instead of inches
        if platform.system() == 'Linux':
            self.cell_font = tk.font.Font(size=-self.font_size, family="Sans")  # Arial was messing up
        else:
            self.cell_font = tk.font.Font(size=-self.font_size, family="Arial")
