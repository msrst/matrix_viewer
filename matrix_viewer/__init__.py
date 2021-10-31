"""Top-level package for Matrix Viewer."""

__author__ = """Matthias Rosenthal"""
__version__ = '0.1.0'

from ._window import pause, show, show_with_pyplot, view, viewer, Viewer
from ._tab_numpy import ViewerTabNumpy
from ._tab_struct import ViewerTabStruct

__all__ = [
    'pause',
    'show',
    'show_with_pyplot',
    'view',
    'viewer',
    'Viewer',
    'ViewerTabNumpy',
    'ViewerTabStruct'
]
