"""
═══════════════════════════════════════════════════════════════════════════════
realTinyTalk BACKENDS
Multiple compilation targets from the same AST
═══════════════════════════════════════════════════════════════════════════════
"""

from .js.emitter import JSEmitter, compile_to_js

__all__ = ['JSEmitter', 'compile_to_js']
