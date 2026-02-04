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
    builtin_card_set,
    builtin_card_save,
    builtin_card_delete,
    builtin_card_props,
    
    # Query builtins
    builtin_query_all,
    builtin_query_where,
    builtin_query_select,
    builtin_query_first,
    builtin_query_count,
    builtin_query_sort,
    builtin_query_distinct,
    
    # Services builtins
    builtin_services_register,
    builtin_services_get,
    builtin_services_call,
    builtin_services_list,
    
    # Inspector builtins
    builtin_inspector_type,
    builtin_inspector_props,
    builtin_inspector_validate,
    builtin_inspector_diff,
    
    # Workspace builtins
    builtin_workspace_list,
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
