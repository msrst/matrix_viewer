
import tkinter as tk
import tkinter.font
import numpy as np
import math
import platform

from ._utils import clip

class ViewerTab():
    """Base class for viewer tabs.

    You must also call viewer.register in the __init__ function.

    You must declare on_destroy(self): This method is called by Viewer when the tab is closed by the user. It is not called if the whole window is closed. It must call viewer.unregister(self).
    """
