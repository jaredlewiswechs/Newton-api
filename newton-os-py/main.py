"""
═══════════════════════════════════════════════════════════════
NEWTON OS - MAIN ENTRY POINT
Boot the verified desktop environment.
═══════════════════════════════════════════════════════════════

"Squares and circles suck."
Everything is a continuous curve.
Everything is an NObject.
Query by constraint, not by path.

Usage:
    python main.py

Requirements:
    pip install PyQt6
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


def main():
    """Boot Newton OS."""
    
    # Enable high DPI scaling (must be before QApplication)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Newton OS")
    app.setOrganizationName("Newton Systems")
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Import and create desktop (must be after QApplication)
    from shell.desktop import NDesktop
    from apps.inspector import NInspector
    from apps.console import NConsole
    
    # Create the desktop
    desktop = NDesktop()
    
    # Register apps
    desktop.register_app("Inspector", NInspector)
    desktop.register_app("Console", NConsole)
    
    # Show desktop
    desktop.show()
    
    print("◆ Newton OS booting...")
    print("  - Everything is an NObject")
    print("  - Query by constraint, not by path")
    print("  - Squares and circles suck")
    print()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
