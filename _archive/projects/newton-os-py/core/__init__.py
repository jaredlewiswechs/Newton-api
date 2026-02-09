"""
═══════════════════════════════════════════════════════════════
NEWTON OS - CORE
QObject-based verified object system
═══════════════════════════════════════════════════════════════
"""

from .nobject import NObject, NProperty, NRelationship
from .graph import NObjectGraph, TheGraph
from .shapes import Squircle, squircle_path

__all__ = [
    'NObject', 'NProperty', 'NRelationship',
    'NObjectGraph', 'TheGraph',
    'Squircle', 'squircle_path'
]
