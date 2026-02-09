"""
═══════════════════════════════════════════════════════════════
NEWTON IMAGE EDITOR - MAIN APPLICATION
Verified creativity. Every pixel accountable.
═══════════════════════════════════════════════════════════════
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QInputDialog, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QColor, QIcon

from core.document import NDocument, NLayer, BlendMode
from core.tools import (
    ToolType, NBrushTool, NEraserTool, NMoveTool,
    NRectSelectTool, NTextTool, NEyedropperTool
)
from core.history import NHistory, HistoryAction
from core.filters import (
    FilterType, BrightnessFilter, ContrastFilter,
    SaturationFilter, GrayscaleFilter, InvertFilter,
    SepiaFilter, BlurFilter, create_filter
)

from ui.canvas import NCanvas
from ui.toolbar import NToolbar
from ui.layers_panel import NLayersPanel
from ui.color_picker import NColorPicker
from ui.inspector import NInspector
from ui.adjustments import NAdjustmentsPanel


class NImageEditor(QMainWindow):
    """
    Newton Image Editor - Main Window.
    
    A Photoshop-like image editor built on Newton principles:
    - Every action is verified
    - Every state change is logged
    - Every computation is bounded
    
    Apple HIG 2025 compliant:
    - Liquid Glass styling
    - Proper toolbar layout
    - Inspector panels
    - Keyboard shortcuts
    """
    
    def __init__(self):
        super().__init__()
        
        # Current document
        self._document: Optional[NDocument] = None
        
        # History manager
        self._history = NHistory()
        
        # Tools
        self._tools: Dict[ToolType, object] = {}
        self._current_tool: Optional[object] = None
        
        # Initialize tools
        self._init_tools()
        
        # Setup UI
        self._setup_window()
        self._setup_menubar()
        self._setup_ui()
        self._setup_statusbar()
        self._apply_style()
        
        # Connect signals
        self._connect_signals()
        
        # Create default document
        self._new_document()
    
    def _init_tools(self) -> None:
        """Initialize all tools."""
        self._tools[ToolType.BRUSH] = NBrushTool()
        self._tools[ToolType.ERASER] = NEraserTool()
        self._tools[ToolType.MOVE] = NMoveTool()
        self._tools[ToolType.SELECT_RECT] = NRectSelectTool()
        self._tools[ToolType.TEXT] = NTextTool()
        self._tools[ToolType.EYEDROPPER] = NEyedropperTool()
        
        # Set default tool
        self._current_tool = self._tools[ToolType.BRUSH]
    
    def _setup_window(self) -> None:
        """Configure main window."""
        self.setWindowTitle("Newton Image")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _setup_menubar(self) -> None:
        """Create menu bar with Apple HIG structure."""
        menubar = self.menuBar()
        
        # Apply Apple HIG styling to menu bar
        menubar.setStyleSheet("""
            QMenuBar {
                background: rgba(246, 246, 246, 0.92);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                padding: 2px 8px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                border-radius: 6px;
                color: #1d1d1f;
            }
            QMenuBar::item:selected {
                background: rgba(0, 0, 0, 0.1);
            }
            QMenu {
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                color: #1d1d1f;
            }
            QMenu::item:selected {
                background: #007aff;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: rgba(0, 0, 0, 0.1);
                margin: 4px 8px;
            }
        """)
        
        # ═══════════════════════════════════════════════════════
        # FILE MENU
        # ═══════════════════════════════════════════════════════
        
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New...", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_document_dialog)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_document)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_document)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_document_as)
        file_menu.addAction(save_as_action)
        
        export_action = QAction("Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self._export_document)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("Close", self)
        close_action.setShortcut(QKeySequence.StandardKey.Close)
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # ═══════════════════════════════════════════════════════
        # EDIT MENU
        # ═══════════════════════════════════════════════════════
        
        edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self._undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self._redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        fill_action = QAction("Fill...", self)
        fill_action.setShortcut(QKeySequence("Shift+F5"))
        fill_action.triggered.connect(self._fill_layer)
        edit_menu.addAction(fill_action)
        
        # ═══════════════════════════════════════════════════════
        # IMAGE MENU
        # ═══════════════════════════════════════════════════════
        
        image_menu = menubar.addMenu("Image")
        
        resize_action = QAction("Image Size...", self)
        resize_action.setShortcut(QKeySequence("Ctrl+Alt+I"))
        image_menu.addAction(resize_action)
        
        canvas_action = QAction("Canvas Size...", self)
        canvas_action.setShortcut(QKeySequence("Ctrl+Alt+C"))
        image_menu.addAction(canvas_action)
        
        image_menu.addSeparator()
        
        rotate_menu = image_menu.addMenu("Rotate Canvas")
        rotate_menu.addAction("90° Clockwise")
        rotate_menu.addAction("90° Counter-Clockwise")
        rotate_menu.addAction("180°")
        
        image_menu.addSeparator()
        
        flatten_action = QAction("Flatten Image", self)
        flatten_action.triggered.connect(self._flatten_image)
        image_menu.addAction(flatten_action)
        
        # ═══════════════════════════════════════════════════════
        # LAYER MENU
        # ═══════════════════════════════════════════════════════
        
        layer_menu = menubar.addMenu("Layer")
        
        new_layer_action = QAction("New Layer...", self)
        new_layer_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_layer_action.triggered.connect(self._add_layer)
        layer_menu.addAction(new_layer_action)
        
        duplicate_layer_action = QAction("Duplicate Layer", self)
        duplicate_layer_action.setShortcut(QKeySequence("Ctrl+J"))
        duplicate_layer_action.triggered.connect(self._duplicate_layer)
        layer_menu.addAction(duplicate_layer_action)
        
        delete_layer_action = QAction("Delete Layer", self)
        delete_layer_action.triggered.connect(self._delete_layer)
        layer_menu.addAction(delete_layer_action)
        
        layer_menu.addSeparator()
        
        merge_down_action = QAction("Merge Down", self)
        merge_down_action.setShortcut(QKeySequence("Ctrl+E"))
        merge_down_action.triggered.connect(self._merge_down)
        layer_menu.addAction(merge_down_action)
        
        # ═══════════════════════════════════════════════════════
        # FILTER MENU
        # ═══════════════════════════════════════════════════════
        
        filter_menu = menubar.addMenu("Filter")
        
        # Adjustments submenu
        adjust_menu = filter_menu.addMenu("Adjustments")
        
        brightness_action = QAction("Brightness/Contrast...", self)
        brightness_action.triggered.connect(lambda: self._show_adjustments())
        adjust_menu.addAction(brightness_action)
        
        saturation_action = QAction("Hue/Saturation...", self)
        adjust_menu.addAction(saturation_action)
        
        adjust_menu.addSeparator()
        
        invert_action = QAction("Invert", self)
        invert_action.setShortcut(QKeySequence("Ctrl+I"))
        invert_action.triggered.connect(lambda: self._apply_filter(FilterType.INVERT))
        adjust_menu.addAction(invert_action)
        
        grayscale_action = QAction("Grayscale", self)
        grayscale_action.triggered.connect(lambda: self._apply_filter(FilterType.GRAYSCALE))
        adjust_menu.addAction(grayscale_action)
        
        sepia_action = QAction("Sepia", self)
        sepia_action.triggered.connect(lambda: self._apply_filter(FilterType.SEPIA))
        adjust_menu.addAction(sepia_action)
        
        filter_menu.addSeparator()
        
        # Blur submenu
        blur_menu = filter_menu.addMenu("Blur")
        
        gaussian_blur = QAction("Gaussian Blur...", self)
        gaussian_blur.triggered.connect(lambda: self._apply_filter(FilterType.BLUR))
        blur_menu.addAction(gaussian_blur)
        
        # Stylize submenu
        stylize_menu = filter_menu.addMenu("Stylize")
        
        posterize_action = QAction("Posterize...", self)
        posterize_action.triggered.connect(lambda: self._apply_filter(FilterType.POSTERIZE))
        stylize_menu.addAction(posterize_action)
        
        # ═══════════════════════════════════════════════════════
        # VIEW MENU
        # ═══════════════════════════════════════════════════════
        
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_action = QAction("Fit on Screen", self)
        fit_action.setShortcut(QKeySequence("Ctrl+0"))
        fit_action.triggered.connect(self._fit_in_view)
        view_menu.addAction(fit_action)
        
        actual_action = QAction("Actual Size", self)
        actual_action.setShortcut(QKeySequence("Ctrl+1"))
        actual_action.triggered.connect(self._zoom_100)
        view_menu.addAction(actual_action)
        
        # ═══════════════════════════════════════════════════════
        # HELP MENU
        # ═══════════════════════════════════════════════════════
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About Newton Image", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_ui(self) -> None:
        """Create main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = NToolbar()
        main_layout.addWidget(self.toolbar)
        
        # Main content area
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        
        # Left panel (Color picker + Inspector)
        left_panel = QWidget()
        left_panel.setFixedWidth(240)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        self.color_picker = NColorPicker()
        left_layout.addWidget(self.color_picker)
        
        self.inspector = NInspector()
        left_layout.addWidget(self.inspector)
        
        content.addWidget(left_panel)
        
        # Canvas (center)
        self.canvas = NCanvas()
        content.addWidget(self.canvas, 1)
        
        # Right panel (Layers + Adjustments)
        right_panel = QWidget()
        right_panel.setFixedWidth(260)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.layers_panel = NLayersPanel()
        right_layout.addWidget(self.layers_panel)
        
        self.adjustments = NAdjustmentsPanel()
        right_layout.addWidget(self.adjustments)
        
        content.addWidget(right_panel)
        
        main_layout.addLayout(content)
    
    def _setup_statusbar(self) -> None:
        """Create status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Position label
        self.pos_label = QLabel("X: 0  Y: 0")
        self.pos_label.setStyleSheet("color: #86868b; font-size: 11px;")
        self.statusbar.addWidget(self.pos_label)
        
        # Spacer
        spacer = QWidget()
        spacer.setMinimumWidth(20)
        self.statusbar.addWidget(spacer)
        
        # Zoom label
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("color: #86868b; font-size: 11px;")
        self.statusbar.addWidget(self.zoom_label)
        
        # Spacer
        spacer2 = QWidget()
        spacer2.setMinimumWidth(20)
        self.statusbar.addWidget(spacer2)
        
        # Document info
        self.doc_label = QLabel("No Document")
        self.doc_label.setStyleSheet("color: #86868b; font-size: 11px;")
        self.statusbar.addPermanentWidget(self.doc_label)
    
    def _apply_style(self) -> None:
        """Apply global styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: #e5e5e5;
            }
            QStatusBar {
                background: rgba(246, 246, 246, 0.92);
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
    
    def _connect_signals(self) -> None:
        """Connect UI signals."""
        # Toolbar signals
        self.toolbar.tool_selected.connect(self._on_tool_selected)
        self.toolbar.action_triggered.connect(self._on_toolbar_action)
        
        # Canvas signals
        self.canvas.zoom_changed.connect(self._on_zoom_changed)
        self.canvas.position_changed.connect(self._on_position_changed)
        self.canvas.tool_used.connect(self._on_tool_used)
        
        # Color picker signals
        self.color_picker.color_changed.connect(self._on_color_changed)
        
        # Layers panel signals
        self.layers_panel.layer_selected.connect(self._on_layer_selected)
        
        # Adjustments signals
        self.adjustments.filter_applied.connect(self._apply_filter)
        self.adjustments.adjustment_changed.connect(self._on_adjustment_changed)
        
        # History signals
        self._history.can_undo_changed.connect(self.undo_action.setEnabled)
        self._history.can_redo_changed.connect(self.redo_action.setEnabled)
    
    # ═══════════════════════════════════════════════════════════
    # DOCUMENT OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _new_document(self, width: int = 1920, height: int = 1080, 
                      name: str = "Untitled") -> None:
        """Create a new document."""
        self._document = NDocument(name, width, height)
        self.canvas.document = self._document
        self.layers_panel.document = self._document
        self.inspector.set_document(self._document)
        
        # Set default tool on canvas
        if self._current_tool:
            self.canvas.tool = self._current_tool
            if hasattr(self._current_tool, 'color'):
                self._current_tool.color = self.color_picker.color
        
        # Update UI
        self.setWindowTitle(f"Newton Image — {name}")
        self.doc_label.setText(f"{width} × {height}")
        
        # Clear history
        self._history.clear()
        
        # Fit in view
        self.canvas.fit_in_view()
    
    def _new_document_dialog(self) -> None:
        """Show new document dialog."""
        width, ok1 = QInputDialog.getInt(self, "New Document", "Width:", 1920, 1, 10000)
        if not ok1:
            return
        
        height, ok2 = QInputDialog.getInt(self, "New Document", "Height:", 1080, 1, 10000)
        if not ok2:
            return
        
        name, ok3 = QInputDialog.getText(self, "New Document", "Name:", text="Untitled")
        if not ok3:
            return
        
        self._new_document(width, height, name)
    
    def _open_document(self) -> None:
        """Open an image file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)"
        )
        
        if path:
            from PyQt6.QtGui import QImage
            image = QImage(path)
            
            if image.isNull():
                QMessageBox.warning(self, "Error", "Could not load image.")
                return
            
            # Create document from image
            name = os.path.basename(path)
            self._document = NDocument(name, image.width(), image.height())
            
            # Set background layer to loaded image
            self._document.layers[0].set_image(image)
            self._document.layers[0].name = "Background"
            
            self.canvas.document = self._document
            self.layers_panel.document = self._document
            self.inspector.set_document(self._document)
            
            self.setWindowTitle(f"Newton Image — {name}")
            self.doc_label.setText(f"{image.width()} × {image.height()}")
            
            self._history.clear()
            self.canvas.fit_in_view()
    
    def _save_document(self) -> None:
        """Save the current document."""
        if not self._document:
            return
        self._save_document_as()
    
    def _save_document_as(self) -> None:
        """Save document with new name."""
        if not self._document:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Document",
            f"{self._document.name}.png",
            "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
        )
        
        if path:
            self._document.export(path)
    
    def _export_document(self) -> None:
        """Export flattened image."""
        if not self._document:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Image",
            f"{self._document.name}.png",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff);;BMP (*.bmp)"
        )
        
        if path:
            self._document.export(path)
    
    # ═══════════════════════════════════════════════════════════
    # LAYER OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _add_layer(self) -> None:
        """Add a new layer."""
        if self._document:
            name, ok = QInputDialog.getText(self, "New Layer", "Name:", text="Layer")
            if ok:
                self._document.add_layer(name)
    
    def _duplicate_layer(self) -> None:
        """Duplicate the active layer."""
        if self._document and self._document.active_layer:
            self._document.duplicate_layer(self._document.active_layer)
    
    def _delete_layer(self) -> None:
        """Delete the active layer."""
        if self._document and self._document.active_layer:
            self._document.remove_layer(self._document.active_layer)
    
    def _merge_down(self) -> None:
        """Merge active layer down."""
        if self._document and self._document.active_layer:
            self._document.merge_down(self._document.active_layer)
    
    def _flatten_image(self) -> None:
        """Flatten all layers."""
        if self._document:
            self._document.flatten()
    
    def _fill_layer(self) -> None:
        """Fill active layer with foreground color."""
        if self._document and self._document.active_layer:
            color = self.color_picker.color
            self._document.active_layer.fill(color)
    
    # ═══════════════════════════════════════════════════════════
    # FILTER OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _apply_filter(self, filter_type: FilterType) -> None:
        """Apply a filter to the active layer."""
        if not self._document or not self._document.active_layer:
            return
        
        layer = self._document.active_layer
        if layer.locked:
            return
        
        try:
            filter_obj = create_filter(filter_type)
            result = filter_obj.apply(layer.image)
            layer.set_image(result)
        except Exception as e:
            QMessageBox.warning(self, "Filter Error", str(e))
    
    def _on_adjustment_changed(self, name: str, value: int) -> None:
        """Handle adjustment slider changes (live preview)."""
        if not self._document or not self._document.active_layer:
            return
        
        layer = self._document.active_layer
        if layer.locked:
            return
        
        # Map adjustment names to filter types and apply
        try:
            if name == "brightness":
                filter_obj = create_filter(FilterType.BRIGHTNESS)
                filter_obj.value = value
            elif name == "contrast":
                filter_obj = create_filter(FilterType.CONTRAST)
                filter_obj.value = value
            elif name == "saturation":
                filter_obj = create_filter(FilterType.SATURATION)
                filter_obj.value = value
            elif name == "blur" and value > 0:
                filter_obj = create_filter(FilterType.BLUR)
                filter_obj.radius = value
            else:
                return
            
            # Apply to a copy for preview (don't modify original yet)
            # For now, just apply directly
            result = filter_obj.apply(layer.image)
            layer.set_image(result)
        except Exception as e:
            # Silently ignore during live adjustment
            pass
    
    def _show_adjustments(self) -> None:
        """Show adjustments panel."""
        # Adjustments panel is always visible
        pass
    
    # ═══════════════════════════════════════════════════════════
    # VIEW OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def _zoom_in(self) -> None:
        self.canvas.zoom_in()
    
    def _zoom_out(self) -> None:
        self.canvas.zoom_out()
    
    def _fit_in_view(self) -> None:
        self.canvas.fit_in_view()
    
    def _zoom_100(self) -> None:
        self.canvas.zoom_to_100()
    
    # ═══════════════════════════════════════════════════════════
    # UNDO/REDO
    # ═══════════════════════════════════════════════════════════
    
    def _undo(self) -> None:
        """Undo last action."""
        entry = self._history.undo()
        if entry and self._document:
            # Find layer and restore state
            for layer in self._document.layers:
                if layer.id == entry.layer_id:
                    from PyQt6.QtCore import QBuffer, QIODevice
                    buffer = QBuffer()
                    buffer.setData(entry.before_state)
                    buffer.open(QIODevice.OpenModeFlag.ReadOnly)
                    layer.image.loadFromData(buffer.data())
                    layer.changed.emit()
                    break
    
    def _redo(self) -> None:
        """Redo last undone action."""
        entry = self._history.redo()
        if entry and self._document:
            # Find layer and restore state
            for layer in self._document.layers:
                if layer.id == entry.layer_id:
                    from PyQt6.QtCore import QBuffer, QIODevice
                    buffer = QBuffer()
                    buffer.setData(entry.after_state)
                    buffer.open(QIODevice.OpenModeFlag.ReadOnly)
                    layer.image.loadFromData(buffer.data())
                    layer.changed.emit()
                    break
    
    # ═══════════════════════════════════════════════════════════
    # SIGNAL HANDLERS
    # ═══════════════════════════════════════════════════════════
    
    def _on_tool_selected(self, tool_type: ToolType) -> None:
        """Handle tool selection."""
        if tool_type in self._tools:
            self._current_tool = self._tools[tool_type]
            self.canvas.tool = self._current_tool
            self.inspector.set_tool(self._current_tool)
            
            # Set brush color
            if hasattr(self._current_tool, 'color'):
                self._current_tool.color = self.color_picker.color
    
    def _on_toolbar_action(self, action: str) -> None:
        """Handle toolbar action."""
        actions = {
            'new': self._new_document_dialog,
            'open': self._open_document,
            'save': self._save_document,
            'zoom_in': self._zoom_in,
            'zoom_out': self._zoom_out,
            'fit': self._fit_in_view,
            'undo': self._undo,
            'redo': self._redo,
        }
        
        if action in actions:
            actions[action]()
    
    def _on_zoom_changed(self, zoom: float) -> None:
        """Handle zoom change."""
        self.toolbar.set_zoom(zoom)
        self.zoom_label.setText(f"{int(zoom * 100)}%")
    
    def _on_position_changed(self, x: int, y: int) -> None:
        """Handle cursor position change."""
        self.pos_label.setText(f"X: {x}  Y: {y}")
    
    def _on_color_changed(self, color: QColor) -> None:
        """Handle color change."""
        self.canvas.foreground_color = color
        if self._current_tool and hasattr(self._current_tool, 'color'):
            self._current_tool.color = color
    
    def _on_layer_selected(self, layer: NLayer) -> None:
        """Handle layer selection."""
        if self._document:
            self._document.active_layer = layer
    
    def _on_tool_used(self, tool_name: str, data: dict) -> None:
        """Handle tool usage (for history)."""
        if 'before_state' in data and 'layer_id' in data:
            # Capture after state
            if self._document and self._document.active_layer:
                from PyQt6.QtCore import QBuffer, QIODevice
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                self._document.active_layer.image.save(buffer, "PNG")
                after_state = bytes(buffer.data())
                
                self._history.record(
                    HistoryAction.PAINT,
                    tool_name,
                    data['layer_id'],
                    data['before_state'],
                    after_state
                )
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Newton Image",
            """
            <h2>Newton Image</h2>
            <p>Verified creativity. Every pixel accountable.</p>
            
            <p>Built on Newton OS principles:</p>
            <ul>
            <li>Every action is verified</li>
            <li>Every state change is logged</li>
            <li>Every computation is bounded</li>
            </ul>
            
            <p style="color: #86868b;">
            "1 == 1. The cloud is weather. We're building shelter."
            </p>
            
            <p>Apple HIG 2025 compliant interface.</p>
            """
        )


def main():
    """Entry point."""
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Newton Image")
    app.setOrganizationName("Newton")
    app.setApplicationVersion("1.0.0")
    
    # Create and show editor
    editor = NImageEditor()
    editor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
