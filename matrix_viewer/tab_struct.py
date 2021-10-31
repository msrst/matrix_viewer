
import numpy as np
import tkinter as tk
from .tab import ViewerTab

class ViewerTabStruct(ViewerTab):
    def __init__(self, viewer, object, title=None):
        self.object = object

        self.font_size = 12
        self.cell_font = tk.font.Font(size=self.font_size, family="Helvetica")  # default root window needed to create font

        default_title = object.__class__.__name__

        # query all attributes associated with the object
        if type(self.object) == set:
            self.object_attributes = list(("", value) for value in self.object)
            self.row_heading_heading = ""
            default_title = f"set with {len(self.object)} elements"
        elif type(self.object) == list:
            self.object_attributes = list((str(i), value) for i, value in enumerate(self.object))
            self.row_heading_heading = ""
            default_title = f"list with {len(self.object)} elements"
        elif type(self.object) == dict:
            self.object_attributes = list(self.object.items())
            self.row_heading_heading = "Key"
            default_title = f"dict with {len(self.object)} elements"
        else:
            self.object_attributes = []
            for element_name in dir(self.object):
                attr = getattr(self.object, element_name)
                if not callable(attr):
                    self.object_attributes.append((element_name, attr))
            self.row_heading_heading = "Name"

        # format the values
        self.object_value_strings = []
        for _, value in self.object_attributes:
            if type(value) in [str, int, float, bytes]:
                value_string = str(value)
            elif type(value) == np.ndarray:
                value_string = f"{value.shape} {value.dtype} ndarray"
            elif type(value) in [list, dict, set]:
                value_string = f"{value.__class__.__name__} with {len(value)} elements"
            else:
                value_string = str(type(value))
            self.object_value_strings.append(value_string)

        self.max_text_width = max(self.cell_font.measure(s) for s in self.object_value_strings)
        self.row_heading_text_width = max(self.cell_font.measure(s[0]) for s in self.object_attributes)

        if title is None:
            title = default_title

        ViewerTab.__init__(self, viewer, title, 1, len(self.object_attributes))

    def draw_cells(self):
        x = self.cell_hpadding
        y = self.cell_vpadding
        self.canvas1.create_text(x, y, text=self.row_heading_heading, font=self.cell_font, anchor='nw')
        y += self.cell_height
        for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
            self.canvas1.create_text(x, y, text=self.object_attributes[i_row][0], font=self.cell_font, anchor='nw')
            y += self.cell_height
        x += self.row_heading_width

        for i_column in range(self.xscroll_item, min(self.xscroll_item + self.xscroll_page_size + 1, self.xscroll_items)):
            y = self.cell_vpadding
            self.canvas1.create_text(x, y, text="Value", font=self.cell_font, anchor='nw')
            y += self.cell_height

            for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
                self.canvas1.create_text(x, y, text=self.object_value_strings[i_row], font=self.cell_font, anchor='nw')
                y += self.cell_height
            x += self.cell_width