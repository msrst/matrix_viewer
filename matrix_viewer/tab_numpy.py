
import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
import numpy as np
import math
import time
import os
import platform

from . import manager
from .utils import clip
from .tab import ViewerTab

class ViewerTabNumpy(ViewerTab):
    def __init__(self, viewer, matrix, matrix_title=None):
        self.matrix = matrix

        if matrix_title is None:
            matrix_title = f"{self.matrix.shape[0]} x {self.matrix.shape[1]} {self.matrix.dtype}"

        self.font_size = 12
        self.cell_font = tk.font.Font(size=self.font_size, family="Helvetica")  # default root window needed to create font

        # TODO determine optimal format here depending on matrix type and appropriately calculate max text width
        # (e.g. integer / floating point format, exp format vs. 0.00000)
        # TODO check how to handle complex numbers
        self.float_formatter = "{:.6f}".format
        self.max_text_width = self.cell_font.measure(self.float_formatter(1234.5678))

        self.column_heading_formatter = "{:d}".format
        self.row_heading_formatter = "{:d}".format
        self.row_heading_text_width = self.cell_font.measure("0" * (len(str(self.matrix.shape[0] - 1))))

        ViewerTab.__init__(self, viewer, matrix_title, matrix.shape[1], matrix.shape[0])

        self.canvas1.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas1.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas1.bind("<Motion>", self.on_mouse_motion)

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

    def draw_cells(self):
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
