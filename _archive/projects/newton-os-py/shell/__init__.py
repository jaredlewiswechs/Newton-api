"""
═══════════════════════════════════════════════════════════════
SHELL - NEWTON OS UI COMPONENTS
═══════════════════════════════════════════════════════════════
"""

from .window import NWindow
from .dock import NDock, DockItem
from .desktop import NDesktop
from .menubar import NMenuBar

__all__ = ['NWindow', 'NDock', 'DockItem', 'NDesktop', 'NMenuBar']
