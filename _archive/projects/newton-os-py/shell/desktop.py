"""
═══════════════════════════════════════════════════════════════
NDESKTOP - THE DESKTOP ENVIRONMENT
The main shell that holds everything together.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, Dict, List, Callable, Type
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QScreen

from core.nobject import NObject
from core.graph import TheGraph
from .window import NWindow
from .dock import NDock
from .menubar import NMenuBar

import datetime


class NDesktop(QMainWindow):
    """
    The Newton OS Desktop - the main shell.
    
    Manages:
    - Menu bar (top)
    - Desktop area (center)
    - Dock (bottom)
    - Window management
    - App launching
    
    Uses composition for NObject instead of inheritance to avoid
    PyQt6 signal conflicts.
    """
    
    window_opened = pyqtSignal(object)  # NWindow
    window_closed = pyqtSignal(str)  # window_id
    app_launched = pyqtSignal(str)  # app_name
    
    def __init__(self):
        super().__init__()
        
        # Use composition for NObject
        self._nobject = NObject(object_type="NDesktop")
        
        self._nobject.add_tag('desktop')
        self._nobject.add_tag('system')
        self._nobject.set_property('name', 'Newton Desktop')
        
        # Window tracking
        self._windows: Dict[str, NWindow] = {}
        self._app_registry: Dict[str, Type] = {}
        self._running_apps: Dict[str, List[NWindow]] = {}
        
        # Setup
        self._setup_window()
        self._setup_ui()
        self._setup_clock()
        self._register_default_apps()
    
    def _setup_window(self) -> None:
        """Configure the main window."""
        self.setWindowTitle("Newton OS")
        
        # Full screen on primary display
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.setGeometry(geometry)
        
        # Background color (desktop gray)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #3d3d3d;
            }
        """)
    
    def _setup_ui(self) -> None:
        """Setup the desktop UI components."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Menu bar
        self._menubar = NMenuBar()
        self._menubar.menu_clicked.connect(self._on_menu_clicked)
        main_layout.addWidget(self._menubar)
        
        # Desktop area (where windows live)
        self._desktop_area = QWidget()
        self._desktop_area.setStyleSheet("background: transparent;")
        main_layout.addWidget(self._desktop_area, 1)
        
        # Dock container (centered at bottom)
        dock_container = QWidget()
        dock_layout = QHBoxLayout(dock_container)
        dock_layout.setContentsMargins(0, 0, 0, 12)
        dock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._dock = NDock()
        self._dock.app_launched.connect(self._on_app_launched)
        dock_layout.addWidget(self._dock)
        
        main_layout.addWidget(dock_container)
        
        # Setup default dock items
        self._setup_dock()
    
    def _setup_dock(self) -> None:
        """Add default items to the dock."""
        self._dock.add_item("Inspector", "🔍", QColor(64, 156, 255))
        self._dock.add_item("Console", "⌨", QColor(40, 40, 40))
        self._dock.add_item("Files", "📁", QColor(100, 180, 255))
        self._dock.add_item("Settings", "⚙", QColor(128, 128, 128))
    
    def _setup_clock(self) -> None:
        """Setup clock timer."""
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)  # Update every second
        self._update_clock()
    
    def _update_clock(self) -> None:
        """Update the menu bar clock."""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        self._menubar.set_clock(time_str)
    
    # ═══════════════════════════════════════════════════════════
    # APP REGISTRY
    # ═══════════════════════════════════════════════════════════
    
    def _register_default_apps(self) -> None:
        """Register built-in apps."""
        # Will be populated when apps are imported
        pass
    
    def register_app(self, name: str, app_class: Type) -> None:
        """Register an app class for launching."""
        self._app_registry[name] = app_class
    
    def _on_app_launched(self, app_name: str) -> None:
        """Handle app launch from dock."""
        self.launch_app(app_name)
    
    def launch_app(self, app_name: str) -> Optional[NWindow]:
        """Launch an app by name."""
        if app_name in self._app_registry:
            # Create app window
            app_class = self._app_registry[app_name]
            window = app_class()
        else:
            # Create generic window for unknown apps
            window = self._create_generic_app_window(app_name)
        
        if window:
            self._register_window(window, app_name)
            window.show()
            self.app_launched.emit(app_name)
            
            # Mark dock item as running
            dock_item = self._dock.get_item(app_name)
            if dock_item:
                dock_item.set_running(True)
        
        return window
    
    def _create_generic_app_window(self, app_name: str) -> NWindow:
        """Create a generic window for an app."""
        window = NWindow(title=app_name, parent=self._desktop_area)
        
        # Add placeholder content
        label = QLabel(f"App: {app_name}\n\nThis is a placeholder.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 14px;")
        window.add_widget(label)
        
        return window
    
    # ═══════════════════════════════════════════════════════════
    # WINDOW MANAGEMENT
    # ═══════════════════════════════════════════════════════════
    
    def _register_window(self, window: NWindow, app_name: str) -> None:
        """Register a window with the desktop."""
        window_id = window.id
        self._windows[window_id] = window
        
        # Track by app
        if app_name not in self._running_apps:
            self._running_apps[app_name] = []
        self._running_apps[app_name].append(window)
        
        # Connect signals
        window.closed.connect(lambda: self._on_window_closed(window_id, app_name))
        
        # Position window
        self._position_new_window(window)
        
        # Update menubar
        self._menubar.set_current_app(app_name)
        
        self.window_opened.emit(window)
    
    def _position_new_window(self, window: NWindow) -> None:
        """Position a new window on the desktop."""
        # Cascade from top-left
        count = len(self._windows)
        offset = 30 * (count % 10)
        
        # Get desktop area geometry
        area = self._desktop_area.geometry()
        
        x = area.x() + 50 + offset
        y = area.y() + 50 + offset
        
        window.move(x, y)
    
    def _on_window_closed(self, window_id: str, app_name: str) -> None:
        """Handle window close."""
        if window_id in self._windows:
            del self._windows[window_id]
        
        # Update running apps
        if app_name in self._running_apps:
            self._running_apps[app_name] = [
                w for w in self._running_apps[app_name] 
                if w.id != window_id
            ]
            
            # If no more windows for this app, mark as not running
            if not self._running_apps[app_name]:
                dock_item = self._dock.get_item(app_name)
                if dock_item:
                    dock_item.set_running(False)
        
        self.window_closed.emit(window_id)
    
    def get_windows(self) -> List[NWindow]:
        """Get all open windows."""
        return list(self._windows.values())
    
    def get_windows_for_app(self, app_name: str) -> List[NWindow]:
        """Get all windows for a specific app."""
        return self._running_apps.get(app_name, [])
    
    # ═══════════════════════════════════════════════════════════
    # MENU HANDLING
    # ═══════════════════════════════════════════════════════════
    
    def _on_menu_clicked(self, menu: str, item: str) -> None:
        """Handle menu item clicks."""
        if menu == "Newton":
            if item == "About":
                self._show_about()
            elif item == "Shutdown":
                QApplication.quit()
        
        elif menu == "View":
            if item == "Show Inspector":
                self.launch_app("Inspector")
            elif item == "Show Console":
                self.launch_app("Console")
        
        elif menu == "File":
            if item == "New Window":
                self.launch_app("Newton")
            elif item == "Close Window":
                # Close focused window
                pass
    
    def _show_about(self) -> None:
        """Show about dialog."""
        window = NWindow(title="About Newton OS", width=300, height=200)
        
        content = QLabel(
            "◆ Newton OS\n\n"
            "Version 1.0\n\n"
            "Everything is an NObject.\n"
            "Query by constraint, not by path.\n"
            "Squares and circles suck.\n\n"
            "© 2024 Newton Systems"
        )
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("color: #333; font-size: 13px;")
        window.add_widget(content)
        
        self._register_window(window, "About")
        window.show()
