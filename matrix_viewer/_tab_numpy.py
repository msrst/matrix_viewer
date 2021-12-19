
import numpy as np
import tkinter as tk
import tkinter.font
import time
from ._tab_table import ViewerTabTable

class ViewerTabNumpy(ViewerTabTable):
    """A viewer tab that can be used to visualize numpy.ndarray matrices and vectors."""
    def __init__(self, viewer, matrix, matrix_title=None, font_size=None, cell_formatter=None):
        """Creates a new tab in the specified viewer. Please use viewer.view instead because this selects the appropriate Tab subclass."""
        self.matrix = matrix
        self.num_dims = matrix.ndim

        if type(self.matrix).__name__ == "Tensor":
            self.matrix = self.matrix.cpu().numpy()  # convert pytorch to numpy. This is like a copy
        else:
            # If the user modifies the value after running viewer.view, but before viewer.show, the new values
            # are displayed but one would expect that the state when viewer.view was called is displayed. Therefore,
            # make a copy
            self.matrix = self.matrix.copy()

        assert self.matrix.dtype.isbuiltin == 1, "matrix must be a type built-in into numpy (e. g. float32 ndarray), but it is a composed type or something else"

        if matrix_title is None:
            if self.num_dims == 1:
                matrix_title = f"{self.matrix.shape[0]} {self.matrix.dtype}"
            else:
                matrix_title = f"{self.matrix.shape[0]} x {self.matrix.shape[1]} {self.matrix.dtype}"

        self._calc_font(font_size)

        if self.matrix.dtype.kind == 'c':
            self.max_val = np.max(self.matrix.real) + np.max(self.matrix.imag) * 1j
        else:
            self.max_val = np.max(self.matrix)

        small_formatted_threshold = 0.1
        max_value_for_fixed_point = 1e8
        if cell_formatter is None:
            if self.matrix.dtype.kind in ['i', 'u']:  # signed, unsigned integer
                self.float_formatter = "{:d}".format
            elif self.matrix.dtype.kind == 'b': # boolean
                self.float_formatter = "{}".format
            elif self.matrix.dtype.kind == 'f':
                if self.max_val >= max_value_for_fixed_point:
                    self.float_formatter = "{:.6e}".format
                else:
                    if np.sum(np.logical_and(self.matrix != 0, np.abs(self.matrix) < 1e-4)) < small_formatted_threshold * np.product(self.matrix.shape):
                        # below 10% of the values is not looking nice with non-exponential format
                        self.float_formatter = "{:.6f}".format
                    else:
                        self.float_formatter = "{:.6e}".format  # use exponential format
            elif self.matrix.dtype.kind == 'c':  # complex float (there is no complex int)
                if (self.max_val.real >= max_value_for_fixed_point) or (self.max_val.imag >= max_value_for_fixed_point):
                    self.float_formatter = "{:.6e}".format
                else:
                    if ((np.sum(np.logical_and(self.matrix.real != 0, np.abs(self.matrix.real) < 1e-4))
                        < small_formatted_threshold * np.product(self.matrix.shape)) and
                        (np.sum(np.logical_and(self.matrix.imag != 0, np.abs(self.matrix.imag) < 1e-4))
                        < small_formatted_threshold * np.product(self.matrix.shape))):
                        # below 10% of both the imag and the real part is not looking nice with non-exponential format
                        self.float_formatter = "{:.6f}".format
                    else:
                        self.float_formatter = "{:.6e}".format  # use exponential format
            else:
                # use string formatter as fallback
                self.float_formatter = "{}".format
        else:
            self.float_formatter = cell_formatter

        self.column_heading_formatter = "{:d}".format
        self.row_heading_formatter = "{:d}".format
        self._font_changed()

        if self.num_dims == 1:
            ViewerTabTable.__init__(self, viewer, matrix_title, 1, self.matrix.shape[0], highlight_selected_columns=False)
        else:
            ViewerTabTable.__init__(self, viewer, matrix_title, self.matrix.shape[1], self.matrix.shape[0])

        self.canvas1.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas1.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas1.bind("<Motion>", self._on_mouse_motion)

    def _font_changed(self):
        self.max_text_width = self.cell_font.measure('0' + self.float_formatter(self.max_val))  # add trailing 0 as a placeholder for better readability
        self.row_heading_text_width = self.cell_font.measure("0" * (len(str(self.matrix.shape[0] - 1))))

    def _on_mouse_press(self, event):
        if (self._selection is not None) and (event.state & 0x01 == 0x01):  # shift pressed
            self.mouse_press_start = self.old_mouse_press_start  # if we start selecting a rectangle by moving the holded mouse to the right, then release the mouse button, and then press shift on a point left to the rectangle, the start point is needed because we do correct the actual selection rectangle so that end > start
            if self.mouse_press_start is not None:
                self._adjust_selection(event)
        else:
            self.mouse_press_start = None
            hit_x, hit_y = self._calc_hit_cell(event.x, event.y)

            if hit_x is None:
                self._selection = None
                self._focused_cell = None
            elif (hit_x == -1) and (hit_y == -1):
                self._selection = [0, 0, self.xscroll_items, self.yscroll_items]
            elif hit_x == -1:
                self._selection = [0, hit_y, self.xscroll_items, hit_y + 1]
                self._focused_cell = [0, hit_y]
                self.mouse_press_start = [-1, hit_y]
            elif hit_y == -1:
                self._selection = [hit_x, 0, hit_x + 1, self.yscroll_items]
                self._focused_cell = [hit_x, 0]
                self.mouse_press_start = [hit_x, -1]
            else:
                self._selection = [hit_x, hit_y, hit_x + 1, hit_y + 1]
                self._focused_cell = [hit_x, hit_y]
                self.mouse_press_start = [hit_x, hit_y]

        self._draw()

    def _on_mouse_release(self, event):
        self.old_mouse_press_start = self.mouse_press_start
        self.mouse_press_start = None

    def _on_mouse_motion(self, event):
        if self.mouse_press_start is not None:
            current_time = time.time()
            if self.last_autoscroll_time < current_time - self.autoscroll_delay:
                if self.mouse_press_start[0] != -1:
                    if event.x < self.row_heading_width:
                        self.xscroll_item = max(self.xscroll_item - 1, 0)
                        self._scroll_x()
                        self.last_autoscroll_time = current_time
                    elif event.x > self.row_heading_width + self.xscroll_page_size * self.cell_width:
                        self.xscroll_item = min(self.xscroll_item + 1, self.xscroll_max)
                        self._scroll_x()
                        self.last_autoscroll_time = current_time

                if self.mouse_press_start[1] != -1:
                    if event.y < self.cell_height:
                        self.yscroll_item = max(self.yscroll_item - 1, 0)
                        self._scroll_y()
                        self.last_autoscroll_time = current_time
                    elif event.y > self.cell_height + self.yscroll_page_size * self.cell_height:
                        self.yscroll_item = min(self.yscroll_item + 1, self.yscroll_max)
                        self._scroll_y()
                        self.last_autoscroll_time = current_time

            self._adjust_selection(event)
            self._draw()

    def _draw_cells(self):
        x = -self.cell_hpadding + self.row_heading_width
        y = self.cell_vpadding + self.cell_height
        for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
            self.canvas1.create_text(x, y, text=self.row_heading_formatter(i_row), font=self.cell_font, anchor='ne')
            y += self.cell_height
        x += self.cell_width

        if self.num_dims == 1:
            for i_column in range(self.xscroll_item, min(self.xscroll_item + self.xscroll_page_size + 1, self.xscroll_items)):
                y = self.cell_vpadding
                self.canvas1.create_text(x, y, text='Value', font=self.cell_font, anchor='ne')
                y += self.cell_height

                for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
                    self.canvas1.create_text(x, y, text=self.float_formatter(self.matrix[i_row]), font=self.cell_font, anchor='ne')
                    y += self.cell_height
                x += self.cell_width
        else:
            for i_column in range(self.xscroll_item, min(self.xscroll_item + self.xscroll_page_size + 1, self.xscroll_items)):
                y = self.cell_vpadding
                self.canvas1.create_text(x - self.max_text_width // 2, y, text=self.column_heading_formatter(i_column), font=self.cell_font, anchor='n')
                y += self.cell_height

                for i_row in range(self.yscroll_item, min(self.yscroll_item + self.yscroll_page_size + 1, self.yscroll_items)):
                    self.canvas1.create_text(x, y, text=self.float_formatter(self.matrix[i_row, i_column]), font=self.cell_font, anchor='ne')
                    y += self.cell_height
                x += self.cell_width

    def get_selection(self):
        """Get the current selected matrix area.

        :return: [start0, end0, start1, end1] so that matrix[start0:end0, start1:end1] represents the selected part.
                 If nothing was selected, returns None. If no area was explicitly selected, this is an 1x1 area representing the focused cell.
        """
        if self._selection is None:
            return None
        else:
            return [self._selection[1], self._selection[3], self._selection[0], self._selection[2]]

    def get_focused_cell(self):
        """Get the currently focused cell. This is the most recent cell that the user clicked on.
        If an area was selected that it drawn in blue, the focus cell is
        the cell with a white background inside the blue rectangle.

        :return: [index0, index1] so that matrix[index0, index1] represents the focused cell.
        """
        if self._focused_cell is None:
            return None
        else:
            return [self._focused_cell[1], self._focused_cell[0]]

def matches_tab_numpy(object):
    return ((isinstance(object, np.ndarray) and (object.ndim <= 2) and (object.dtype.isbuiltin == 1)) or
        ((type(object).__name__ == "Tensor") and (object.ndim <= 2)))  # pytorch