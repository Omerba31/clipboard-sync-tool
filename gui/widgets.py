# -*- coding: utf-8 -*-
# gui/widgets.py
"""
Reusable widgets for Clipboard Sync Tool GUI.
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
import pyperclip

from gui import styles
from gui.styles import Colors, CONTENT_ICONS, PLATFORM_ICONS


class ClipboardItemWidget(QWidget):
    """Widget for displaying clipboard history item"""
    
    def __init__(self, content: str, content_type: str, timestamp: datetime, 
                 device: str, is_sent: bool = True):
        super().__init__()
        self.content = content
        self._setup_ui(content_type, timestamp, device, is_sent)
    
    def _setup_ui(self, content_type: str, timestamp: datetime, device: str, is_sent: bool):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Icon based on content type
        icon_label = QLabel(CONTENT_ICONS.get(content_type, CONTENT_ICONS['default']))
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setFixedWidth(40)
        layout.addWidget(icon_label)
        
        # Content preview
        content_layout = QVBoxLayout()
        
        # Content text (truncated)
        display_text = str(self.content)
        if len(display_text) > 100:
            display_text = display_text[:100] + '...'
        content_label = QLabel(display_text.replace('\n', ' '))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("font-size: 12px;")
        content_layout.addWidget(content_label)
        
        # Metadata
        direction = 'Sent to' if is_sent else 'From'
        meta_text = f"{direction} {device} • {timestamp.strftime('%H:%M:%S')}"
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 10px;")
        content_layout.addWidget(meta_label)
        
        layout.addLayout(content_layout, 1)
        
        # Copy button
        copy_btn = QPushButton("Copy")
        copy_btn.setToolTip("Copy to clipboard")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        copy_btn.setFixedSize(60, 30)
        copy_btn.setStyleSheet(styles.BTN_PRIMARY)
        layout.addWidget(copy_btn)
        
        self.setLayout(layout)
        self.setStyleSheet(styles.CARD_HOVER)

    def _copy_to_clipboard(self):
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
        self.pair_btn = None  # Will be set if device not paired
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Device icon - detect platform if available
        platform = self.device.get('platform', 'windows')
        icon = PLATFORM_ICONS.get(platform, PLATFORM_ICONS['default'])
        icon_label = QLabel(icon)
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
        status_icon = '🟢' if status in ('online', 'paired', 'discovered') else '🔴'
        status_text = f"{status_icon} {status} • {ip}"
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout, 1)
        
        # Action button
        if status != 'paired':
            self.pair_btn = QPushButton("Connect")
            self.pair_btn.setStyleSheet(styles.BTN_PRIMARY)
            layout.addWidget(self.pair_btn)
        else:
            trust_label = QLabel("✔ Connected")
            trust_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: bold;")
            layout.addWidget(trust_label)
        
        self.setLayout(layout)
        self.setStyleSheet(styles.CARD)


class StatCard(QWidget):
    """Widget for displaying statistics on dashboard"""
    
    def __init__(self, title: str, value: str, icon: str = "📊"):
        super().__init__()
        self._setup_ui(title, value, icon)
    
    def _setup_ui(self, title: str, value: str, icon: str):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Icon and title row
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Colors.PRIMARY};")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        self.setStyleSheet(styles.CARD)
    
    def set_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(value)
