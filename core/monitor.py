# core/monitor.py
"""
Clipboard monitoring system that automatically detects changes.
Completely different from manual message sending in chat app.
"""

import time
import threading
import hashlib
import io
import json
import base64
from typing import Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import pyperclip
from PIL import Image, ImageGrab
from loguru import logger

class ContentType(Enum):
    """Content types that can be synced"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    HTML = "html"
    CODE = "code"
    URL = "url"
    PASSWORD = "password"
    JSON = "json"

@dataclass
class ClipboardContent:
    """Structured clipboard data"""
    content: Any
    content_type: ContentType
    timestamp: datetime
    device_id: str
    checksum: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            'content_type': self.content_type.value,
            'timestamp': self.timestamp.isoformat(),
            'device_id': self.device_id,
            'checksum': self.checksum,
            'metadata': self.metadata
        }

class ClipboardMonitor:
    """
    Monitor clipboard for changes and categorize content.
    Features not in chat app:
    - Automatic detection
    - Content classification
    - Smart filtering
    - History tracking
    """
    
    def __init__(self, device_id: str, on_change_callback: Optional[Callable] = None):
        self.device_id = device_id
        self.on_change_callback = on_change_callback
        self.previous_checksum = None
        self.monitoring = False
        self.monitor_thread = None
        self.history = []
        self.max_history = 100
        
        # Smart filters
        self.filters = {
            'password_patterns': [
                r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]{8,}$',
                r'password:?\s*\S+',
                r'pwd:?\s*\S+'
            ],
            'sensitive_patterns': [
                r'\d{3}-\d{2}-\d{4}',  # SSN
                r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',  # Credit card
                r'[A-Za-z0-9+/]{40,}={0,2}$'  # API keys
            ],
            'code_indicators': [
                'function', 'class', 'import', 'def', 'var', 'const',
                '{', '}', '()', '=>', 'public', 'private'
            ]
        }
        
        # Content processors
        self.processors = {
            ContentType.TEXT: self._process_text,
            ContentType.IMAGE: self._process_image,
            ContentType.CODE: self._process_code,
            ContentType.URL: self._process_url,
            ContentType.JSON: self._process_json
        }
    
    def start_monitoring(self):
        """Start monitoring clipboard in background"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()
            logger.info("Clipboard monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Clipboard monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                content = self._get_clipboard_content()
                if content:
                    checksum = self._calculate_checksum(content)
                    
                    if checksum != self.previous_checksum:
                        self.previous_checksum = checksum
                        self._handle_new_content(content)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(0.5)  # Check every 500ms
    
    def _get_clipboard_content(self) -> Optional[Any]:
        """Get current clipboard content"""
        try:
            # Try text first (most common)
            text = pyperclip.paste()
            if text:
                return text
            
            # Try image (Windows/Mac)
            try:
                image = ImageGrab.grabclipboard()
                if image:
                    return image
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"Clipboard read error: {e}")
            return None
    
    def _handle_new_content(self, content: Any):
        """Process new clipboard content"""
        # Classify content
        content_type = self._classify_content(content)
        
        # Check if should sync
        if not self._should_sync(content, content_type):
            logger.debug(f"Content filtered: {content_type}")
            return
        
        # Process based on type
        processor = self.processors.get(content_type, self._process_generic)
        processed_content, metadata = processor(content)
        
        # Create structured data
        clipboard_data = ClipboardContent(
            content=processed_content,
            content_type=content_type,
            timestamp=datetime.now(),
            device_id=self.device_id,
            checksum=self._calculate_checksum(processed_content),
            metadata=metadata
        )
        
        # Add to history
        self._add_to_history(clipboard_data)
        
        # Trigger callback
        if self.on_change_callback:
            self.on_change_callback(clipboard_data)
        
        logger.info(f"New clipboard content: {content_type.value}")
    
    def _classify_content(self, content: Any) -> ContentType:
        """Intelligent content classification"""
        if isinstance(content, Image.Image):
            return ContentType.IMAGE
        
        if isinstance(content, str):
            # Check for JSON
            try:
                json.loads(content)
                return ContentType.JSON
            except:
                pass
            
            # Check for URL
            if content.startswith(('http://', 'https://', 'ftp://')):
                return ContentType.URL
            
            # Check for code
            code_score = sum(1 for indicator in self.filters['code_indicators'] 
                           if indicator in content)
            if code_score >= 3 or '\n' in content and any(
                line.strip().startswith(('#', '//', '/*', 'import', 'function'))
                for line in content.split('\n')
            ):
                return ContentType.CODE
            
            # Check for password
            import re
            for pattern in self.filters['password_patterns']:
                if re.match(pattern, content):
                    return ContentType.PASSWORD
            
            return ContentType.TEXT
        
        return ContentType.FILE
    
    def _should_sync(self, content: Any, content_type: ContentType) -> bool:
        """Smart filtering to prevent sensitive data sync"""
        if content_type == ContentType.PASSWORD:
            # Ask user for confirmation
            return self._prompt_sensitive_sync("password")
        
        if isinstance(content, str):
            import re
            # Check for sensitive patterns
            for pattern in self.filters['sensitive_patterns']:
                if re.search(pattern, content):
                    return self._prompt_sensitive_sync("sensitive data")
        
        # Size limits
        if isinstance(content, str) and len(content) > 1_000_000:  # 1MB text
            return False
        
        if isinstance(content, Image.Image):
            width, height = content.size
            if width * height > 10_000_000:  # 10MP image
                return False
        
        return True
    
    def _prompt_sensitive_sync(self, data_type: str) -> bool:
        """Prompt user for sensitive data sync"""
        # In real implementation, show GUI dialog
        logger.warning(f"Sensitive {data_type} detected, skipping sync")
        return False
    
    def _process_text(self, content: str) -> Tuple[str, Dict]:
        """Process text content"""
        metadata = {
            'length': len(content),
            'lines': content.count('\n') + 1,
            'words': len(content.split()),
            'has_formatting': any(c in content for c in ['\t', '\r', '\n'])
        }
        return content, metadata
    
    def _process_image(self, content: Image.Image) -> Tuple[bytes, Dict]:
        """Process image content"""
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        content.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Generate thumbnail
        thumbnail = content.copy()
        thumbnail.thumbnail((256, 256))
        thumb_byte_arr = io.BytesIO()
        thumbnail.save(thumb_byte_arr, format='PNG')
        
        metadata = {
            'width': content.width,
            'height': content.height,
            'format': content.format or 'PNG',
            'mode': content.mode,
            'size_bytes': len(img_bytes),
            'thumbnail': base64.b64encode(thumb_byte_arr.getvalue()).decode()
        }
        
        return img_bytes, metadata
    
    def _process_code(self, content: str) -> Tuple[str, Dict]:
        """Process code content"""
        # Detect language
        language = self._detect_language(content)
        
        metadata = {
            'language': language,
            'lines': content.count('\n') + 1,
            'has_syntax_highlighting': False
        }
        
        return content, metadata
    
    def _process_url(self, content: str) -> Tuple[str, Dict]:
        """Process URL content"""
        from urllib.parse import urlparse
        
        parsed = urlparse(content)
        metadata = {
            'domain': parsed.netloc,
            'path': parsed.path,
            'has_query': bool(parsed.query)
        }
        
        return content, metadata
    
    def _process_json(self, content: str) -> Tuple[str, Dict]:
        """Process JSON content"""
        try:
            data = json.loads(content)
            metadata = {
                'valid': True,
                'keys': len(data) if isinstance(data, dict) else None,
                'items': len(data) if isinstance(data, list) else None,
                'formatted': json.dumps(data, indent=2)
            }
        except:
            metadata = {'valid': False}
        
        return content, metadata
    
    def _process_generic(self, content: Any) -> Tuple[Any, Dict]:
        """Generic content processing"""
        return content, {'type': str(type(content))}
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code"""
        indicators = {
            'python': ['def ', 'import ', 'from ', '__init__', 'self.'],
            'javascript': ['const ', 'let ', 'var ', 'function ', '=>'],
            'java': ['public class', 'private ', 'void ', 'System.out'],
            'cpp': ['#include', 'std::', 'cout', 'nullptr'],
            'html': ['<html', '<div', '<body', '<!DOCTYPE'],
            'css': ['{', '}', ':', ';', 'px', 'color:'],
            'sql': ['SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE']
        }
        
        scores = {}
        for lang, patterns in indicators.items():
            scores[lang] = sum(1 for p in patterns if p in code)
        
        if scores:
            return max(scores, key=scores.get)
        return 'plain'
    
    def _calculate_checksum(self, content: Any) -> str:
        """Calculate content checksum"""
        if isinstance(content, str):
            data = content.encode()
        elif isinstance(content, bytes):
            data = content
        elif isinstance(content, Image.Image):
            data = content.tobytes()
        else:
            data = str(content).encode()
        
        return hashlib.sha256(data).hexdigest()
    
    def _add_to_history(self, content: ClipboardContent):
        """Add content to history"""
        self.history.append(content)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, limit: int = 10) -> list:
        """Get recent clipboard history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear clipboard history"""
        self.history = []
        self.previous_checksum = None