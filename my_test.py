import matrix_viewer
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # GTK3Agg
import matplotlib.pyplot as plt
import time

v = matrix_viewer.view(np.random.rand(10000, 15000) ** 5 * 100)

plt.plot(np.random.rand(5))
matrix_viewer.show_with_pyplot()