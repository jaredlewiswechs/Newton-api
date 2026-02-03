"""
═══════════════════════════════════════════════════════════════
NMENUBAR - THE MENU BAR
System menu bar with Newton logo and menus.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List, Dict, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QAction

from core.nobject import NObject


class NMenuBar(QWidget):
    """
    Newton OS Menu Bar.
    
    Always visible at top of screen.
    Shows:
    - Newton logo (left)
    - App menus (left-center)
    - System indicators (right)
    - Clock (right)
    """
    
    menu_clicked = pyqtSignal(str, str)  # menu_name, item_name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Use composition for NObject
        self._nobject = NObject(object_type="NMenuBar")
        self._nobject.add_tag('menubar')
        self._nobject.add_tag('system')
        
        self._menus: Dict[str, QMenu] = {}
        self._current_app = "Newton"
        
        self.setFixedHeight(28)
        # Apple 2025 HIG: Frosted glass with high contrast text
        self.setStyleSheet("""
            NMenuBar {
                background-color: rgba(246, 246, 246, 0.92);
                border-bottom: 1px solid rgba(0, 0, 0, 0.12);
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)
        
        # Newton logo/button - Apple HIG: Bold, high contrast
        self._newton_btn = QPushButton("◆")
        self._newton_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 15px;
                font-weight: 600;
                color: #1d1d1f;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.12);
            }
        """)
        self._newton_btn.clicked.connect(self._show_newton_menu)
        layout.addWidget(self._newton_btn)
        
        # App name - Apple HIG: SF Pro semibold, high contrast
        self._app_label = QLabel(self._current_app)
        self._app_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 13px;
                color: #1d1d1f;
                letter-spacing: -0.2px;
            }
        """)
        layout.addWidget(self._app_label)
        
        # Standard menus
        self._file_btn = self._make_menu_button("File")
        self._edit_btn = self._make_menu_button("Edit")
        self._view_btn = self._make_menu_button("View")
        self._window_btn = self._make_menu_button("Window")
        self._help_btn = self._make_menu_button("Help")
        
        layout.addWidget(self._file_btn)
        layout.addWidget(self._edit_btn)
        layout.addWidget(self._view_btn)
        layout.addWidget(self._window_btn)
        layout.addWidget(self._help_btn)
        
        # Spacer
        layout.addStretch()
        
        # System indicators (right side) - Apple HIG: SF Symbols style
        self._status_label = QLabel("✓ Verified")
        self._status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
                color: #34c759;
            }
        """)
        layout.addWidget(self._status_label)
        
        # Clock - Apple HIG: Medium weight, high contrast
        self._clock_label = QLabel("--:--")
        self._clock_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #1d1d1f;
            }
        """)
        layout.addWidget(self._clock_label)
        
        # Setup menus
        self._setup_menus()
    
    def _make_menu_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        # Apple 2025 HIG: High contrast menu items
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: 400;
                color: #1d1d1f;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.12);
            }
            QPushButton::menu-indicator {
                image: none;
            }
        """)
        return btn
    
    def _setup_menus(self) -> None:
        # Apple HIG: Clean menu styling
        menu_style = """
            QMenu {
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 8px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #1d1d1f;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #007aff;
                color: white;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(0, 0, 0, 0.1);
                margin: 4px 8px;
            }
        """
        
        # File menu
        file_menu = QMenu(self)
        file_menu.setStyleSheet(menu_style)
        file_menu.addAction("New Window", lambda: self.menu_clicked.emit("File", "New Window"))
        file_menu.addAction("New Tab", lambda: self.menu_clicked.emit("File", "New Tab"))
        file_menu.addSeparator()
        file_menu.addAction("Close Window", lambda: self.menu_clicked.emit("File", "Close Window"))
        self._file_btn.setMenu(file_menu)
        self._menus['File'] = file_menu
        
        # Edit menu
        edit_menu = QMenu(self)
        edit_menu.setStyleSheet(menu_style)
        edit_menu.addAction("Undo", lambda: self.menu_clicked.emit("Edit", "Undo"))
        edit_menu.addAction("Redo", lambda: self.menu_clicked.emit("Edit", "Redo"))
        edit_menu.addSeparator()
        edit_menu.addAction("Cut", lambda: self.menu_clicked.emit("Edit", "Cut"))
        edit_menu.addAction("Copy", lambda: self.menu_clicked.emit("Edit", "Copy"))
        edit_menu.addAction("Paste", lambda: self.menu_clicked.emit("Edit", "Paste"))
        self._edit_btn.setMenu(edit_menu)
        self._menus['Edit'] = edit_menu
        
        # View menu
        view_menu = QMenu(self)
        view_menu.setStyleSheet(menu_style)
        view_menu.addAction("Show Inspector", lambda: self.menu_clicked.emit("View", "Show Inspector"))
        view_menu.addAction("Show Console", lambda: self.menu_clicked.emit("View", "Show Console"))
        view_menu.addSeparator()
        view_menu.addAction("Enter Full Screen", lambda: self.menu_clicked.emit("View", "Full Screen"))
        self._view_btn.setMenu(view_menu)
        self._menus['View'] = view_menu
        
        # Window menu
        window_menu = QMenu(self)
        window_menu.setStyleSheet(menu_style)
        window_menu.addAction("Minimize", lambda: self.menu_clicked.emit("Window", "Minimize"))
        window_menu.addAction("Zoom", lambda: self.menu_clicked.emit("Window", "Zoom"))
        window_menu.addSeparator()
        window_menu.addAction("Bring All to Front", lambda: self.menu_clicked.emit("Window", "Bring All"))
        self._window_btn.setMenu(window_menu)
        self._menus['Window'] = window_menu
        
        # Help menu
        help_menu = QMenu(self)
        help_menu.setStyleSheet(menu_style)
        help_menu.addAction("Newton Help", lambda: self.menu_clicked.emit("Help", "Newton Help"))
        help_menu.addAction("About Newton", lambda: self.menu_clicked.emit("Help", "About"))
        self._help_btn.setMenu(help_menu)
        self._menus['Help'] = help_menu
    
    def _show_newton_menu(self) -> None:
        """Show the Newton system menu."""
        # Apple HIG: System menu styling
        menu_style = """
            QMenu {
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 8px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #1d1d1f;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #007aff;
                color: white;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(0, 0, 0, 0.1);
                margin: 4px 8px;
            }
        """
        newton_menu = QMenu(self)
        newton_menu.setStyleSheet(menu_style)
        newton_menu.addAction("About Newton OS", lambda: self.menu_clicked.emit("Newton", "About"))
        newton_menu.addSeparator()
        newton_menu.addAction("System Preferences...", lambda: self.menu_clicked.emit("Newton", "Preferences"))
        newton_menu.addSeparator()
        newton_menu.addAction("Sleep", lambda: self.menu_clicked.emit("Newton", "Sleep"))
        newton_menu.addAction("Restart...", lambda: self.menu_clicked.emit("Newton", "Restart"))
        newton_menu.addAction("Shut Down...", lambda: self.menu_clicked.emit("Newton", "Shutdown"))
        
        newton_menu.exec(self._newton_btn.mapToGlobal(self._newton_btn.rect().bottomLeft()))
    
    def set_current_app(self, app_name: str) -> None:
        """Set the current app name displayed in menu bar."""
        self._current_app = app_name
        self._app_label.setText(app_name)
    
    def set_clock(self, time_str: str) -> None:
        """Update the clock display."""
        self._clock_label.setText(time_str)
    
    def set_verification_status(self, verified: bool, message: str = None) -> None:
        """Update the verification status indicator."""
        # Apple HIG: System green/red with proper contrast
        if verified:
            self._status_label.setText("✓ " + (message or "Verified"))
            self._status_label.setStyleSheet("QLabel { font-size: 12px; font-weight: 500; color: #34c759; }")
        else:
            self._status_label.setText("✗ " + (message or "Unverified"))
            self._status_label.setStyleSheet("QLabel { font-size: 12px; font-weight: 500; color: #ff3b30; }")
