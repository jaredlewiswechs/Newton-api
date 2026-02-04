"""
═══════════════════════════════════════════════════════════════
NINA STDLIB - Standard Library for TinyTalk Integration
═══════════════════════════════════════════════════════════════

Provides TinyTalk bindings for Nina Desktop kernel objects:
- Card, Query, Services, Inspector
- Workspace management
- Cross-object linking
"""

from .foghorn_bindings import (
    register_nina_stdlib,
    register_foghorn_stdlib,  # Backward compatibility alias
    FOGHORN_BUILTINS,
    
    # Card builtins
    builtin_card_new,
    builtin_card_get,
    builtin_card_all,
    
    # Query builtins
    builtin_query_new,
    
    # Services builtins
    builtin_services_list,
    builtin_services_run,
    builtin_services_for,
    
    # Inspector builtins
    builtin_inspect,
    
    # Command history builtins
    builtin_undo,
    builtin_redo,
    builtin_history,
    
    # Workspace builtins
    builtin_workspace_count,
    builtin_workspace_all,
    builtin_workspace_delete,
    
    # Link builtins
    builtin_link_new,
)

__all__ = [
    'register_nina_stdlib',
    'register_foghorn_stdlib',
    'FOGHORN_BUILTINS',
]
