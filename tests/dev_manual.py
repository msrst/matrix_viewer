# test file used during development

import os
import sys
from typing import OrderedDict
sys.path.append(os.getcwd())  # to be able to include matrix_viewer

import matrix_viewer
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # GTK3Agg
import matplotlib.pyplot as plt
import torch

torch_array = torch.rand(100, 150)
v = matrix_viewer.view(torch_array ** 5 * 100)
torch_array *= 0  # test if it is really copied
v2 = matrix_viewer.view(np.random.rand(100, 150, 30))
v4 = matrix_viewer.view({'a': 'la le lu', 'lala': 123, 'blubbi': np.random.rand(10, 12)})
matrix_viewer.viewer()
v3 = matrix_viewer.view(np.random.rand(55) ** 5 * 100)
v3 = matrix_viewer.view(np.random.rand(3, 4) ** 5 * 100, tab_title='lalala', font_size=40, formatter="{:.3f}".format)
v3 = matrix_viewer.view(np.random.rand(3, 4) ** 5 * 100 * (1e-3 + 1e-3j))
v3 = matrix_viewer.view(np.random.rand(50, 100) < 0.5)

torch_array = torch.complex(torch.rand(100, 150).to('cuda'), torch.rand(100, 150).to('cuda'))
v3 = matrix_viewer.view(torch_array)

v3 = matrix_viewer.view(OrderedDict({2: 'hello', 3: 'lala'}))

matrix_viewer.show_with_pyplot()