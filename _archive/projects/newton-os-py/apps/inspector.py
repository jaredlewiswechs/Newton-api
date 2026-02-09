"""
═══════════════════════════════════════════════════════════════
NINSPECTOR - OBJECT INSPECTOR
Browse and inspect all NObjects in TheGraph.
The equivalent of a file browser, but for objects.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLabel, QLineEdit, QPushButton, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from core.nobject import NObject
from core.graph import TheGraph
from shell.window import NWindow


class NInspector(NWindow):
    """
    The Object Inspector - browse TheGraph.
    
    Features:
    - Tree view of all objects by type
    - Property inspector
    - Relationship viewer
    - Live updates
    - Query interface
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(title="Inspector", width=600, height=450, parent=parent)
        
        self.add_tag('app')
        self.add_tag('inspector')
        self.set_property('app_name', 'Inspector')
        
        self._selected_object: Optional[NObject] = None
        
        self._setup_inspector_ui()
        self._setup_refresh_timer()
    
    def _setup_inspector_ui(self) -> None:
        """Setup the inspector interface."""
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Object tree
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search/filter
        search_layout = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Filter objects...")
        self._search_input.textChanged.connect(self._filter_objects)
        search_layout.addWidget(self._search_input)
        
        self._refresh_btn = QPushButton("↻")
        self._refresh_btn.setFixedWidth(30)
        self._refresh_btn.clicked.connect(self._refresh_tree)
        search_layout.addWidget(self._refresh_btn)
        
        left_layout.addLayout(search_layout)
        
        # Object tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Object", "Type"])
        self._tree.setColumnWidth(0, 200)
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #409cff;
                color: white;
            }
        """)
        left_layout.addWidget(self._tree)
        
        # Stats label
        self._stats_label = QLabel("0 objects")
        self._stats_label.setStyleSheet("color: #888; font-size: 11px;")
        left_layout.addWidget(self._stats_label)
        
        splitter.addWidget(left_panel)
        
        # Right panel - Details
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Object info header
        self._info_header = QLabel("Select an object")
        self._info_header.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                padding: 8px;
                background-color: #f5f5f7;
                border-radius: 4px;
            }
        """)
        right_layout.addWidget(self._info_header)
        
        # Properties display
        self._properties_text = QTextEdit()
        self._properties_text.setReadOnly(True)
        self._properties_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self._properties_text)
        
        # Relationships section
        self._relationships_label = QLabel("Relationships")
        self._relationships_label.setStyleSheet("font-weight: 600; margin-top: 8px;")
        right_layout.addWidget(self._relationships_label)
        
        self._relationships_text = QTextEdit()
        self._relationships_text.setReadOnly(True)
        self._relationships_text.setMaximumHeight(100)
        self._relationships_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        right_layout.addWidget(self._relationships_text)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 350])
        
        self.add_widget(splitter)
        
        # Initial load
        self._refresh_tree()
    
    def _setup_refresh_timer(self) -> None:
        """Setup auto-refresh timer."""
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_tree)
        self._refresh_timer.start(2000)  # Refresh every 2 seconds
    
    def _refresh_tree(self) -> None:
        """Refresh the object tree."""
        self._tree.clear()
        
        # Group objects by type
        by_type = {}
        for obj in TheGraph.get_all():
            obj_type = obj.object_type
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(obj)
        
        # Build tree
        for obj_type, objects in sorted(by_type.items()):
            type_item = QTreeWidgetItem([f"{obj_type} ({len(objects)})", ""])
            type_item.setData(0, Qt.ItemDataRole.UserRole, None)
            
            for obj in objects:
                # Get display name
                name = obj.get_property('name') or obj.get_property('title') or obj.id[:8]
                obj_item = QTreeWidgetItem([str(name), obj.object_type])
                obj_item.setData(0, Qt.ItemDataRole.UserRole, obj.id)
                type_item.addChild(obj_item)
            
            self._tree.addTopLevelItem(type_item)
            type_item.setExpanded(True)
        
        # Update stats
        total = TheGraph.count()
        self._stats_label.setText(f"{total} objects in graph")
    
    def _filter_objects(self, text: str) -> None:
        """Filter the tree based on search text."""
        text = text.lower()
        
        for i in range(self._tree.topLevelItemCount()):
            type_item = self._tree.topLevelItem(i)
            visible_children = 0
            
            for j in range(type_item.childCount()):
                child = type_item.child(j)
                obj_name = child.text(0).lower()
                obj_type = child.text(1).lower()
                
                matches = text in obj_name or text in obj_type
                child.setHidden(not matches)
                if matches:
                    visible_children += 1
            
            # Hide type if no visible children (unless searching empty)
            type_item.setHidden(visible_children == 0 and text != "")
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle item click."""
        obj_id = item.data(0, Qt.ItemDataRole.UserRole)
        if obj_id:
            obj = TheGraph.get(obj_id)
            if obj:
                self._show_object_details(obj)
    
    def _show_object_details(self, obj: NObject) -> None:
        """Display object details in the right panel."""
        self._selected_object = obj
        
        # Header
        name = obj.get_property('name') or obj.get_property('title') or 'Unnamed'
        self._info_header.setText(f"{name}\n{obj.object_type} • {obj.id[:8]}...")
        
        # Properties
        props_text = []
        props_text.append(f"ID: {obj.id}")
        props_text.append(f"Type: {obj.object_type}")
        props_text.append(f"Tags: {', '.join(obj.tags) or 'none'}")
        props_text.append(f"Verified: {obj.is_verified}")
        props_text.append("")
        props_text.append("Properties:")
        props_text.append("-" * 30)
        
        for prop_name in obj.list_properties():
            prop = obj.get_property_object(prop_name)
            if prop:
                value = prop.value
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                props_text.append(f"  {prop_name}: {value}")
        
        self._properties_text.setText("\n".join(props_text))
        
        # Relationships
        rels = TheGraph.get_relationships_for(obj.id)
        if rels:
            rel_text = []
            for rel in rels:
                direction = "→" if rel.source_id == obj.id else "←"
                other_id = rel.target_id if rel.source_id == obj.id else rel.source_id
                other = TheGraph.get(other_id)
                other_name = other.get_property('name') if other else other_id[:8]
                rel_text.append(f"  {direction} {rel.type}: {other_name}")
            self._relationships_text.setText("\n".join(rel_text))
        else:
            self._relationships_text.setText("  No relationships")
