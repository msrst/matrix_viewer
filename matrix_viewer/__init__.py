"""Top-level package for Matrix Viewer."""

__author__ = """Matthias Rosenthal"""
__version__ = '0.2.0'

from ._window import pause, show, show_with_pyplot, view, viewer, Viewer
from ._tab import ViewerTab
from ._tab_numpy import ViewerTabNumpy
from ._tab_struct import ViewerTabStruct
from ._tab_text import ViewerTabText

__all__ = [
    'pause',
    'show',
    'show_with_pyplot',
    'view',
    'viewer',
    'Viewer',
    'ViewerTab',
    'ViewerTabNumpy',
    'ViewerTabStruct',
    'ViewerTabText',
]
