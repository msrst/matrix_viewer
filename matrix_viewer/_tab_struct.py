
import numpy as np
import tkinter as tk

from ._tab_table import ViewerTabTable
from ._tab_numpy import matches_tab_numpy

class ViewerTabStruct(ViewerTabTable):
    """A viewer tab that can be used to visualize a class, list, dict and some other container types."""
    def __init__(self, viewer, object, title=None, font_size=None):
        """Creates a new tab in the specified viewer. Please use viewer.view instead because this selects the appropriate Tab subclass."""
        self.object = object

        self._calc_font(font_size)

        default_title = object.__class__.__name__

        # query all attributes associated with the object
        if type(self.object) in (set, tuple):
            self.object_attributes = list(("", value) for value in self.object)
            self.row_heading_heading = ""
            default_title = f"{self.object.__class__.__name__} with {len(self.object)} elements"
        elif type(self.object) == list:
            self.object_attributes = list((str(i), value) for i, value in enumerate(self.object))
            self.row_heading_heading = ""
            default_title = f"list with {len(self.object)} elements"
        elif isinstance(self.object, dict):
            self.object_attributes = list(self.object.items())
            self.row_heading_heading = "Key"
            default_title = f"{type(self.object).__name__} with {len(self.object)} elements"
        else:
            self.object_attributes = []
            for element_name in dir(self.object):
                try:
                    attr = getattr(self.object, element_name)
                    if (not callable(attr)) and (element_name not in ["__dict__", "__doc__", "__module__", "__weakref__"]):
                        self.object_attributes.append((element_name, attr))
                except BaseException as e:
                    # print(f'matrix_viewer: exception querying {element_name}: {e}')
                    pass
            self.row_heading_heading = "Name"

        # format the values
        self.object_value_strings = []
        self.object_value_clickable = []
        for _, value in self.object_attributes:
            if isinstance(value, (int, float)):  # also matches bool because bool is a subclass of int
                value_string = str(value)
            elif type(value) in [str, bytes]:
                value_string = str(value)
                if '\n' in value_string:
                    value_string = f"multiline string with {len(value)} characters"
            elif value is None:
                value_string = "None"
            elif type(value) == np.ndarray:
                value_string = f"{value.shape} {value.dtype} ndarray"
            elif type(value) in [list, dict, set, tuple]:
                value_string = f"{value.__class__.__name__} with {len(value)} elements"
            else:
                value_string = str(type(value))

            clickable = matches_tab_numpy(value) or matches_tab_struct(value) or (type(value).__name__ in ["ndarray", "Tensor"])

            self.object_value_strings.append(value_string)
            self.object_value_clickable.append(clickable)

        self._font_changed()

        if title is None:
            title = default_title

        ViewerTabTable.__init__(self, viewer, title, 1, len(self.object_attributes))

        self.clickable_color = "#000077"
        self.clickable_hover_color = "#0000ff"

        self.canvas1.bind("<ButtonRelease-1>", self._on_mouse_release)

    def _font_changed(self):
        self.max_text_width = max(self.cell_font.measure(s) for s in (self.object_value_strings + ['Value']))
        row_headings = list(attr[0] for attr in self.object_attributes)
        self.row_heading_text_width = max(self.cell_font.measure(s) for s in (row_headings + [self.row_heading_heading]))

    def _on_mouse_release(self, event):
        hit_x, hit_y = self._calc_hit_cell(event.x, event.y)

        if (hit_x is not None) and (hit_x != -1) and (hit_y != -1):
            assert hit_x == 0
            if self.object_value_clickable[hit_y]:
                self.viewer.view(self.object_attributes[hit_y][1])
                new_tab_index = self.viewer.paned.index('end') - 1  # assumes that the new tab is the last tab
                self.viewer.paned.select(new_tab_index)  # go to the currently added tab

    def _draw_cells(self):
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
                if self.object_value_clickable[i_row]:
                    self.canvas1.create_text(
                        x, y, text=self.object_value_strings[i_row], font=self.cell_font, anchor='nw',
                        fill=self.clickable_color, activefill=self.clickable_hover_color,
                    )
                else:
                    self.canvas1.create_text(x, y, text=self.object_value_strings[i_row], font=self.cell_font, anchor='nw')
                y += self.cell_height
            x += self.cell_width

def matches_tab_struct(object):
    return (not isinstance(object, (int, float, str, bytes, np.ndarray))) and (type(object).__name__ != "Tensor") and (object is not None)