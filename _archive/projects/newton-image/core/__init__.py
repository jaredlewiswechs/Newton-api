"""
═══════════════════════════════════════════════════════════════
NEWTON IMAGE - CORE MODULE
Image editing primitives built on NObject architecture.
Every layer, every stroke, every pixel - verified.
═══════════════════════════════════════════════════════════════
"""

from .document import NDocument, NLayer, LayerType, BlendMode
from .history import NHistory, NHistoryEntry, HistoryAction
from .tools import (
    NTool, ToolType, ToolState,
    NBrushTool, NEraserTool, NSelectTool, NMoveTool, 
    NRectSelectTool, NTextTool, NEyedropperTool
)
from .filters import NFilter, FilterType

__all__ = [
    'NDocument', 'NLayer', 'LayerType', 'BlendMode',
    'NHistory', 'NHistoryEntry', 'HistoryAction',
    'NTool', 'ToolType', 'ToolState',
    'NBrushTool', 'NEraserTool', 'NSelectTool', 'NMoveTool',
    'NRectSelectTool', 'NTextTool', 'NEyedropperTool',
    'NFilter', 'FilterType'
]
