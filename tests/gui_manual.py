
# This is the actual GUI test file used when adding features etc.
# Its a bit dumb (no fancy frameworks but manual input), but at least it's simple.

import os
import sys
sys.path.append(os.getcwd())  # to be able to include matrix_viewer

import numpy as np
import matrix_viewer
import matplotlib
import platform
import torchvision

def open_with_pyplot(backend='TkAgg'):
    import matplotlib.pyplot as plt
    matplotlib.use(backend)
    assert matplotlib.get_backend() == backend, f"{matplotlib.get_backend()} {backend}"

    matrix_viewer.view(np.random.rand(10, 5))
    matrix_viewer.view(['a', 'b', 3])
    plt.plot(np.random.rand(10))
    matrix_viewer.show_with_pyplot()

def test_pyplot_interoperability():
    print('TEST test_pyplot_interoperability')
    print('TEST: numpy and matrix_viewer react to scrolling etc?')
    print('TEST: Close the matrix viewer window first.')
    print('TEST: Pyplot still open? Loop stops if pyplot closed?')
    open_with_pyplot('TkAgg')

    print('TEST: Close the pyplot viewer window first.')
    print('TEST: Matrix_viewer still open? Loop stops if matrix_viewer closed?')
    open_with_pyplot('TkAgg')

def test_pyplot_interoperability_gtkagg():
    # on linux, the following is needed:
    # pycairo>=1.16.0
    # pygobject==3.42.0

    print('TEST test_pyplot_interoperability_gtkagg')
    print('TEST: Close the matrix viewer window first.')
    print('TEST: Pyplot still open? Loop stops if pyplot closed?')
    open_with_pyplot('GTK3Agg')

    print('TEST: Close the pyplot viewer window first.')
    print('TEST: Matrix_viewer still open? Loop stops if matrix_viewer closed?')
    open_with_pyplot('GTK3Agg')

def test_struct_strings():
    print('TEST test_struct_strings')
    print('TEST: No def or ghi visible?')
    matrix_viewer.view(['a', 'abc\ndef\nghi'])
    matrix_viewer.show()

def test_struct_empty():
    print('TEST test_struct_empty')
    print('TEST: No error messages / exceptions?')
    matrix_viewer.view([])
    matrix_viewer.show()

def test_multiple_windows():
    print('TEST test_multiple_windows')
    print('TEST: Window "Matrix Viewer" has 1 tabs and window "Second Window" has 2 tabs?')
    print('TEST: Tab allows horizontal and vertical scrolling by using the mouse wheel?')
    print('TEST: Font size can be changed dynamically with Ctrl-Scroll?')
    matrix_viewer.view(np.random.rand(100, 100))
    v1 = matrix_viewer.viewer('Second Window')
    matrix_viewer.view(v1)
    matrix_viewer.view(np.random.rand(5, 5))
    matrix_viewer.show()

def test_pytorch():
    print('TEST test_pytorch')
    print('TEST: click on a few parameters')
    model = torchvision.models.vgg16(pretrained=False)
    matrix_viewer.view(dict(model.named_parameters()))
    matrix_viewer.show()

test_pyplot_interoperability()
if platform.system() == 'Linux':
    test_pyplot_interoperability_gtkagg()
test_struct_strings()
test_struct_empty()
test_multiple_windows()
test_pytorch()