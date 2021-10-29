
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

from numpy.lib.function_base import select

def clip(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value

class Viewer():
    def __init__(self, matrix, title="Matrix Viewer", matrix_title=None):
        self.matrix = matrix

        self.font_size = 12
        self.cell_vpadding = 5
        self.cell_hpadding = 5
        self.background_color = "#ffffff"
        self.heading_color = "#dddddd"
        self.cell_outline_color = "#bbbbbb"
        self.selection_border_color = "#000000"
        self.selection_border_width = 2
        self.selection_heading_color = "#aaaaaa"
        self.selection_color = "#bbbbff"
        self.autoscroll_delay = 0.1  # in seconds

        self.window  = tk.Tk()
        self.window.title(title)
        self.window.geometry('500x500')
        self.window['bg'] = '#AC99F2'

        self.cell_font = tk.font.Font(size=self.font_size, family="Helvetica")  # default root window needed to create font
        self.calc_dimensions()

        self.paned = ttk.Notebook(self.window)
        f1 = tk.Frame(self.paned)
        if matrix_title is None:
            matrix_title = f"{self.matrix.shape[0]} x {self.matrix.shape[1]} {self.matrix.dtype}"
        self.paned.add(f1, text=matrix_title)
        f2 = tk.Frame(self.window)

        self.paned.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)

        self.canvas1 = tk.Canvas(f1, width=20, bg=self.background_color)

        self.canvas1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.canvas1["scrollregion"] = [0, 0, 500, 1000]  # left, top, right, bottom corner of scrollable field
        self.canvas1.bind("<Configure>", self.on_resize)
        self.canvas1.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas1.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas1.bind("<Motion>", self.on_mouse_motion)
        # see https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar#17457843
        if platform.system() == "Linux":
            self.canvas1.bind_all("<Button-4>", lambda event: self.on_mouse_wheel(event, -1))
            self.canvas1.bind_all("<Button-5>", lambda event: self.on_mouse_wheel(event, 1))
        elif platform.system() == "Windows":
            self.canvas1.bind_all("<MouseWheel>", lambda event: self.on_mouse_wheel(event, -event.delta // 120))
        else: # Mac (untested, sorry I have no Mac)
            self.canvas1.bind_all("<MouseWheel>", lambda event: self.on_mouse_wheel(event, event.delta))

        self.xscrollbar = tk.Scrollbar(self.window, orient=tk.HORIZONTAL, command=self.on_x_scroll)
        self.xscrollbar.grid(column=0, rows=1, sticky="ew")
        print(self.xscrollbar.keys())
        print(self.xscrollbar["relief"], self.xscrollbar["repeatdelay"], self.xscrollbar["repeatinterval"], self.xscrollbar.get())
        self.yscrollbar = tk.Scrollbar(f1, orient=tk.VERTICAL, command=self.on_y_scroll)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        f2.grid(column=0, row=2, sticky="n")
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

        f3 = tk.Frame(self.paned)
        self.paned.add(f3)
        but = tk.Button(f3, text="DAT BUTTON IS IN PANED").pack(side=tk.LEFT)

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

    def calc_dimensions(self):
        # TODO determine optimal format here depending on matrix type and appropriately calculate max text width
        # (e.g. integer / floating point format, exp format vs. 0.00000)
        # TODO check how to handle complex numbers
        self.float_formatter = "{:.6f}".format
        self.max_text_width = self.cell_font.measure(self.float_formatter(1234.5678))

        self.column_heading_formatter = "{:d}".format
        self.row_heading_formatter = "{:d}".format

        self.cell_height = self.font_size + self.cell_vpadding * 2
        self.cell_width = self.max_text_width + self.cell_hpadding * 2
        self.row_heading_width = self.cell_font.measure("0" * (len(str(self.matrix.shape[0])) - 1)) + self.cell_hpadding * 2
        self.xscroll_items = self.matrix.shape[1]
        self.yscroll_items = self.matrix.shape[0]
        self.xscroll_item = 0
        self.yscroll_item = 0

        self.focused_cell = None  # format: [x, y] if a cell is focused
        self.selection = None  # format: [xstart, ystart, xend, yend] if something was selected
        self.mouse_press_start = None
        self.old_mouse_press_start = None
        self.last_autoscroll_time = 0

    def calc_size_scroll(self, init):
        self.xscroll_page_size = (self.size_x - self.row_heading_width) // self.cell_width
        self.xscroll_max = max(self.xscroll_items - self.xscroll_page_size, 0)
        self.xscroll_item = min(self.xscroll_item, self.xscroll_max)
        if self.xscroll_max == 0:
            self.xscrollbar.set(0, 1)
        else:
            self.scroll_x()

        self.yscroll_page_size = (self.size_y - self.cell_height) // self.cell_height
        self.yscroll_max = max(self.yscroll_items - self.yscroll_page_size, 0)
        self.yscroll_item = min(self.yscroll_item, self.yscroll_max)
        if self.yscroll_max == 0:
            self.yscrollbar.set(0, 1)
        else:
            self.scroll_y()

    def scroll_y(self):
        self.yscrollbar.set(self.yscroll_item / self.yscroll_items, (self.yscroll_item + self.yscroll_page_size) / self.yscroll_items)

    def scroll_x(self):
        self.xscrollbar.set(self.xscroll_item / self.xscroll_items, (self.xscroll_item + self.xscroll_page_size) / self.xscroll_items)

    def on_x_scroll(self, *args):
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
            self.scroll_x()
            self.draw()

    def on_y_scroll(self, *args):
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
            self.scroll_y()
            self.draw()

    def on_resize(self, event):
        self.size_x = event.width
        self.size_y = event.height
        self.calc_size_scroll(False)
        self.draw()

    def calc_hit_cell(self, mouse_x, mouse_y):
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

    def on_mouse_press(self, event):
        print('mouse press', event)

        if (self.selection is not None) and (event.state & 0x01 == 0x01):  # shift pressed
            self.mouse_press_start = self.old_mouse_press_start  # if we start selecting a rectangle by moving the holded mouse to the right, then release the mouse button, and then press shift on a point left to the rectangle, the start point is needed because we do correct the actual selection rectangle so that end > start
            if self.mouse_press_start is not None:
                self.adjust_selection(event)
        else:
            self.mouse_press_start = None
            hit_x, hit_y = self.calc_hit_cell(event.x, event.y)

            if hit_x is None:
                self.selection = None
                self.focused_cell = None
            elif (hit_x == -1) and (hit_y == -1):
                self.selection = [0, 0, self.xscroll_items, self.yscroll_items]
            elif hit_x == -1:
                self.selection = [0, hit_y, self.xscroll_items, hit_y + 1]
                self.focused_cell = [0, hit_y]
                self.mouse_press_start = [-1, hit_y]
            elif hit_y == -1:
                self.selection = [hit_x, 0, hit_x + 1, self.yscroll_items]
                self.focused_cell = [hit_x, 0]
                self.mouse_press_start = [hit_x, -1]
            else:
                self.selection = [hit_x, hit_y, hit_x + 1, hit_y + 1]
                self.focused_cell = [hit_x, hit_y]
                self.mouse_press_start = [hit_x, hit_y]

        self.draw()

    def on_mouse_release(self, event):
        print('mouse release', event)
        self.old_mouse_press_start = self.mouse_press_start
        self.mouse_press_start = None

    def on_mouse_motion(self, event):
        if self.mouse_press_start is not None:
            current_time = time.time()
            if self.last_autoscroll_time < current_time - self.autoscroll_delay:
                if self.mouse_press_start[0] != -1:
                    if event.x < self.row_heading_width:
                        self.xscroll_item = max(self.xscroll_item - 1, 0)
                        self.scroll_x()
                        self.last_autoscroll_time = current_time
                    elif event.x > self.row_heading_width + self.xscroll_page_size * self.cell_width:
                        self.xscroll_item = min(self.xscroll_item + 1, self.xscroll_max)
                        self.scroll_x()
                        self.last_autoscroll_time = current_time

                if self.mouse_press_start[1] != -1:
                    if event.y < self.cell_height:
                        self.yscroll_item = max(self.yscroll_item - 1, 0)
                        self.scroll_y()
                        self.last_autoscroll_time = current_time
                    elif event.y > self.cell_height + self.yscroll_page_size * self.cell_height:
                        self.yscroll_item = min(self.yscroll_item + 1, self.yscroll_max)
                        self.scroll_y()
                        self.last_autoscroll_time = current_time

            self.adjust_selection(event)
            self.draw()

    def on_mouse_wheel(self, event, delta):
        print('mouse wheel', event, delta)
        if event.state & 0x01 == 0x01:  # shift
            self.xscroll_item = clip(self.xscroll_item + delta * 3, 0, self.xscroll_max)
            self.scroll_x()
        else:
            self.yscroll_item = clip(self.yscroll_item + delta * 3, 0, self.yscroll_max)
            self.scroll_y()
        self.draw()

    def adjust_selection(self, event):
        hit_x = (event.x - self.row_heading_width) // self.cell_width + self.xscroll_item
        hit_y = (event.y - self.cell_height) // self.cell_height + self.yscroll_item

        if self.mouse_press_start[1] == -1:  # full column selected
            self.focused_cell = [clip(hit_x, 0, self.xscroll_items - 1), 0]
            selection_start = [self.mouse_press_start[0], self.yscroll_items - 1]
        elif self.mouse_press_start[0] == -1:  # full row selected
            self.focused_cell = [0, clip(hit_y, 0, self.yscroll_items - 1)]
            selection_start = [self.xscroll_items - 1, self.mouse_press_start[1]]
        else:
            self.focused_cell = [clip(hit_x, 0, self.xscroll_items - 1), clip(hit_y, 0, self.yscroll_items - 1)]
            selection_start = self.mouse_press_start

        self.selection = [
            min(selection_start[0], self.focused_cell[0]),
            min(selection_start[1], self.focused_cell[1]),
            max(selection_start[0], self.focused_cell[0]) + 1,
            max(selection_start[1], self.focused_cell[1]) + 1,
        ]

    def draw(self):
        self.canvas1.delete('all')

        line_end_x = self.size_x - 1
        line_end_y = self.size_y - 1
        self.canvas1.create_rectangle(0, 0, line_end_x, self.cell_height, fill=self.heading_color, width=0)
        self.canvas1.create_rectangle(0, 0, self.row_heading_width, line_end_y, fill=self.heading_color, width=0)

        if self.selection is not None:
            selection_x0 = self.row_heading_width + max(self.selection[0] - self.xscroll_item, 0) * self.cell_width
            selection_y0 = self.cell_height + max(self.selection[1] - self.yscroll_item, 0) * self.cell_height
            selection_x1 = self.row_heading_width + max(self.selection[2] - self.xscroll_item, 0) * self.cell_width
            selection_y1 = self.cell_height + max(self.selection[3] - self.yscroll_item, 0) * self.cell_height
            self.canvas1.create_rectangle(0, selection_y0, self.row_heading_width, selection_y1, width=0, fill=self.selection_heading_color)
            self.canvas1.create_rectangle(selection_x0, selection_y0, selection_x1, selection_y1, width=0, fill=self.selection_color)
            self.canvas1.create_rectangle(selection_x0, 0, selection_x1, self.cell_height, width=0, fill=self.selection_heading_color)

        if (self.focused_cell is not None) and (self.focused_cell[0] >= self.xscroll_item) and (self.focused_cell[1] >= self.yscroll_item):
            focused_x0 = self.row_heading_width + (self.focused_cell[0] - self.xscroll_item) * self.cell_width
            focused_y0 = self.cell_height + (self.focused_cell[1] - self.yscroll_item) * self.cell_height
            # re-fill the focused cell with white color so that it is better distinguishable from the selection
            self.canvas1.create_rectangle(focused_x0, focused_y0, focused_x0 + self.cell_width, focused_y0 + self.cell_height, width=0, fill=self.background_color)

        if (self.xscroll_page_size > 0) and (self.yscroll_page_size > 0):
            # vertical lines
            table_lines = np.empty((self.xscroll_page_size + 2) * 4)
            table_lines[::4] = self.row_heading_width
            table_lines[1::8] = 0
            table_lines[2::4] = self.row_heading_width
            table_lines[3::8] = line_end_y
            if len(table_lines) > 4:
                table_lines[4::4] = self.row_heading_width + np.arange(self.xscroll_page_size + 1) * self.cell_width
                table_lines[5::8] = line_end_y
                table_lines[6::4] = self.row_heading_width + np.arange(self.xscroll_page_size + 1) * self.cell_width
                table_lines[7::8] = 0
                self.canvas1.create_line(table_lines.tolist(), fill=self.cell_outline_color)

            # horizontal lines
            table_lines = np.empty((self.yscroll_page_size + 2) * 4)
            table_lines[::8] = 0
            table_lines[1::4] = np.arange(self.yscroll_page_size + 2) * self.cell_height
            table_lines[2::8] = line_end_x
            table_lines[3::4] = np.arange(self.yscroll_page_size + 2) * self.cell_height
            if len(table_lines) > 4:
                table_lines[4::8] = line_end_x
                table_lines[6::8] = 0
                self.canvas1.create_line(table_lines.tolist(), fill=self.cell_outline_color)

            x = -self.cell_hpadding + self.row_heading_width
            y = self.cell_vpadding + self.cell_height
            for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
                self.canvas1.create_text(x, y, text=self.row_heading_formatter(i_row), font=self.cell_font, anchor='ne')
                y += self.cell_height
            x += self.cell_width

            for i_column in range(self.xscroll_item, min(self.xscroll_item + self.xscroll_page_size + 1, self.xscroll_items)):
                y = self.cell_vpadding
                self.canvas1.create_text(x - self.max_text_width // 2, y, text=self.column_heading_formatter(i_column), font=self.cell_font, anchor='n')
                y += self.cell_height

                for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
                    self.canvas1.create_text(x, y, text=self.float_formatter(self.matrix[i_row, i_column]), font=self.cell_font, anchor='ne')
                    y += self.cell_height
                x += self.cell_width

            if self.selection is not None:
                if (selection_x0 != selection_x1) and (selection_y0 != selection_y1):
                    if self.selection[0] >= self.xscroll_item:
                        self.canvas1.create_line(selection_x0, selection_y0, selection_x0, selection_y1,
                            width=self.selection_border_width, fill=self.selection_border_color
                        )  # left border line
                    self.canvas1.create_line(selection_x1, selection_y0, selection_x1, selection_y1,
                        width=self.selection_border_width, fill=self.selection_border_color
                    )  # right border line
                    if self.selection[1] >= self.yscroll_item:
                        self.canvas1.create_line(selection_x0, selection_y0, selection_x1, selection_y0,
                            width=self.selection_border_width, fill=self.selection_border_color,
                        )  # top border line
                    self.canvas1.create_line(selection_x0, selection_y1, selection_x1, selection_y1,
                        width=self.selection_border_width, fill=self.selection_border_color,
                    )  # bottom border line

def view(matrix):
    viewer = Viewer(matrix)
    return viewer

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

    if matplotlib.get_backend() == 'TkAgg':
        matplotlib.pyplot.show()  # this will also show matrix_viewer windows because matplotlib is also using tkinter
        if len(manager.registered_viewers) > 0:  # pyplot.show() returns if all pyplot figures were closed
            show()  # Therefore, we have to wait until all matrix_viewer windows are closed, too
    else:
        matplotlib.pyplot.show(block=False)
        # this implementation is a bit laggy, eventually there is a better one
        while (len(manager.registered_viewers) > 0) or (len(matplotlib.pyplot.get_fignums()) > 0):
            # run both event loops in sequence, fast enough for acceptable delay
            pause(0.02)
            matplotlib.pyplot.pause(0.02)