
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
