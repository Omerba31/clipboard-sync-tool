# gui/simple_gui.py
"""
Simplified GUI that actually works without all the complex features.
Start with this, then expand later.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyperclip
from datetime import datetime

class SimpleSyncWindow(QMainWindow):
    """Simple working GUI for clipboard sync"""
    
    def __init__(self):
        super().__init__()
        self.clipboard_history = []
        self.setup_ui()
        self.setup_clipboard_monitor()
    
    def setup_ui(self):
        """Setup basic UI"""
        self.setWindowTitle("📋 Clipboard Sync Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Status bar
        self.status_label = QLabel("🟢 Monitoring clipboard...")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Tab widget
        tabs = QTabWidget()
        
        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        history_layout.addWidget(QLabel("📜 Clipboard History:"))
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
        """)
        history_layout.addWidget(self.history_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Copy Selected")
        copy_btn.clicked.connect(self.copy_selected)
        btn_layout.addWidget(copy_btn)
        
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(clear_btn)
        
        history_layout.addLayout(btn_layout)
        
        tabs.addTab(history_tab, "History")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        
        self.auto_sync = QCheckBox("Enable Auto Sync")
        self.auto_sync.setChecked(True)
        settings_layout.addRow("Auto Sync:", self.auto_sync)
        
        self.max_history = QSpinBox()
        self.max_history.setRange(10, 1000)
        self.max_history.setValue(100)
        settings_layout.addRow("Max History Items:", self.max_history)
        
        tabs.addTab(settings_tab, "Settings")
        
        layout.addWidget(tabs)
        
        # System tray
        self.setup_tray()
    
    def setup_clipboard_monitor(self):
        """Setup clipboard monitoring"""
        self.clipboard = QApplication.clipboard()
        self.last_text = ""
        
        # Timer to check clipboard
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(1000)  # Check every second
    
    def check_clipboard(self):
        """Check for clipboard changes"""
        try:
            current_text = pyperclip.paste()
            
            if current_text and current_text != self.last_text:
                self.last_text = current_text
                self.add_to_history(current_text)
                
        except Exception as e:
            print(f"Error checking clipboard: {e}")
    
    def add_to_history(self, text):
        """Add item to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Truncate long text
        display_text = text[:100] + "..." if len(text) > 100 else text
        display_text = display_text.replace('\n', ' ')
        
        # Add to list
        item_text = f"[{timestamp}] {display_text}"
        self.history_list.insertItem(0, item_text)
        
        # Store full text
        self.clipboard_history.insert(0, text)
        
        # Limit history size
        max_items = self.max_history.value()
        while self.history_list.count() > max_items:
            self.history_list.takeItem(self.history_list.count() - 1)
            self.clipboard_history.pop()
        
        # Update status
        self.status_label.setText(f"🟢 Captured clipboard item at {timestamp}")
    
    def copy_selected(self):
        """Copy selected item back to clipboard"""
        current_row = self.history_list.currentRow()
        if current_row >= 0 and current_row < len(self.clipboard_history):
            text = self.clipboard_history[current_row]
            pyperclip.copy(text)
            QMessageBox.information(self, "Copied", "Text copied to clipboard!")
    
    def clear_history(self):
        """Clear all history"""
        reply = QMessageBox.question(self, "Clear History", 
                                   "Clear all clipboard history?")
        if reply == QMessageBox.StandardButton.Yes:
            self.history_list.clear()
            self.clipboard_history.clear()
    
    def setup_tray(self):
        """Setup system tray"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Clipboard Sync Tool")
        
        # Tray menu
        menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)
        
        # Create simple icon (you can use actual icon file later)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.green)
        self.tray.setIcon(QIcon(pixmap))
        
        self.tray.show()
    
    def closeEvent(self, event):
        """Minimize to tray instead of closing"""
        event.ignore()
        self.hide()
        self.tray.showMessage("Clipboard Sync", 
                            "Minimized to system tray",
                            QSystemTrayIcon.MessageIcon.Information,
                            2000)

def main():
    """Run the application"""
    app = QApplication(sys.argv)
    window = SimpleSyncWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()