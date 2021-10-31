import matrix_viewer
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # GTK3Agg
import matplotlib.pyplot as plt
import time

v = matrix_viewer.view(np.random.rand(100, 150) ** 5 * 100)
v2 = matrix_viewer.view(np.random.rand(50, 66) ** 5 * 100)
v4 = matrix_viewer.view({'a': 'la le lu', 'lala': 123, 'blubbi': np.random.rand(10, 12)})
matrix_viewer.viewer()
v3 = matrix_viewer.view(np.random.rand(55, 66) ** 5 * 100)
v3 = matrix_viewer.view(np.random.rand(3, 4) ** 5 * 100)

matrix_viewer.show_with_pyplot()