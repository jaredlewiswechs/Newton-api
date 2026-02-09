"""
═══════════════════════════════════════════════════════════════
NCONSOLE - NEWTON CONSOLE
Interactive console for Newton commands and verification.
Direct access to Newton Agent.
═══════════════════════════════════════════════════════════════
"""

from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLineEdit, QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor

from core.nobject import NObject
from core.graph import TheGraph
from shell.window import NWindow


class NewtonWorker(QThread):
    """Worker thread for Newton Agent calls."""
    
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, command: str, mode: str = "ask"):
        super().__init__()
        self.command = command
        self.mode = mode
    
    def run(self):
        try:
            # Try to import Newton Agent
            from newton_agent import NewtonAgent
            
            agent = NewtonAgent()
            
            if self.mode == "ask":
                result = agent.process(self.command)
                self.result_ready.emit({
                    'content': result.content,
                    'verified': result.verified,
                    'constraints_passed': result.constraints_passed,
                    'mode': 'ask'
                })
            
            elif self.mode == "verify":
                # Direct verification
                from core.forge import Forge
                forge = Forge()
                result = forge.verify(self.command)
                self.result_ready.emit({
                    'verified': result.verified,
                    'confidence': result.confidence,
                    'mode': 'verify'
                })
            
            elif self.mode == "calculate":
                # Logic engine calculation
                from core.logic import LogicEngine
                engine = LogicEngine()
                import json
                expr = json.loads(self.command)
                result = engine.evaluate(expr)
                self.result_ready.emit({
                    'result': result.value,
                    'verified': result.verified,
                    'mode': 'calculate'
                })
            
            elif self.mode == "query":
                # Query TheGraph
                import json
                query_params = json.loads(self.command)
                results = TheGraph.query(**query_params)
                self.result_ready.emit({
                    'count': len(results),
                    'results': [obj.to_dict() for obj in results[:10]],
                    'mode': 'query'
                })
                
        except ImportError as e:
            self.error_occurred.emit(f"Newton Agent not available: {e}")
        except Exception as e:
            self.error_occurred.emit(str(e))


class NConsole(NWindow):
    """
    Newton Console - interactive command interface.
    
    Features:
    - Direct Newton Agent queries
    - Verification commands
    - Logic calculations
    - Object graph queries
    - Command history
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(title="Console", width=600, height=400, parent=parent)
        
        self.add_tag('app')
        self.add_tag('console')
        self.set_property('app_name', 'Console')
        
        self._history: List[str] = []
        self._history_index = -1
        self._worker: Optional[NewtonWorker] = None
        
        self._setup_console_ui()
    
    def _setup_console_ui(self) -> None:
        """Setup the console interface."""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Output area
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Consolas", 11))
        self._output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self._output, 1)
        
        # Print welcome message
        self._print_welcome()
        
        # Mode selector and input row
        input_row = QHBoxLayout()
        
        # Mode dropdown
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["ask", "verify", "calculate", "query"])
        self._mode_combo.setFixedWidth(100)
        self._mode_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        input_row.addWidget(self._mode_combo)
        
        # Input field
        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter command...")
        self._input.setFont(QFont("Consolas", 11))
        self._input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        self._input.returnPressed.connect(self._execute_command)
        input_row.addWidget(self._input, 1)
        
        # Execute button
        self._exec_btn = QPushButton("▶")
        self._exec_btn.setFixedSize(36, 36)
        self._exec_btn.setStyleSheet("""
            QPushButton {
                background-color: #27c93f;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #32d74b;
            }
            QPushButton:disabled {
                background-color: #888;
            }
        """)
        self._exec_btn.clicked.connect(self._execute_command)
        input_row.addWidget(self._exec_btn)
        
        layout.addLayout(input_row)
        
        # Add to window content
        container = QWidget()
        container.setLayout(layout)
        self.add_widget(container)
    
    def _print_welcome(self) -> None:
        """Print welcome message."""
        welcome = """<span style="color: #569cd6;">◆ Newton Console</span>
<span style="color: #6a9955;">// Everything is verified. Nothing is assumed.</span>

<span style="color: #dcdcaa;">Modes:</span>
  <span style="color: #ce9178;">ask</span>      - Query Newton Agent
  <span style="color: #ce9178;">verify</span>   - Verify a claim
  <span style="color: #ce9178;">calculate</span> - Evaluate expression
  <span style="color: #ce9178;">query</span>    - Query object graph

