# -*- coding: utf-8 -*-
# gui/main_window.py
"""
Complete GUI for Clipboard Sync Tool using PyQt6.
Fixed version with all features properly implemented.
"""

import sys
import os
import base64
import io
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import qrcode
import pyperclip

try:
    from core.sync_engine import SyncEngine
    from core.monitor import ContentType
    from gui.pairing_server import PairingServer
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    PairingServer = None
    print("Warning: Core modules not available, running in limited mode")

class ClipboardItemWidget(QWidget):
    """Widget for displaying clipboard history item"""
    
    def __init__(self, content: str, content_type: str, timestamp: datetime, 
                 device: str, is_sent: bool = True):
        super().__init__()
        self.content = content
        self.setup_ui(content_type, timestamp, device, is_sent)
    
    def setup_ui(self, content_type: str, timestamp: datetime, device: str, is_sent: bool):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Icon based on content type
        icon_label = QLabel()
        icon_map = {
            'text': '📝',
            'image': '🖼️',
            'code': '💻',
            'url': '🔗',
            'json': '📊',
            'file': '📁'
        }
        icon_label.setText(icon_map.get(content_type, '📎'))
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedWidth(40)
        layout.addWidget(icon_label)
        
        # Content preview
        content_layout = QVBoxLayout()
        
        # Content text (truncated)
        display_content = str(self.content)[:100] + '...' if len(str(self.content)) > 100 else str(self.content)
        content_label = QLabel(display_content.replace('\n', ' '))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("font-size: 12px;")
        content_layout.addWidget(content_label)
        
        # Metadata
        meta_text = f"{'Sent to' if is_sent else 'From'} {device} • {timestamp.strftime('%H:%M:%S')}"
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet("color: #888; font-size: 10px;")
        content_layout.addWidget(meta_label)
        
        layout.addLayout(content_layout, 1)
        
        # Action buttons
        copy_btn = QPushButton("Copy")
        copy_btn.setToolTip("Copy to clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        copy_btn.setFixedSize(60, 30)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(copy_btn)
        
        self.setLayout(layout)
        
        # Widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 5px;
            }
            QWidget:hover {
                background-color: #f9f9f9;
                border: 1px solid #4CAF50;
            }
        """)

    def copy_to_clipboard(self):
        """Copy content back to clipboard"""
        try:
            pyperclip.copy(str(self.content))
            QMessageBox.information(self, "Copied", "Content copied to clipboard!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not copy: {str(e)}")

class DeviceWidget(QWidget):
    """Widget for displaying connected device"""
    
    pair_signal = pyqtSignal(object)
    
    def __init__(self, device_info: dict):
        super().__init__()
        self.device = device_info
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Device icon
        icon_label = QLabel()
        platform_icons = {
            'windows': '💻',
            'darwin': '🖥️',
            'linux': '🐧',
            'android': '📱',
            'ios': '📱'
        }
        icon_label.setText(platform_icons.get('windows', '📟'))
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setFixedWidth(50)
        layout.addWidget(icon_label)
        
        # Device info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.device.get('name', 'Unknown Device'))
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        status = self.device.get('status', 'unknown')
        ip = self.device.get('ip_address', 'N/A')
        status_text = f"🟢 {status} • {ip}"
        status_label = QLabel(status_text)
        status_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout, 1)
        
        # Action button
        if status != 'paired':
            pair_btn = QPushButton("Connect")
            pair_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            pair_btn.clicked.connect(lambda: self.pair_signal.emit(self.device))
            layout.addWidget(pair_btn)
        else:
            trust_label = QLabel("✔ Connected")
            trust_label.setStyleSheet("color: green; font-weight: bold;")
            layout.addWidget(trust_label)
        
        self.setLayout(layout)
        
        # Widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)

class MainWindow(QMainWindow):
    """Main application window with full features"""
    
    def __init__(self):
        super().__init__()
        self.sync_engine = None
        self.pairing_server = None
        self.clipboard_history = []
        self.history_widgets = []
        self.is_syncing = True
        
        self.setup_ui()
        if CORE_AVAILABLE:
            self.setup_sync_engine()
        else:
            self.setup_simple_mode()
        self.setup_timers()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("📄 Clipboard Sync Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                background: white;
                border: none;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin: 2px;
                background: #f0f0f0;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 3px solid #4CAF50;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Dashboard tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # History tab
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, "📜 History")
        
        # Devices tab
        self.devices_tab = self.create_devices_tab()
        self.tabs.addTab(self.devices_tab, "🖥️ Devices")

        # Settings tab
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")

        main_layout.addWidget(self.tabs)
        
        central_widget.setLayout(main_layout)
        
        # System tray
        self.setup_system_tray()
    
    def create_header(self) -> QWidget:
        """Create header with status and quick actions"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QWidget {
                background-color: #4CAF50;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: white;
                color: #4CAF50;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Status
        self.status_label = QLabel("🟢 Sync Active")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Device count
        self.device_count_label = QLabel("0 devices connected")
        self.device_count_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.device_count_label)
        
        layout.addStretch()
        
        # Quick actions
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.toggle_sync)
        layout.addWidget(self.pause_btn)
        
        qr_btn = QPushButton("📱 Local P2P")
        qr_btn.clicked.connect(self.show_qr_code)
        layout.addWidget(qr_btn)
        
        cloud_btn = QPushButton("☁️ Cloud Relay")
        cloud_btn.clicked.connect(self.show_cloud_relay)
        layout.addWidget(cloud_btn)
        
        header.setLayout(layout)
        return header
    
    def create_dashboard_tab(self) -> QWidget:
        """Create dashboard with stats and recent activity"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        self.total_syncs_card = self.create_stat_card("Total Syncs", "0", "📊")
        stats_layout.addWidget(self.total_syncs_card)
        
        self.active_devices_card = self.create_stat_card("Active Devices", "0", "🖥️")
        stats_layout.addWidget(self.active_devices_card)
        
        self.data_saved_card = self.create_stat_card("Data Synced", "0 MB", "💾")
        stats_layout.addWidget(self.data_saved_card)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
            }
        """)
        activity_layout = QVBoxLayout()
        
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #f9f9f9;
            }
        """)
        activity_layout.addWidget(self.activity_list)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self) -> QWidget:
        """Create history tab with clipboard history"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search clipboard history...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_history)
        search_layout.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Text", "Images", "URLs", "Code"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(lambda: self.filter_history(self.search_input.text()))
        search_layout.addWidget(self.filter_combo)
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        search_layout.addWidget(clear_btn)
        
        layout.addLayout(search_layout)
        
        # History list
        self.history_scroll = QScrollArea()
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_layout.addStretch()
        self.history_container.setLayout(self.history_layout)
        self.history_scroll.setWidget(self.history_container)
        self.history_scroll.setWidgetResizable(True)
        
        layout.addWidget(self.history_scroll)
        
        widget.setLayout(layout)
        return widget
    
    def create_devices_tab(self) -> QWidget:
        """Create devices tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cloud relay status card
        self.cloud_status_card = QWidget()
        self.cloud_status_card.setStyleSheet("""
            QWidget {
                background-color: #FFF3E0;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        """)
        cloud_card_layout = QVBoxLayout()
        cloud_card_layout.setContentsMargins(12, 12, 12, 12)
        
        self.cloud_status_label = QLabel("☁️ Cloud Relay: Not connected")
        self.cloud_status_label.setStyleSheet("font-weight: bold; color: #E65100;")
        cloud_card_layout.addWidget(self.cloud_status_label)
        
        self.cloud_details_label = QLabel("Click '☁️ Cloud Relay' button to connect to mobile devices")
        self.cloud_details_label.setStyleSheet("color: #666; font-size: 11px;")
        self.cloud_details_label.setWordWrap(True)
        cloud_card_layout.addWidget(self.cloud_details_label)
        
        # Device list label
        self.cloud_devices_label = QLabel("")
        self.cloud_devices_label.setStyleSheet("color: #444; font-size: 11px; margin-top: 8px;")
        self.cloud_devices_label.setWordWrap(True)
        self.cloud_devices_label.setVisible(False)
        cloud_card_layout.addWidget(self.cloud_devices_label)
        
        # Test button (hidden by default)
        self.cloud_test_btn = QPushButton("📤 Test Sync")
        self.cloud_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.cloud_test_btn.clicked.connect(self.test_cloud_sync)
        self.cloud_test_btn.setVisible(False)
        cloud_card_layout.addWidget(self.cloud_test_btn)
        
        self.cloud_status_card.setLayout(cloud_card_layout)
        layout.addWidget(self.cloud_status_card)
        
        # Info label
        info_label = QLabel("💡 Local P2P: Devices on the same WiFi will appear below")
        info_label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1976D2;
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 10px;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Discovered devices (local P2P)
        discovered_group = QGroupBox("Discovered Devices (Local Network)")
        self.discovered_layout = QVBoxLayout()
        self.discovered_layout.addStretch()
        discovered_group.setLayout(self.discovered_layout)
        
        # Paired devices (local P2P)
        paired_group = QGroupBox("Paired Devices (Local Network)")
        self.paired_layout = QVBoxLayout()
        self.paired_layout.addStretch()
        paired_group.setLayout(self.paired_layout)
        
        layout.addWidget(discovered_group)
        layout.addWidget(paired_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QFormLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Auto sync
        self.auto_sync_check = QCheckBox("Enable automatic sync")
        self.auto_sync_check.setChecked(True)
        layout.addRow("Auto Sync:", self.auto_sync_check)
        
        # Content types
        types_group = QWidget()
        types_layout = QHBoxLayout()
        types_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sync_text_check = QCheckBox("Text")
        self.sync_text_check.setChecked(True)
        self.sync_images_check = QCheckBox("Images")
        self.sync_images_check.setChecked(True)
        self.sync_files_check = QCheckBox("Files")
        self.sync_files_check.setChecked(True)
        
        types_layout.addWidget(self.sync_text_check)
        types_layout.addWidget(self.sync_images_check)
        types_layout.addWidget(self.sync_files_check)
        types_layout.addStretch()
        types_group.setLayout(types_layout)
        layout.addRow("Sync Types:", types_group)
        
        # Size limit
        self.size_limit_spin = QSpinBox()
        self.size_limit_spin.setRange(1, 100)
        self.size_limit_spin.setValue(10)
        self.size_limit_spin.setSuffix(" MB")
        layout.addRow("Max Size:", self.size_limit_spin)
        
        # Device name
        self.device_name_input = QLineEdit()
        self.device_name_input.setPlaceholderText("My Computer")
        layout.addRow("Device Name:", self.device_name_input)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addRow(save_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_stat_card(self, title: str, value: str, icon: str) -> QWidget:
        """Create a statistics card widget"""
        card = QWidget()
        card.setFixedSize(200, 120)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon and title
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        layout.addWidget(self.value_label)
        
        layout.addStretch()
        
        card.setLayout(layout)
        card.value_label = self.value_label  # Store reference for updates
        return card
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Clipboard Sync Tool")
        
        # Create simple icon
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.green)
        self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        tray_menu.addSeparator()
        
        pause_action = tray_menu.addAction("Pause Sync")
        pause_action.triggered.connect(self.toggle_sync)
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def setup_sync_engine(self):
        """Initialize sync engine if available"""
        if CORE_AVAILABLE:
            try:
                self.sync_engine = SyncEngine()
                # Start the full sync engine (monitor + network)
                self.sync_engine.start()
                
                # Start the pairing server for mobile devices
                if PairingServer:
                    self.pairing_server = PairingServer(self.sync_engine, port=8080)
                    self.pairing_server.start(on_pair_callback=self.on_device_paired)
                    print(f"✅ Pairing server ready at: {self.pairing_server.get_pairing_url()}")
                
                # Create a timer to poll for new clipboard items
                self.poll_timer = QTimer()
                self.poll_timer.timeout.connect(self.check_for_new_items)
                self.poll_timer.start(500)  # Check every 500ms
                
                self.status_label.setText("🟢 Sync Active")
                print("✅ Sync engine started successfully")
            except Exception as e:
                print(f"❌ Could not start sync engine: {e}")
                import traceback
                traceback.print_exc()
                self.setup_simple_mode()
    
    def on_device_paired(self, device):
        """Callback when a device is paired"""
        QMessageBox.information(self, "Device Paired", 
                              f"Successfully paired with {device.name}!")
        self.update_devices_display()

    def check_for_new_items(self):
        """Check if monitor has new items and add them to GUI"""
        if not self.sync_engine or not self.sync_engine.monitor:
            return
        
        # Get recent history from monitor
        monitor_history = self.sync_engine.monitor.get_history(1)
        
        if monitor_history:
            latest = monitor_history[0]
            
            # Check if this is a new item
            if not self.clipboard_history or (
                self.clipboard_history and 
                latest.checksum != self.clipboard_history[0].get('checksum')
            ):
                # Add to GUI
                content = latest.content
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='ignore')
                
                # Add to our history
                self.clipboard_history.insert(0, {
                    'content': str(content),
                    'timestamp': latest.timestamp,
                    'type': latest.content_type.value,
                    'checksum': latest.checksum,
                    'device': 'Local'
                })
                
                # Create widget and add to GUI
                item_widget = ClipboardItemWidget(
                    content=str(content),
                    content_type=latest.content_type.value,
                    timestamp=latest.timestamp,
                    device='Local',
                    is_sent=True
                )
                
                # Remove stretch, add widget, re-add stretch
                if self.history_layout.count() > 0:
                    last_item = self.history_layout.itemAt(self.history_layout.count() - 1)
                    if isinstance(last_item, QSpacerItem):
                        self.history_layout.removeItem(last_item)
                
                self.history_layout.insertWidget(0, item_widget)
                self.history_widgets.append(item_widget)
                self.history_layout.addStretch()
                
                # Update activity list
                activity_text = f"[{latest.timestamp.strftime('%H:%M:%S')}] {latest.content_type.value.title()}: {str(content)[:50]}..."
                self.activity_list.insertItem(0, activity_text)
                
                # Update stats
                self.total_syncs_card.value_label.setText(str(len(self.clipboard_history)))
    
    def add_to_history_simple(self, content: str):
        """Add item to history in simple mode"""
        timestamp = datetime.now()
        
        # Add to internal list
        self.clipboard_history.insert(0, {
            'content': content,
            'timestamp': timestamp,
            'type': 'text',
            'device': 'Local'
        })
        
        # Determine content type
        content_type = 'text'
        if content.startswith(('http://', 'https://')):
            content_type = 'url'
        elif any(keyword in content.lower() for keyword in ['def ', 'class ', 'import ', 'function']):
            content_type = 'code'
        
        # Create the widget for history tab
        item_widget = ClipboardItemWidget(
            content=content,
            content_type=content_type,
            timestamp=timestamp,
            device='Local',
            is_sent=True
        )
        
        # Add to history layout (remove stretch first if it exists)
        if self.history_layout.count() > 0:
            last_item = self.history_layout.itemAt(self.history_layout.count() - 1)
            if isinstance(last_item, QSpacerItem):
                self.history_layout.removeItem(last_item)
        
        # Insert at the beginning
        self.history_layout.insertWidget(0, item_widget)
        self.history_widgets.append(item_widget)
        
        # Re-add stretch at the end
        self.history_layout.addStretch()
        
        # Limit history widgets
        while len(self.history_widgets) > 100:
            widget = self.history_widgets.pop()
            self.history_layout.removeWidget(widget)
            widget.deleteLater()
        
        # Update activity list in dashboard
        activity_text = f"[{timestamp.strftime('%H:%M:%S')}] {content_type.title()}: {content[:50]}..."
        self.activity_list.insertItem(0, activity_text)
        while self.activity_list.count() > 10:
            self.activity_list.takeItem(self.activity_list.count() - 1)
        
        # Update stats
        self.total_syncs_card.value_label.setText(str(len(self.clipboard_history)))
        
        # Force UI update
        self.history_container.update()
        QApplication.processEvents()
        
        print(f"Added to history: {content[:50]}... (Total items: {len(self.clipboard_history)})")
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(5000)  # Update every 5 seconds
    
    def update_ui(self):
        """Update UI with latest data"""
        if self.sync_engine and CORE_AVAILABLE:
            try:
                # Update device count
                devices = self.sync_engine.get_paired_devices()
                self.device_count_label.setText(f"{len(devices)} devices connected")
                
                # Update cloud relay status
                if self.sync_engine.is_cloud_relay_connected():
                    self.cloud_status_label.setText("☁️ Cloud Relay: ✅ Connected")
                    self.cloud_status_label.setStyleSheet("font-weight: bold; color: #2E7D32;")
                    
                    # Show connection details
                    if hasattr(self.sync_engine, 'cloud_relay') and self.sync_engine.cloud_relay:
                        room_id = self.sync_engine.cloud_relay.room_id
                        server = self.sync_engine.cloud_relay.server_url
                        device_name = self.sync_engine.cloud_relay.device_name
                        self.cloud_details_label.setText(f"Server: {server}\nRoom: {room_id}\nYour device: {device_name}")
                        
                        # Show device list if available
                        if hasattr(self.sync_engine.cloud_relay, 'devices') and self.sync_engine.cloud_relay.devices:
                            device_icons = {'desktop': '🖥️', 'mobile': '📱', 'tablet': '📱'}
                            device_list = []
                            for device in self.sync_engine.cloud_relay.devices:
                                icon = device_icons.get(device.get('deviceType', 'desktop'), '🖥️')
                                name = device.get('deviceName', 'Unknown')
                                is_you = ' (You)' if device.get('deviceId') == self.sync_engine.cloud_relay.device_id else ''
                                device_list.append(f"{icon} {name}{is_you}")
                            
                            self.cloud_devices_label.setText("Connected devices:\n" + "\n".join(device_list))
                            self.cloud_devices_label.setVisible(True)
                        else:
                            self.cloud_devices_label.setVisible(False)
                        
                        self.cloud_status_card.setStyleSheet("""
                            QWidget {
                                background-color: #E8F5E9;
                                border-radius: 6px;
                                margin-bottom: 10px;
                            }
                        """)
                        self.cloud_test_btn.setVisible(True)
                else:
                    self.cloud_status_label.setText("☁️ Cloud Relay: Not connected")
                    self.cloud_status_label.setStyleSheet("font-weight: bold; color: #E65100;")
                    self.cloud_details_label.setText("Click '☁️ Cloud Relay' button to connect to mobile devices")
                    self.cloud_devices_label.setVisible(False)
                    self.cloud_status_card.setStyleSheet("""
                        QWidget {
                            background-color: #FFF3E0;
                            border-radius: 6px;
                            margin-bottom: 10px;
                        }
                    """)
                    self.cloud_test_btn.setVisible(False)
                
                # Update devices tab
                self.update_devices_display()
            except:
                pass
    
    def update_devices_display(self):
        """Update the devices display"""
        if not self.sync_engine or not CORE_AVAILABLE:
            return
        
        try:
            # Clear current displays
            while self.discovered_layout.count() > 1:
                item = self.discovered_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            while self.paired_layout.count() > 1:
                item = self.paired_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add discovered devices
            discovered = self.sync_engine.get_discovered_devices()
            for device in discovered:
                device_widget = DeviceWidget({'name': device.name, 'status': 'discovered', 
                                             'ip_address': device.ip_address})
                # Store the actual Device object for pairing
                device_widget.device_obj = device
                device_widget.pair_signal.connect(lambda d=device: self.pair_device(d))
                self.discovered_layout.insertWidget(0, device_widget)
            
            # Add paired devices
            paired = self.sync_engine.get_paired_devices()
            for device in paired:
                device_widget = DeviceWidget({'name': device.name, 'status': 'paired',
                                             'ip_address': device.ip_address})
                self.paired_layout.insertWidget(0, device_widget)
        except:
            pass
    
    def toggle_sync(self):
        """Toggle sync on/off"""
        if self.is_syncing:
            # Pausing
            try:
                if self.sync_engine and CORE_AVAILABLE:
                    if self.sync_engine.is_running:
                        print("Pausing sync...")
                        self.sync_engine.stop()
                        self.status_label.setText("🔴 Sync Paused")
                        self.pause_btn.setText("▶️ Resume")
                        self.is_syncing = False
                        print("✅ Sync paused")
                    else:
                        print("⚠️ Sync engine already stopped")
                        # Update UI to match actual state
                        self.status_label.setText("🔴 Sync Paused")
                        self.pause_btn.setText("▶️ Resume")
                        self.is_syncing = False
            except Exception as e:
                print(f"❌ Error stopping sync: {e}")
                import traceback
                traceback.print_exc()
                # Reset UI state on error
                self.status_label.setText("⚠️ Sync Error")
                self.pause_btn.setText("▶️ Resume")
                self.is_syncing = False
        else:
            # Resuming
            try:
                if self.sync_engine and CORE_AVAILABLE:
                    if not self.sync_engine.is_running:
                        print("Resuming sync...")
                        self.sync_engine.start()
                        self.status_label.setText("🟢 Sync Active")
                        self.pause_btn.setText("⏸️ Pause")
                        self.is_syncing = True
                        print("✅ Sync resumed")
                    else:
                        print("⚠️ Sync engine already running")
                        # Update UI to match actual state
                        self.status_label.setText("🟢 Sync Active")
                        self.pause_btn.setText("⏸️ Pause")
                        self.is_syncing = True
            except Exception as e:
                print(f"❌ Error starting sync: {e}")
                import traceback
                traceback.print_exc()
                # Reset UI state on error
                self.status_label.setText("⚠️ Sync Error")
                self.pause_btn.setText("🔄 Retry")
                self.is_syncing = False
                QMessageBox.critical(
                    self,
                    "Sync Error",
                    f"Failed to resume sync:\n\n{str(e)}\n\nTry restarting the application."
                )
    
    def show_qr_code(self):
        """Show QR code for pairing"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Device Pairing")
        dialog.setFixedSize(500, 650)
        
        layout = QVBoxLayout()
        
        # Tab widget for show/scan options
        tab_widget = QTabWidget()
        
        # Tab 1: Show QR Code
        show_tab = QWidget()
        show_layout = QVBoxLayout()
        
        label = QLabel("📱 Pairing Data for P2P Connection")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        show_layout.addWidget(label)
        
        # Generate QR code
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setMinimumHeight(200)
        
        # JSON data text box (copyable)
        json_text = QTextEdit()
        json_text.setReadOnly(True)
        json_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                background: #f9f9f9;
            }
        """)
        json_text.setMaximumHeight(150)
        
        # Copy button
        copy_btn = QPushButton("📋 Copy JSON Data")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        if self.sync_engine and CORE_AVAILABLE:
            try:
                # Generate pairing JSON data
                pairing_data = self.sync_engine.generate_pairing_qr()
                json_text.setPlainText(pairing_data)
                
                # Generate QR code with the JSON
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(pairing_data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert PIL image to QPixmap
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.read())
                qr_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                
                # Copy button functionality
                def copy_json():
                    clipboard = QApplication.clipboard()
                    clipboard.setText(pairing_data)
                    copy_btn.setText("✅ Copied!")
                    QTimer.singleShot(2000, lambda: copy_btn.setText("📋 Copy JSON Data"))
                
                copy_btn.clicked.connect(copy_json)
                
            except Exception as e:
                qr_label.setText(f"❌ Generation failed\n\n{str(e)}")
                qr_label.setStyleSheet("color: red;")
                json_text.setPlainText("Error generating pairing data")
                copy_btn.setEnabled(False)
        else:
            qr_label.setText("❌ Network sync not available")
            qr_label.setStyleSheet("color: red;")
            json_text.setPlainText("Core modules not loaded - running in simple mode")
            copy_btn.setEnabled(False)
        
        show_layout.addWidget(qr_label)
        show_layout.addWidget(QLabel("Copy this JSON and paste on the other computer:"))
        show_layout.addWidget(json_text)
        show_layout.addWidget(copy_btn)
        
        # Instructions
        instructions = QLabel("1. Click 'Copy JSON Data'\n2. Go to other computer\n3. Click 'Enter QR Data' tab\n4. Paste and click 'Pair'")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setStyleSheet("font-size: 11px; color: #888; margin-top: 10px;")
        show_layout.addWidget(instructions)
        
        show_layout.addStretch()
        show_tab.setLayout(show_layout)
        
        # Tab 2: Enter QR Data
        scan_tab = QWidget()
        scan_layout = QVBoxLayout()
        
        scan_label = QLabel("🔗 Paste Pairing Data from Another Computer")
        scan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        scan_layout.addWidget(scan_label)
        
        instructions = QLabel("Paste the JSON pairing data from the other device:")
        instructions.setStyleSheet("color: #666; margin: 5px; font-size: 12px;")
        scan_layout.addWidget(instructions)
        
        qr_input = QTextEdit()
        qr_input.setPlaceholderText('Paste JSON here:\n{"device_id": "...", "device_name": "...", "ip": "...", "port": ..., "public_key": "...", "timestamp": "..."}')
        qr_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #2196F3;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                background: #f9f9f9;
            }
        """)
        scan_layout.addWidget(qr_input)
        
        pair_btn = QPushButton("Pair with Device")
        pair_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        def pair_with_qr():
            qr_text = qr_input.toPlainText().strip()
            if not qr_text:
                QMessageBox.warning(dialog, "Error", "Please enter QR code data")
                return
            
            if self.sync_engine and CORE_AVAILABLE:
                success = self.sync_engine.pair_with_qr_code(qr_text)
                if success:
                    QMessageBox.information(dialog, "Success", "Device paired successfully!")
                    dialog.accept()
                else:
                    QMessageBox.warning(dialog, "Error", "Failed to pair with device. Check the QR data.")
            else:
                QMessageBox.warning(dialog, "Error", "Network sync not available")
        
        pair_btn.clicked.connect(pair_with_qr)
        scan_layout.addWidget(pair_btn)
        
        scan_tab.setLayout(scan_layout)
        
        # Add tabs
        tab_widget.addTab(show_tab, "📱 Show QR")
        tab_widget.addTab(scan_tab, "🔗 Enter QR Data")
        
        layout.addWidget(tab_widget)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def test_cloud_sync(self):
        """Test cloud relay sync by sending a test message"""
        if not self.sync_engine or not self.sync_engine.is_cloud_relay_connected():
            QMessageBox.warning(self, "Not Connected", "Cloud relay is not connected")
            return
        
        import datetime
        test_message = f"Test sync from desktop at {datetime.datetime.now().strftime('%H:%M:%S')}"
        
        try:
            import pyperclip
            pyperclip.copy(test_message)
            QMessageBox.information(self, "Test Sent! 📤", 
                                  f"Test message copied to clipboard:\n\n"
                                  f'"{test_message}"\n\n'
                                  f"It should appear on your mobile device shortly!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send test: {str(e)}")
    
    def show_cloud_relay(self):
        """Show cloud relay connection dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("☁️ Cloud Relay Connection")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("☁️ Connect to Cloud Relay")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Connect your desktop to the cloud relay server for mobile sync.\nMake sure you've deployed your relay to Fly.io first!")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; margin-bottom: 20px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Server URL input
        url_label = QLabel("Cloud Relay URL:")
        url_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(url_label)
        
        self.cloud_url_input = QLineEdit()
        self.cloud_url_input.setPlaceholderText("https://your-app.fly.dev")
        
        # Auto-load deployed URL if available
        import json
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cloud-relay-config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    url = config.get('cloudRelayUrl')
                    if url:
                        self.cloud_url_input.setText(url)
                        print(f"[INFO] Auto-loaded cloud relay URL: {url}")
            except Exception as e:
                pass
        
        self.cloud_url_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self.cloud_url_input)
        
        # Room ID input
        room_label = QLabel("Room ID (must match mobile device):")
        room_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(room_label)
        
        self.room_id_input = QLineEdit()
        self.room_id_input.setPlaceholderText("my-clipboard")
        self.room_id_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self.room_id_input)
        
        # Device name input
        device_name_label = QLabel("Device Name (shown to other devices):")
        device_name_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(device_name_label)
        
        self.device_name_input = QLineEdit()
        # Auto-fill with hostname
        import socket
        import platform
        try:
            hostname = socket.gethostname() or platform.node() or "Desktop"
        except:
            hostname = "Desktop"
        self.device_name_input.setPlaceholderText(hostname)
        self.device_name_input.setText(hostname)
        self.device_name_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self.device_name_input)
        
        # Info box
        info_box = QLabel("💡 Tip: Use the same Room ID on your mobile device to sync clipboards across all your devices!")
        info_box.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1976D2;
                padding: 12px;
                border-radius: 6px;
                margin-top: 15px;
            }
        """)
        info_box.setWordWrap(True)
        layout.addWidget(info_box)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        connect_btn = QPushButton("🔌 Connect")
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        connect_btn.clicked.connect(lambda: self.connect_to_cloud_relay(dialog))
        btn_layout.addWidget(connect_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def connect_to_cloud_relay(self, dialog):
        """Connect to cloud relay with given URL and room ID"""
        url = self.cloud_url_input.text().strip()
        room_id = self.room_id_input.text().strip()
        device_name = self.device_name_input.text().strip()
        
        if not url:
            QMessageBox.warning(dialog, "Missing URL", "Please enter your cloud relay URL")
            return
        
        if not room_id:
            QMessageBox.warning(dialog, "Missing Room ID", "Please enter a Room ID")
            return
        
        # Use hostname if device name is empty
        if not device_name:
            import socket
            import platform
            try:
                device_name = socket.gethostname() or platform.node() or "Desktop"
            except:
                device_name = "Desktop"
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Check if sync engine is available
        if not self.sync_engine or not CORE_AVAILABLE:
            QMessageBox.warning(dialog, "Error", 
                              "Sync engine not available. Core modules may not be loaded.")
            return
        
        # Connect in separate thread to avoid blocking GUI
        import threading
        import asyncio
        from PyQt6.QtCore import QTimer, pyqtSignal
        
        # Store connection state
        self._connection_result = {'success': False, 'error': None}
        
        # Close the input dialog
        dialog.accept()
        
        # Show non-modal progress message
        from PyQt6.QtWidgets import QProgressDialog
        progress = QProgressDialog("Connecting to cloud relay...\n" + url, "Cancel", 0, 0, self)
        progress.setWindowTitle("Connecting...")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        def do_connect_thread():
            """Run connection in thread"""
            try:
                # Run async connection
                future = asyncio.run_coroutine_threadsafe(
                    self.sync_engine.connect_to_cloud_relay(url, room_id, device_name),
                    self.sync_engine.loop
                )
                # Wait for result with timeout
                success = future.result(timeout=10)
                self._connection_result = {'success': success, 'error': None}
            except Exception as e:
                self._connection_result = {'success': False, 'error': str(e)}
        
        # Start connection thread
        thread = threading.Thread(target=do_connect_thread, daemon=True)
        thread.start()
        
        # Check connection status periodically
        def check_status():
            if thread.is_alive():
                # Still connecting, check again
                QTimer.singleShot(100, check_status)
            else:
                # Connection complete
                progress.close()
                
                result = self._connection_result
                if result['success']:
                    QMessageBox.information(self, "✅ Connected!", 
                                          f"Successfully connected to cloud relay!\n\n"
                                          f"Server: {url}\n"
                                          f"Room: {room_id}\n\n"
                                          f"Your clipboard is now syncing with mobile devices in this room.")
                    self.status_label.setText("🟢 Sync Active (Cloud + Local)")
                elif result['error']:
                    QMessageBox.critical(self, "Error", 
                                       f"Failed to connect:\n{result['error']}\n\n"
                                       f"Check the console for more details.")
                else:
                    QMessageBox.warning(self, "Connection Failed", 
                                      f"Could not connect to cloud relay.\n\n"
                                      f"Please check:\n"
                                      f"• Server URL is correct\n"
                                      f"• Server is running\n"
                                      f"• Internet connection is working")
        
        # Start checking after 100ms
        QTimer.singleShot(100, check_status)
    
    def pair_device(self, device):
        """Pair with a device"""
        if self.sync_engine and CORE_AVAILABLE:
            try:
                self.sync_engine._pair_with_device(device)
                # Get device name - handle both dict and Device object
                device_name = device.name if hasattr(device, 'name') else device.get('name', 'device')
                QMessageBox.information(self, "Success", f"Paired with {device_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not pair: {str(e)}")
    
    def filter_history(self, text):
        """Filter history based on search text"""
        search_text = text.lower()
        filter_type = self.filter_combo.currentText().lower()
        
        # Go through all history widgets
        for widget in self.history_widgets:
            should_show = True
            
            # Check search text match
            if search_text:
                content = str(widget.content).lower()
                if search_text not in content:
                    should_show = False
            
            # Check type filter
            if filter_type != 'all' and should_show:
                # Map filter names to content types
                type_map = {
                    'text': ['text'],
                    'images': ['image'],
                    'urls': ['url'],
                    'code': ['code']
                }
                
                if filter_type in type_map:
                    # Need to check the widget's content type
                    # We'll determine this from the icon or store it in the widget
                    content = str(widget.content)
                    widget_type = 'text'
                    
                    if content.startswith(('http://', 'https://')):
                        widget_type = 'url'
                    elif any(keyword in content.lower() for keyword in ['def ', 'class ', 'import ', 'function']):
                        widget_type = 'code'
                    
                    if widget_type not in type_map[filter_type]:
                        should_show = False
            
            # Show or hide the widget
            if should_show:
                widget.show()
            else:
                widget.hide()
    
    def clear_history(self):
        """Clear clipboard history"""
        reply = QMessageBox.question(self, "Clear History",
                                    "Are you sure you want to clear all clipboard history?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear internal history
            self.clipboard_history.clear()
            
            # Clear all widgets from the layout
            for widget in self.history_widgets:
                self.history_layout.removeWidget(widget)
                widget.deleteLater()
            
            # Clear the widgets list
            self.history_widgets.clear()
            
            # Remove all items from layout (including any remaining spacers)
            while self.history_layout.count() > 0:
                item = self.history_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Re-add the stretch at the end
            self.history_layout.addStretch()
            
            # Clear activity list
            self.activity_list.clear()
            
            # Reset stats
            self.total_syncs_card.value_label.setText("0")
    
    def save_settings(self):
        """Save settings"""
        if self.sync_engine and CORE_AVAILABLE:
            try:
                self.sync_engine.update_settings(
                    auto_sync=self.auto_sync_check.isChecked(),
                    sync_text=self.sync_text_check.isChecked(),
                    sync_images=self.sync_images_check.isChecked(),
                    sync_files=self.sync_files_check.isChecked(),
                    max_size_mb=self.size_limit_spin.value()
                )
            except:
                pass
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
    
    def quit_application(self):
        """Properly quit the application"""
        print("Shutting down...")
        
        # Stop pairing server first
        if self.pairing_server:
            try:
                self.pairing_server.stop()
                print("✅ Pairing server stopped")
            except Exception as e:
                print(f"⚠️ Error stopping pairing server: {e}")
        
        # Stop sync engine
        if self.sync_engine and CORE_AVAILABLE:
            try:
                if self.sync_engine.is_running:
                    self.sync_engine.stop()
                    print("✅ Sync engine stopped")
            except Exception as e:
                print(f"⚠️ Error stopping sync engine: {e}")
        
        print("👋 Goodbye!")
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close - quit the application"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Quit Application",
            "Are you sure you want to quit Clipboard Sync?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
            self.quit_application()
        else:
            event.ignore()
