
import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import math

def clip(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value

class Viewer():
    # TODO implement mouse wheel scroll
    # TODO make scrollbars less weird (use page size for scroll nibble, resolve problem that causes an empty extra column)
    def __init__(self, matrix):
        self.matrix = matrix

        self.font_size = 15

    def run(self):
        root  = tk.Tk()
        root.title('Matrix Viewer')
        root.geometry('500x500')
        root['bg'] = '#AC99F2'

        self.cell_font = tk.font.Font(size=self.font_size, family="Helvetica")  # default root window needed to create font
        self.calc_dimensions()

        f1 = tk.Frame(root)
        f2 = tk.Frame(root)

        f1.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        self.canvas1 = tk.Canvas(f1, width=20)

        self.canvas1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_lines = np.array([10, 20, 300, 400, 30, 50, 330, 450])
        self.canvas1.create_line(table_lines.tolist())
        # self.canvas1["scrollregion"] = [0, 0, 500, 1000]  # left, top, right, bottom corner of scrollable field
        self.canvas1.bind("<Configure>", self.on_resize)

        self.xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.on_x_scroll)  # TODO how do I set scroll limits and step size? (it must be possible, compare for using scrollbar in conjunction with treeview)
        self.xscrollbar.grid(column=0, rows=1, sticky="ew")
        print(self.xscrollbar.keys())
        print(self.xscrollbar["relief"], self.xscrollbar["repeatdelay"], self.xscrollbar["repeatinterval"], self.xscrollbar.get())
        self.yscrollbar = tk.Scrollbar(f1, orient=tk.VERTICAL, command=self.on_y_scroll)
        self.yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        f2.grid(column=0, row=2, sticky="n")
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
        tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

        root.mainloop()

    def calc_dimensions(self):
        # TODO determine optimal format here depending on matrix type and appropriately calculate max text width
        # (e.g. integer / floating point format, exp format vs. 0.00000)
        self.float_formatter = "{:.6f}".format
        self.max_text_width = self.cell_font.measure(self.float_formatter(1234.5678))

        self.cell_vpadding = 2
        self.cell_hpadding = 2
        self.cell_height = self.font_size + self.cell_vpadding * 2
        self.cell_width = self.max_text_width + self.cell_hpadding * 2
        self.row_heading_width = self.cell_font.measure(self.float_formatter(self.matrix.shape[0])) + self.cell_hpadding * 2
        self.xscroll_items = self.matrix.shape[1] + 1
        self.yscroll_items = self.matrix.shape[0] + 1
        self.xscroll_item = 0
        self.yscroll_item = 0

    def calc_size_scroll(self, init):
        self.xscroll_max = max(self.xscroll_items - self.size_x // self.cell_width, 0)
        if self.xscroll_max == 0:
            if self.row_heading_width + self.xscroll_items * self.cell_width > self.size_x:
                self.xscroll_max = 1  # if first column (the row headings) is larger than expected
        elif self.xscroll_max == 1:
            if self.row_heading_width + self.xscroll_items * self.cell_width <= self.size_x:
                self.xscroll_max = 0  # if first column (the row headings) is smaller than expected
        self.xscroll_item = min(self.xscroll_item, self.xscroll_max)
        if self.xscroll_max == 0:
            self.xscrollbar.set(0, 1)
        else:
            self.xscrollbar.set(self.xscroll_item / (self.xscroll_max + 1), (self.xscroll_item + 1) / (self.xscroll_max + 1))

        self.yscroll_max = max(self.yscroll_items - self.size_y // self.cell_height, 0)  # cell_height is equal to the heading height which facilitates yscroll calculations
        self.yscroll_item = min(self.yscroll_item, self.yscroll_max)
        if self.yscroll_max == 0:
            self.yscrollbar.set(0, 1)
        else:
            self.yscrollbar.set(self.yscroll_item / (self.yscroll_max + 1), (self.yscroll_item + 1) / (self.yscroll_max + 1))

    def on_x_scroll(self, *args):
        new_xscroll_item = None
        if args[0] == 'scroll':
            if args[2] == 'units':
                new_xscroll_item = clip(self.xscroll_item + int(args[1]), 0, self.xscroll_max)
            elif args[2] == 'pages':
                items_per_page = self.size_x // self.cell_width
                new_xscroll_item = clip(self.xscroll_item + int(args[1]) * items_per_page, 0, self.xscroll_max)
        elif args[0] == 'moveto':
            desired_fraction = float(args[1])  # desired scroll position from 0 to 1
            new_xscroll_item = clip(math.floor(desired_fraction * (self.xscroll_max + 1) + 0.5), 0, self.xscroll_max)

        if (new_xscroll_item is not None) and (new_xscroll_item != self.xscroll_item):
            self.xscroll_item = new_xscroll_item
            self.xscrollbar.set(self.xscroll_item / (self.xscroll_max + 1), (self.xscroll_item + 1) / (self.xscroll_max + 1))
            self.draw()

    def on_y_scroll(self, *args):
        new_yscroll_item = None
        if args[0] == 'scroll':
            if args[2] == 'units':
                new_yscroll_item = clip(self.yscroll_item + int(args[1]), 0, self.yscroll_max)
            elif args[2] == 'pages':
                items_per_page = self.size_y // self.cell_width
                new_yscroll_item = clip(self.yscroll_item + int(args[1]) * items_per_page, 0, self.yscroll_max)
        elif args[0] == 'moveto':
            desired_fraction = float(args[1])  # desired scroll position from 0 to 1
            new_yscroll_item = clip(math.floor(desired_fraction * (self.yscroll_max + 1) + 0.5), 0, self.yscroll_max)

        if (new_yscroll_item is not None) and (new_yscroll_item != self.yscroll_item):
            self.yscroll_item = new_yscroll_item
            self.yscrollbar.set(self.yscroll_item / (self.yscroll_max + 1), (self.yscroll_item + 1) / (self.yscroll_max + 1))
            self.draw()

    def on_resize(self, event):
        self.size_x = event.width
        self.size_y = event.height
        self.calc_size_scroll(False)
        self.draw()

    def draw(self):
        self.canvas1.delete('all')

        x = self.cell_hpadding + self.row_heading_width + self.cell_width
        x_items_per_page = self.size_x // self.cell_width
        y_items_per_page = self.size_y // self.cell_height
        current_x_item = self.xscroll_item
        if current_x_item == 0:
            current_x_item += 1   # TODO draw row headings
        for i_column in range(current_x_item, min(current_x_item + x_items_per_page, self.matrix.shape[1] - 1)):
            y = self.cell_vpadding * 3 + self.cell_height
            current_y_item = self.yscroll_item
            if current_y_item == 0:
                current_y_item += 1  # TODO draw column headings
            for i_row in range(current_y_item, min(current_y_item + y_items_per_page, self.matrix.shape[0] - 1)):
                print(i_row, i_column, self.matrix.shape)
                self.canvas1.create_text(x, y, text=self.float_formatter(self.matrix[i_row, i_column]), font=self.cell_font, anchor='ne')
                y += self.cell_height
            x += self.cell_width

def helo(matrix):
    viewer = Viewer(matrix)
    viewer.run()

def helo3(matrix):
    root  = tk.Tk()
    root.title('Matrix Viewer')
    root.geometry('500x500')
    root['bg'] = '#AC99F2'

    f1 = tk.Frame(root)
    f2 = tk.Frame(root)

    f1.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    canvas1 = tk.Canvas(f1, width=20)

    canvas1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    table_lines = np.array([10, 20, 300, 400, 30, 50, 330, 450])
    canvas1.create_line(table_lines.tolist())
    canvas1["scrollregion"] = [0, 0, 500, 1000]  # left, top, right, bottom corner of scrollable field

    xscrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas1.xview)
    xscrollbar.grid(column=0, rows=1, sticky="ew")
    yscrollbar = tk.Scrollbar(f1, orient=tk.VERTICAL, command=canvas1.yview)
    yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas1["xscrollcommand"] = xscrollbar.set
    canvas1["yscrollcommand"] = yscrollbar.set

    font_size = 15
    my_font = tk.font.Font(size=font_size, family="Helvetica")
    float_formatter = "{:.6f}".format
    text_width = my_font.measure(float_formatter(1234.5678)) + 5
    y = 10
    for i_row in range(matrix.shape[0]):
        x = 10 + text_width
        for i_column in range(matrix.shape[1]):
            canvas1.create_text(x, y, text=float_formatter(matrix[i_row][i_column]), font=my_font, anchor='e')
            x += text_width
        y += font_size + 1

    f2.grid(column=0, row=2, sticky="n")
    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

    root.mainloop()

def helo2():
    # def killme():
    #     root.quit()
    #     root.destroy()

    # root=tk.Tk()

    # lb=tk.Text(root, width=16, height=5)

    # lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

    # yscrollbar=tk.Scrollbar(root, orient=tk.VERTICAL, command=lb.yview)
    # yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    # lb["yscrollcommand"]=yscrollbar.set

    # root.mainloop()

    root  = tk.Tk()
    root.title('Matrix Viewer')
    root.geometry('500x500')
    root['bg'] = '#AC99F2'

    f1 = tk.Frame(root)
    f2 = tk.Frame(root)

    f1.grid(column=0, row=0, sticky="nsew")  # sticky: north south east west, specify which sides the inner widget should be tuck to
    f2.grid(column=0, row=1, sticky="n")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    data_table1 = ttk.Treeview(f1, height=50)

    data_table1['columns'] = ('player_id', 'player_name', 'player_Rank', 'player_states', 'player_city')

    data_table1.column("#0", width=0,  stretch=tk.NO)
    data_table1.column("player_id",anchor=tk.CENTER, width=80)
    data_table1.column("player_name",anchor=tk.CENTER,width=80)
    data_table1.column("player_Rank",anchor=tk.CENTER,width=80)
    data_table1.column("player_states",anchor=tk.CENTER,width=80)
    data_table1.column("player_city",anchor=tk.CENTER,width=80)

    data_table1.heading("#0",text="",anchor=tk.CENTER)
    data_table1.heading("player_id",text="Id",anchor=tk.CENTER)
    data_table1.heading("player_name",text="Name",anchor=tk.CENTER)
    data_table1.heading("player_Rank",text="Rank",anchor=tk.CENTER)
    data_table1.heading("player_states",text="States",anchor=tk.CENTER)
    data_table1.heading("player_city",text="States",anchor=tk.CENTER)

    data_table1.insert(parent='',index='end',iid=0,text='',
    values=('1','Ninja','101','Oklahoma', 'Moore'))
    data_table1.insert(parent='',index='end',iid=1,text='',
    values=('2','Ranger','102','Wisconsin', 'Green Bay'))
    data_table1.insert(parent='',index='end',iid=2,text='',
    values=('3','Deamon','103', 'California', 'Placentia'))
    data_table1.insert(parent='',index='end',iid=3,text='',
    values=('4','Dragon','104','New York' , 'White Plains'))
    data_table1.insert(parent='',index='end',iid=4,text='',
    values=('5','CrissCross','105','California', 'San Diego'))
    data_table1.insert(parent='',index='end',iid=5,text='',
    values=('6','ZaqueriBlack','106','Wisconsin' , 'TONY'))

    data_table1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    yscrollbar = tk.Scrollbar(f1, orient=tk.VERTICAL, command=data_table1.yview)
    yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    data_table1["yscrollcommand"] = yscrollbar.set

    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)
    tk.Button(f2, text="DAT BUTTON IS IN F2").pack(side=tk.LEFT)

    root.mainloop()