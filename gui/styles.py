# gui/styles.py
"""
Centralized styling for the Clipboard Sync Tool GUI.
All styles in one place for easy maintenance and consistency.
"""

# Color palette - single source of truth
class Colors:
    PRIMARY = '#4CAF50'
    PRIMARY_DARK = '#45a049'
    PRIMARY_DARKER = '#3d8b40'
    PRIMARY_LIGHT = '#E8F5E9'
    
    SECONDARY = '#2196F3'
    SECONDARY_DARK = '#1976D2'
    SECONDARY_LIGHT = '#E3F2FD'
    
    WARNING = '#E65100'
    WARNING_LIGHT = '#FFF3E0'
    
    ERROR = '#f44336'
    SUCCESS = '#4CAF50'
    
    TEXT = '#333'
    TEXT_SECONDARY = '#666'
    TEXT_MUTED = '#888'
    
    BORDER = '#ddd'
    BORDER_LIGHT = '#e0e0e0'
    
    BACKGROUND = '#f0f0f0'
    BACKGROUND_LIGHT = '#f9f9f9'
    CARD = 'white'

# Legacy dict for backward compatibility
COLORS = {
    'primary': Colors.PRIMARY,
    'primary_dark': Colors.PRIMARY_DARK,
    'primary_light': Colors.PRIMARY_LIGHT,
    'secondary': Colors.SECONDARY,
    'secondary_dark': Colors.SECONDARY_DARK,
    'secondary_light': Colors.SECONDARY_LIGHT,
    'warning': Colors.WARNING,
    'warning_light': Colors.WARNING_LIGHT,
    'error': Colors.ERROR,
    'success': Colors.SUCCESS,
    'text': Colors.TEXT,
    'text_secondary': Colors.TEXT_SECONDARY,
    'text_muted': Colors.TEXT_MUTED,
    'border': Colors.BORDER,
    'background': Colors.BACKGROUND,
    'card': Colors.CARD,
}

# Main window style
MAIN_WINDOW = """
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
"""

# Header style
HEADER = """
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
"""

# Button styles
BTN_PRIMARY = """
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
    QPushButton:pressed {
        background-color: #3d8b40;
    }
"""

BTN_SECONDARY = """
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1976D2;
    }
"""

BTN_OUTLINE = """
    QPushButton {
        padding: 8px 20px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: white;
    }
    QPushButton:hover {
        background-color: #f0f0f0;
    }
"""

# Input styles
INPUT = """
    QLineEdit {
        padding: 12px;
        border: 2px solid #ddd;
        border-radius: 6px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 2px solid #4CAF50;
    }
"""

TEXTAREA = """
    QTextEdit {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
        font-family: 'Courier New', monospace;
        font-size: 11px;
        background: #f9f9f9;
    }
"""

# Card styles
CARD = """
    QWidget {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
"""

CARD_HOVER = """
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
"""

# Status cards
STATUS_CONNECTED = """
    QWidget {
        background-color: #E8F5E9;
        border-radius: 6px;
        margin-bottom: 10px;
    }
"""

STATUS_DISCONNECTED = """
    QWidget {
        background-color: #FFF3E0;
        border-radius: 6px;
        margin-bottom: 10px;
    }
"""

# Info boxes
INFO_BOX = """
    QLabel {
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 12px;
        border-radius: 6px;
    }
"""

# Group box
GROUP_BOX = """
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
"""

# Search input
SEARCH_INPUT = """
    QLineEdit {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
"""

# Combo box
COMBO_BOX = """
    QComboBox {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
"""

# List widget
LIST_WIDGET = """
    QListWidget {
        border: none;
        background-color: #f9f9f9;
    }
"""


def get_btn_style(color: str, hover_color: str = None, text_color: str = 'white') -> str:
    """Generate a button style with custom colors."""
    if hover_color is None:
        hover_color = color
    return f"""
        QPushButton {{
            background-color: {color};
            color: {text_color};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """


# Icon mappings - centralized
CONTENT_ICONS = {
    'text': '📝',
    'image': '🖼️',
    'code': '💻',
    'url': '🔗',
    'json': '📊',
    'file': '📁',
    'default': '📎'
}

PLATFORM_ICONS = {
    'windows': '💻',
    'darwin': '🖥️',
    'linux': '🐧',
    'android': '📱',
    'ios': '📱',
    'mobile': '📱',
    'default': '📟'
}

STATUS_ICONS = {
    'connected': '🟢',
    'disconnected': '🔴',
    'pairing': '🟡',
    'online': '🟢',
    'offline': '🔴',
    'paired': '✔'
}


def get_icon(icon_type: str, key: str) -> str:
    """Get icon from icon mappings."""
    icons = {
        'content': CONTENT_ICONS,
        'platform': PLATFORM_ICONS,
        'status': STATUS_ICONS
    }
    mapping = icons.get(icon_type, {})
    return mapping.get(key, mapping.get('default', ''))


# Utility function for generating consistent widget styles
def card_style(hover: bool = False, selected: bool = False) -> str:
    """Generate card style with optional hover and selected states."""
    base = f"""
        QWidget {{
            background-color: {Colors.CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: 8px;
            padding: 5px;
        }}
    """
    if hover:
        base += f"""
        QWidget:hover {{
            background-color: {Colors.BACKGROUND_LIGHT};
            border: 1px solid {Colors.PRIMARY};
        }}
    """
    if selected:
        base = base.replace(f'border: 1px solid {Colors.BORDER}', 
                           f'border: 2px solid {Colors.PRIMARY}')
    return base
