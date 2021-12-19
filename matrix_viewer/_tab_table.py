
import tkinter as tk
from tkinter.constants import E
import tkinter.font
import numpy as np
import math
import platform

from ._manager import manager
from ._tab import ViewerTab
from ._utils import clip

class ViewerTabTable(ViewerTab):
    """
    subclasses must implememnt _font_changed(), which calculates cell widths etc on font (size) change
    """

    def __init__(self, viewer, title, num_columns, num_rows, highlight_selected_columns=True):
        ViewerTab.__init__(self)

        self.viewer = viewer
        self.xscroll_items = num_columns
        self.yscroll_items = num_rows
        self.highlight_selected_columns = highlight_selected_columns
        self.title = title

        self.cell_vpadding = self.font_size // 5
        self.cell_hpadding = self.font_size // 5
        self.background_color = "#ffffff"
        self.heading_color = "#dddddd"
        self.cell_outline_color = "#bbbbbb"
        self.selection_border_color = "#000000"
        self.selection_border_width = 2
        self.selection_heading_color = "#aaaaaa"
        self.selection_color = "#bbbbff"
        self.autoscroll_delay = 0.1  # in seconds

        self._calc_dimensions()

        self.xscroll_item = 0
        self.yscroll_item = 0

        self._focused_cell = None  # format: [x, y] if a cell is focused
        self._selection = None  # format: [xstart, ystart, xend, yend] if something was selected. It is always xstart < xend, ystart < yend
        self.mouse_press_start = None
        self.old_mouse_press_start = None
        self.last_autoscroll_time = 0

        self.top_frame = tk.Frame(self.viewer.paned)

        f1a = tk.Frame(self.top_frame)
        f1a.grid(column=0, row=0, sticky="nsew")
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)
        self.canvas1 = tk.Canvas(f1a, width=20, bg=self.background_color)

        self.canvas1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas1.bind("<Configure>", self._on_resize)

        # see https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar#17457843
        if platform.system() == "Linux":
            self.canvas1.bind("<Button-4>", lambda event: self._on_mouse_wheel(event, -1))
            self.canvas1.bind("<Button-5>", lambda event: self._on_mouse_wheel(event, 1))
        elif platform.system() == "Windows":
            self.canvas1.bind("<MouseWheel>", lambda event: self._on_mouse_wheel(event, -event.delta // 120))
        else:  # Mac (untested, sorry I have no Mac)
            self.canvas1.bind("<MouseWheel>", lambda event: self._on_mouse_wheel(event, event.delta))

        self.xscrollbar = tk.Scrollbar(self.top_frame, orient=tk.HORIZONTAL, command=self._on_x_scroll)
        self.xscrollbar.grid(column=0, rows=1, sticky="ew")
        self.yscrollbar = tk.Scrollbar(f1a, orient=tk.VERTICAL, command=self._on_y_scroll)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.size_x = 10
        self.size_y = 10
        self._calc_size_scroll()

        self.viewer.register(self, self.top_frame, title)

    def _calc_dimensions(self):
        self.row_heading_width = self.row_heading_text_width + self.cell_hpadding * 2
        self.cell_height = self.font_size + self.cell_vpadding * 2
        self.cell_width = self.max_text_width + self.cell_hpadding * 2

    def _calc_size_scroll(self):
        self.xscroll_page_size = (self.size_x - self.row_heading_width) // self.cell_width
        self.xscroll_max = max(self.xscroll_items - self.xscroll_page_size, 0)
        self.xscroll_item = min(self.xscroll_item, self.xscroll_max)
        self._scroll_x()

        self.yscroll_page_size = (self.size_y - self.cell_height) // self.cell_height
        self.yscroll_max = max(self.yscroll_items - self.yscroll_page_size, 0)
        self.yscroll_item = min(self.yscroll_item, self.yscroll_max)
        self._scroll_y()

    def _scroll_y(self):
        if self.yscroll_items == 0:
            self.yscrollbar.set(0, 1)
        else:
            self.yscrollbar.set(self.yscroll_item / self.yscroll_items, (self.yscroll_item + self.yscroll_page_size) / self.yscroll_items)

    def _scroll_x(self):
        if self.xscroll_items == 0:
            self.xscrollbar.set(0, 1)
        else:
            self.xscrollbar.set(self.xscroll_item / self.xscroll_items, (self.xscroll_item + self.xscroll_page_size) / self.xscroll_items)

    def _on_x_scroll(self, *args):
        new_xscroll_item = None
        if args[0] == 'scroll':
            if args[2] == 'units':
                new_xscroll_item = clip(self.xscroll_item + int(args[1]), 0, self.xscroll_max)
            elif args[2] == 'pages':
                new_xscroll_item = clip(self.xscroll_item + int(args[1]) * self.xscroll_page_size, 0, self.xscroll_max)
        elif args[0] == 'moveto':
            desired_fraction = float(args[1])  # desired scroll position from 0 to 1
            new_xscroll_item = clip(math.floor(desired_fraction * self.xscroll_items + 0.5), 0, self.xscroll_max)

        if (new_xscroll_item is not None) and (new_xscroll_item != self.xscroll_item):
            self.xscroll_item = new_xscroll_item
            self._scroll_x()
            self._draw()

    def _on_y_scroll(self, *args):
        new_yscroll_item = None
        if args[0] == 'scroll':
            if args[2] == 'units':
                new_yscroll_item = clip(self.yscroll_item + int(args[1]), 0, self.yscroll_max)
            elif args[2] == 'pages':
                new_yscroll_item = clip(self.yscroll_item + int(args[1]) * self.yscroll_page_size, 0, self.yscroll_max)
        elif args[0] == 'moveto':
            desired_fraction = float(args[1])  # desired scroll position from 0 to 1
            new_yscroll_item = clip(math.floor(desired_fraction * self.yscroll_items + 0.5), 0, self.yscroll_max)

        if (new_yscroll_item is not None) and (new_yscroll_item != self.yscroll_item):
            self.yscroll_item = new_yscroll_item
            self._scroll_y()
            self._draw()

    def _on_resize(self, event):
        self.size_x = event.width
        self.size_y = event.height
        self._calc_size_scroll()
        self._draw()

    def _on_key(self, event):
        if event.keysym == 'Next':
            if event.state & 0x01 == 0x01:  # shift
                if self._focused_cell is not None:
                    self._focused_cell[0] = min(self._focused_cell[0] + self.xscroll_page_size, self.xscroll_items - 1)
                    self._selection = [self._focused_cell[0], self._focused_cell[1],
                        self._focused_cell[0] + 1, self._focused_cell[1] + 1]
                self.xscroll_item = min(self.xscroll_item + self.xscroll_page_size, self.xscroll_max)
                self._scroll_x()
            else:
                if self._focused_cell is not None:
                    self._focused_cell[1] = min(self._focused_cell[1] + self.yscroll_page_size, self.yscroll_items - 1)
                    self._selection = [self._focused_cell[0], self._focused_cell[1],
                        self._focused_cell[0] + 1, self._focused_cell[1] + 1]
                self.yscroll_item = min(self.yscroll_item + self.yscroll_page_size, self.yscroll_max)
                self._scroll_y()
            self._draw()
        elif event.keysym == 'Prior':
            if event.state & 0x01 == 0x01:  # shift
                if self._focused_cell is not None:
                    self._focused_cell[0] = max(self._focused_cell[0] - self.xscroll_page_size, 0)
                    self._selection = [self._focused_cell[0], self._focused_cell[1],
                        self._focused_cell[0] + 1, self._focused_cell[1] + 1]
                self.xscroll_item = max(self.xscroll_item - self.xscroll_page_size, 0)
                self._scroll_x()
            else:
                if self._focused_cell is not None:
                    self._focused_cell[1] = max(self._focused_cell[1] - self.yscroll_page_size, 0)
                    self._selection = [self._focused_cell[0], self._focused_cell[1],
                        self._focused_cell[0] + 1, self._focused_cell[1] + 1]
                self.yscroll_item = max(self.yscroll_item - self.yscroll_page_size, 0)
                self._scroll_y()
            self._draw()

        if self._focused_cell is not None:
            next_cell = self._focused_cell.copy()
            if event.keysym == 'Up':
                next_cell[1] = max(self._focused_cell[1] - 1, 0)
            elif event.keysym == 'Down':
                next_cell[1] = min(self._focused_cell[1] + 1, self.yscroll_items - 1)
            elif event.keysym == 'Left':
                next_cell[0] = max(self._focused_cell[0] - 1, 0)
            elif event.keysym == 'Right':
                next_cell[0] = min(self._focused_cell[0] + 1, self.xscroll_items - 1)

            if next_cell != self._focused_cell:
                if event.state & 0x01 == 0x01:  # shift
                    pass  # TODO
                else:
                    self._focused_cell = next_cell
                    self.old_mouse_press_start = self._focused_cell
                    self._selection = [self._focused_cell[0], self._focused_cell[1],
                        self._focused_cell[0] + 1, self._focused_cell[1] + 1]

                    # if focus cell is outside the window, autoscroll so that it moves inside
                    if self._focused_cell[0] >= self.xscroll_item + self.xscroll_page_size:
                        self.xscroll_item = self._focused_cell[0] - self.xscroll_page_size
                        self._scroll_x()
                    elif self._focused_cell[0] < self.xscroll_item:
                        self.xscroll_item = self._focused_cell[0]
                        self._scroll_x()

                    if self._focused_cell[1] >= self.yscroll_item + self.yscroll_page_size:
                        self.yscroll_item = self._focused_cell[1] - self.yscroll_page_size
                        self._scroll_y()
                    elif self._focused_cell[1] < self.yscroll_item:
                        self.yscroll_item = self._focused_cell[1]
                        self._scroll_y()
                self._draw()

    def _calc_hit_cell(self, mouse_x, mouse_y):
        # Returns None, None if nothing was hit.
        # Returns -1, row_index if a row heading was clicked.
        # Returns column_index, -1 if a column was clicked.
        # Returns column_index, row_index if an ordinary cell was clicked.

        hit_x = (mouse_x - self.row_heading_width) // self.cell_width + self.xscroll_item
        hit_y = (mouse_y - self.cell_height) // self.cell_height + self.yscroll_item

        if mouse_x < self.row_heading_width:
            if mouse_y < self.cell_height:
                return -1, -1
            else:
                if hit_y < self.yscroll_items:
                    return -1, hit_y
                else:
                    return None, None
        else:
            if mouse_y < self.cell_height:
                if hit_x < self.xscroll_items:
                    return hit_x, -1
                else:
                    return None, None
            else:
                if (hit_x < self.xscroll_items) and (hit_y < self.yscroll_items):
                    return hit_x, hit_y
                else:
                    return None, None

    def _on_mouse_wheel(self, event, delta):
        if event.state & 0x01 == 0x01:  # shift
            self.xscroll_item = clip(self.xscroll_item + delta * 3, 0, self.xscroll_max)
            self._scroll_x()
        elif event.state & 0x04 == 0x04:  # control
            self._calc_font(max(self.font_size - delta, 1))
            self._font_changed()
            self._calc_dimensions()
            self._calc_size_scroll()
        else:
            self.yscroll_item = clip(self.yscroll_item + delta * 3, 0, self.yscroll_max)
            self._scroll_y()
        self._draw()

    def on_destroy(self):
        """
        This method is called by Viewer when the tab is closed by the user.
        """
        self.viewer.unregister(self)

    def _adjust_selection(self, event):
        """Adjusts self._focused_cell and self._selection if the mouse was released after starting to select something."""
        hit_x = (event.x - self.row_heading_width) // self.cell_width + self.xscroll_item
        hit_y = (event.y - self.cell_height) // self.cell_height + self.yscroll_item

        if self.mouse_press_start[1] == -1:  # full column selected
            self._focused_cell = [clip(hit_x, 0, self.xscroll_items - 1), 0]
            selection_start = [self.mouse_press_start[0], self.yscroll_items - 1]
        elif self.mouse_press_start[0] == -1:  # full row selected
            self._focused_cell = [0, clip(hit_y, 0, self.yscroll_items - 1)]
            selection_start = [self.xscroll_items - 1, self.mouse_press_start[1]]
        else:
            self._focused_cell = [clip(hit_x, 0, self.xscroll_items - 1), clip(hit_y, 0, self.yscroll_items - 1)]
            selection_start = self.mouse_press_start

        self._selection = [
            min(selection_start[0], self._focused_cell[0]),
            min(selection_start[1], self._focused_cell[1]),
            max(selection_start[0], self._focused_cell[0]) + 1,
            max(selection_start[1], self._focused_cell[1]) + 1,
        ]

    def _draw(self):
        self.canvas1.delete('all')

        line_end_x = self.size_x - 1
        line_end_y = self.size_y - 1
        self.canvas1.create_rectangle(0, 0, line_end_x, self.cell_height, fill=self.heading_color, width=0)
        self.canvas1.create_rectangle(0, 0, self.row_heading_width, line_end_y, fill=self.heading_color, width=0)

        if self._selection is not None:
            selection_x0 = self.row_heading_width + max(self._selection[0] - self.xscroll_item, 0) * self.cell_width
            selection_y0 = self.cell_height + max(self._selection[1] - self.yscroll_item, 0) * self.cell_height
            selection_x1 = self.row_heading_width + max(self._selection[2] - self.xscroll_item, 0) * self.cell_width
            selection_y1 = self.cell_height + max(self._selection[3] - self.yscroll_item, 0) * self.cell_height
            self.canvas1.create_rectangle(0, selection_y0, self.row_heading_width, selection_y1, width=0, fill=self.selection_heading_color)  # highlight row headings
            self.canvas1.create_rectangle(selection_x0, selection_y0, selection_x1, selection_y1, width=0, fill=self.selection_color)  # highlight the selection in blue
            if self.highlight_selected_columns:
                self.canvas1.create_rectangle(selection_x0, 0, selection_x1, self.cell_height, width=0, fill=self.selection_heading_color)  # highlight column headings

        if (self._focused_cell is not None) and (self._focused_cell[0] >= self.xscroll_item) and (self._focused_cell[1] >= self.yscroll_item):
            focused_x0 = self.row_heading_width + (self._focused_cell[0] - self.xscroll_item) * self.cell_width
            focused_y0 = self.cell_height + (self._focused_cell[1] - self.yscroll_item) * self.cell_height
            # re-fill the focused cell with white color so that it is better distinguishable from the selection
            self.canvas1.create_rectangle(focused_x0, focused_y0, focused_x0 + self.cell_width, focused_y0 + self.cell_height, width=0, fill=self.background_color)

        # vertical lines
        num_vertical_lines = min(self.xscroll_page_size, self.xscroll_items - self.xscroll_item) + 2
        table_lines = np.empty(num_vertical_lines * 4)
        table_lines[::4] = self.row_heading_width
        table_lines[1::8] = 0
        table_lines[2::4] = self.row_heading_width
        table_lines[3::8] = line_end_y
        if len(table_lines) > 4:
            table_lines[4::4] = self.row_heading_width + np.arange(num_vertical_lines - 1) * self.cell_width
            table_lines[5::8] = line_end_y
            table_lines[6::4] = self.row_heading_width + np.arange(num_vertical_lines - 1) * self.cell_width
            table_lines[7::8] = 0
            self.canvas1.create_line(table_lines.tolist(), fill=self.cell_outline_color)

        # horizontal lines
        num_horizontal_lines = min(self.yscroll_page_size, self.yscroll_items - self.yscroll_item) + 2
        table_lines = np.empty(num_horizontal_lines * 4)
        table_lines[::8] = 0
        table_lines[1::4] = np.arange(num_horizontal_lines) * self.cell_height
        table_lines[2::8] = line_end_x
        table_lines[3::4] = np.arange(num_horizontal_lines) * self.cell_height
        if len(table_lines) > 4:
            table_lines[4::8] = line_end_x
            table_lines[6::8] = 0
            self.canvas1.create_line(table_lines.tolist(), fill=self.cell_outline_color)

        self._draw_cells()

        if self._selection is not None:
            if (selection_x0 != selection_x1) and (selection_y0 != selection_y1):
                if self._selection[0] >= self.xscroll_item:
                    self.canvas1.create_line(selection_x0, selection_y0, selection_x0, selection_y1,
                        width=self.selection_border_width, fill=self.selection_border_color
                    )  # left border line
                self.canvas1.create_line(selection_x1, selection_y0, selection_x1, selection_y1,
                    width=self.selection_border_width, fill=self.selection_border_color
                )  # right border line
                if self._selection[1] >= self.yscroll_item:
                    self.canvas1.create_line(selection_x0, selection_y0, selection_x1, selection_y0,
                        width=self.selection_border_width, fill=self.selection_border_color,
                    )  # top border line
                self.canvas1.create_line(selection_x0, selection_y1, selection_x1, selection_y1,
                    width=self.selection_border_width, fill=self.selection_border_color,
                )  # bottom border line