<span style="color: #dcdcaa;">Examples:</span>
  ask: What is the speed of light?
  verify: The Earth is round
  calculate: {"op": "+", "args": [2, 3]}
  query: {"type": "NWindow"}

"""
        self._output.setHtml(f"<pre>{welcome}</pre>")
    
    def _execute_command(self) -> None:
        """Execute the current command."""
        command = self._input.text().strip()
        if not command:
            return
        
        mode = self._mode_combo.currentText()
        
        # Add to history
        self._history.append(command)
        self._history_index = len(self._history)
        
        # Show command in output
        self._append_output(f"\n<span style='color: #569cd6;'>[{mode}]</span> <span style='color: #9cdcfe;'>{command}</span>\n")
        
        # Clear input
        self._input.clear()
        self._input.setEnabled(False)
        self._exec_btn.setEnabled(False)
        
        # Run in worker thread
        self._worker = NewtonWorker(command, mode)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
    
    def _on_result(self, result: dict) -> None:
        """Handle successful result."""
        mode = result.get('mode', 'ask')
        
        if mode == 'ask':
            content = result.get('content', 'No response')
            verified = result.get('verified', False)
            constraints = result.get('constraints_passed', 0)
            
            status_color = '#27c93f' if verified else '#ff605c'
            status_text = '✓ Verified' if verified else '✗ Unverified'
            
            self._append_output(
                f"<span style='color: #d4d4d4;'>{content}</span>\n"
                f"<span style='color: {status_color};'>{status_text}</span> "
                f"<span style='color: #6a9955;'>({constraints} constraints passed)</span>\n"
            )
        
        elif mode == 'verify':
            verified = result.get('verified', False)
            confidence = result.get('confidence', 0)
            
            status_color = '#27c93f' if verified else '#ff605c'
            status = '✓ VERIFIED' if verified else '✗ NOT VERIFIED'
            
            self._append_output(
                f"<span style='color: {status_color}; font-weight: bold;'>{status}</span>\n"
                f"<span style='color: #6a9955;'>Confidence: {confidence:.1%}</span>\n"
            )
        
        elif mode == 'calculate':
            value = result.get('result', 'Error')
            verified = result.get('verified', False)
            
            status_color = '#27c93f' if verified else '#ff605c'
            
            self._append_output(
                f"<span style='color: #b5cea8;'>= {value}</span>\n"
                f"<span style='color: {status_color};'>{'✓ Verified' if verified else '✗ Unverified'}</span>\n"
            )
        
        elif mode == 'query':
            count = result.get('count', 0)
            results = result.get('results', [])
            
            self._append_output(
                f"<span style='color: #dcdcaa;'>Found {count} objects</span>\n"
            )
            
            for obj in results[:5]:
                obj_type = obj.get('type', 'Unknown')
                obj_id = obj.get('id', '')[:8]
                self._append_output(
                    f"  <span style='color: #9cdcfe;'>{obj_type}</span> "
                    f"<span style='color: #6a9955;'>({obj_id}...)</span>\n"
                )
            
            if count > 5:
                self._append_output(
                    f"  <span style='color: #6a9955;'>... and {count - 5} more</span>\n"
                )
    
    def _on_error(self, error: str) -> None:
        """Handle error."""
        self._append_output(
            f"<span style='color: #f44747;'>Error: {error}</span>\n"
        )
    
    def _on_finished(self) -> None:
        """Re-enable input after command completes."""
        self._input.setEnabled(True)
        self._exec_btn.setEnabled(True)
        self._input.setFocus()
    
    def _append_output(self, html: str) -> None:
        """Append HTML to output."""
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(html)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()
    
    def keyPressEvent(self, event) -> None:
        """Handle key events for history navigation."""
        if event.key() == Qt.Key.Key_Up:
            if self._history and self._history_index > 0:
                self._history_index -= 1
                self._input.setText(self._history[self._history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self._history_index < len(self._history) - 1:
                self._history_index += 1
                self._input.setText(self._history[self._history_index])
            else:
                self._history_index = len(self._history)
                self._input.clear()
        else:
            super().keyPressEvent(event)
