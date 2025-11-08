# core/sync_engine.py
"""
Main synchronization engine that coordinates all components.
This is the brain of the application.
"""

import asyncio
import threading
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib
import base64

from loguru import logger
import pyperclip

from .encryption import HybridEncryption
from .monitor import ClipboardMonitor, ClipboardContent, ContentType
from .network import NetworkDiscovery, P2PCommunication, Device, DeviceStatus

@dataclass
class SyncSettings:
    """User preferences for syncing"""
    auto_sync: bool = True
    sync_text: bool = True
    sync_images: bool = True
    sync_files: bool = True
    require_confirmation: bool = False
    max_size_mb: int = 10
    excluded_apps: List[str] = None
    trusted_networks: List[str] = None
    
    def __post_init__(self):
        if self.excluded_apps is None:
            self.excluded_apps = ['password_manager', 'banking_app']
        if self.trusted_networks is None:
            self.trusted_networks = []

class SyncEngine:
    """
    Orchestrates all components for seamless clipboard sync.
    Much more sophisticated than simple chat message passing.
    """
    
    def __init__(self, device_name: str = None):
        # Core components
        self.encryption = HybridEncryption()
        self.device_id = self.encryption.device_id
        self.device_name = device_name or f"Device-{self.device_id[:8]}"
        
        # Initialize components
        self.monitor = ClipboardMonitor(
            self.device_id,
            on_change_callback=self._on_clipboard_change
        )
        
        self.discovery = NetworkDiscovery(self.device_id, self.device_name)
        self.p2p = P2PCommunication(self.device_id, self.encryption)
        
        # Cloud relay client (lazy initialization)
        self.cloud_relay = None
        self.cloud_relay_enabled = False
        
        # Settings and state
        self.settings = SyncSettings()
        self.is_running = False
        self.paired_devices: Dict[str, Device] = {}
        self.sync_history: List[Dict] = []
        self.incoming_clipboard = None  # Prevent echo
        
        # Setup callbacks
        self.discovery.on_device_discovered = self._on_device_discovered
        self.discovery.on_device_lost = self._on_device_lost
        self.p2p.register_handler('clipboard', self._handle_incoming_clipboard)
        
        # Async event loop for P2P
        self.loop = None
        self.loop_thread = None
    
    def start(self):
        """Start the sync engine"""
        if self.is_running:
            logger.warning("Sync engine already running")
            return
        
        self.is_running = True
        
        # Create new event loop if previous one was stopped
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            self.loop_thread = threading.Thread(
                target=self._run_async_loop,
                daemon=True
            )
            self.loop_thread.start()
        
        # Start components
        self.monitor.start_monitoring()
        self.discovery.start_discovery()
        
        # Start P2P server
        asyncio.run_coroutine_threadsafe(
            self.p2p.start_server(self.discovery.local_ip, self.discovery.port),
            self.loop
        )
        
        logger.info(f"Sync engine started - Device: {self.device_name}")
    
    def stop(self):
        """Stop the sync engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop components first
        self.monitor.stop_monitoring()
        
        # Stop P2P server with proper async handling
        if self.loop and not self.loop.is_closed():
            try:
                # Create stop coroutine
                stop_coro = self.p2p.stop_server()
                # Run it in the event loop
                future = asyncio.run_coroutine_threadsafe(stop_coro, self.loop)
                # Wait for it to complete
                future.result(timeout=3)
            except asyncio.TimeoutError:
                logger.warning("P2P server stop timed out")
            except Exception as e:
                logger.warning(f"Error stopping P2P server: {e}")
        
        # Stop discovery (this recreates zeroconf for next start)
        try:
            self.discovery.stop_discovery()
        except Exception as e:
            logger.warning(f"Error stopping discovery: {e}")
        
        # Stop event loop gracefully
        if self.loop and not self.loop.is_closed():
            try:
                # Cancel all pending tasks
                try:
                    # Get all tasks for this loop
                    all_tasks = [task for task in asyncio.all_tasks(self.loop) 
                                if not task.done()]
                    
                    # Cancel each one
                    for task in all_tasks:
                        self.loop.call_soon_threadsafe(task.cancel)
                except Exception as e:
                    logger.debug(f"Could not cancel tasks: {e}")
                
                # Stop the loop
                self.loop.call_soon_threadsafe(self.loop.stop)
            except Exception as e:
                logger.warning(f"Error stopping event loop: {e}")
        
        # Wait for thread to finish BEFORE closing loop
        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=5)
            if self.loop_thread.is_alive():
                logger.warning("Event loop thread did not stop in time")
        
        # Now close the event loop
        if self.loop and not self.loop.is_closed():
            try:
                self.loop.close()
            except Exception as e:
                logger.warning(f"Error closing event loop: {e}")
        
        # Set to None so start() creates a new one
        self.loop = None
        self.loop_thread = None
        
        logger.info("Sync engine stopped")
    
    def _run_async_loop(self):
        """Run async event loop in thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def _on_clipboard_change(self, clipboard_data: ClipboardContent):
        """Handle local clipboard change"""
        # Don't sync if it came from another device (local or cloud)
        if self.incoming_clipboard:
            # Check if it's the same content
            if self.incoming_clipboard == clipboard_data.checksum:
                self.incoming_clipboard = None
                return
            # For text content, also check the actual content
            if clipboard_data.content_type == ContentType.TEXT and \
               isinstance(clipboard_data.content, str) and \
               self.incoming_clipboard == clipboard_data.content:
                self.incoming_clipboard = None
                return
        
        # Check settings
        if not self._should_sync_content(clipboard_data):
            return
        
        # Add to history
        self._add_to_history('sent', clipboard_data)
        
        # Prepare content for encryption
        content_bytes = self._content_to_bytes(clipboard_data)
        
        # Encrypt for all paired devices (local P2P)
        if self.paired_devices:
            encrypted_data = self.encryption.encrypt_content(
                content_bytes,
                clipboard_data.content_type.value
            )
            
            # Add metadata
            encrypted_data['metadata'] = clipboard_data.metadata
            encrypted_data['timestamp'] = clipboard_data.timestamp.isoformat()
            
            # Broadcast to all devices
            asyncio.run_coroutine_threadsafe(
                self.p2p.broadcast_clipboard(encrypted_data),
                self.loop
            )
            
            logger.info(f"Clipboard synced to {len(self.paired_devices)} devices")
        
        # Send to cloud relay if connected (text and images)
        if self.cloud_relay_enabled:
            if clipboard_data.content_type == ContentType.TEXT:
                text_content = clipboard_data.content if isinstance(clipboard_data.content, str) else str(clipboard_data.content)
                asyncio.run_coroutine_threadsafe(
                    self._send_to_cloud_relay(text_content, 'text'),
                    self.loop
                )
            elif clipboard_data.content_type == ContentType.IMAGE:
                # Send image data
                asyncio.run_coroutine_threadsafe(
                    self._send_to_cloud_relay(content_bytes, 'image'),
                    self.loop
                )
    
    def _on_device_discovered(self, device: Device):
        """Handle new device discovery"""
        logger.info(f"Device discovered: {device.name}")
        
        # Auto-pair if trusted network
        if self.settings.trusted_networks:
            # Check if on trusted network
            # For now, auto-pair all devices (can add network check later)
            self._pair_with_device(device)
    
    def _on_device_lost(self, device: Device):
        """Handle device disconnection"""
        if device.device_id in self.paired_devices:
            del self.paired_devices[device.device_id]
            logger.info(f"Device disconnected: {device.name}")
    
    def _pair_with_device(self, device: Device):
        """Pair with a discovered device"""
        asyncio.run_coroutine_threadsafe(
            self.p2p.connect_to_device(device),
            self.loop
        )
        
        device.status = DeviceStatus.PAIRED
        self.paired_devices[device.device_id] = device
        logger.info(f"Paired with device: {device.name}")
    
    async def _handle_incoming_clipboard(self, content: bytes, content_type: str, 
                                        device_id: str):
        """Handle incoming clipboard from peer"""
        try:
            # Convert bytes back to appropriate type
            clipboard_content = self._bytes_to_content(content, content_type)
            
            # Set flag to prevent echo
            self.incoming_clipboard = hashlib.sha256(content).hexdigest()
            
            # Update local clipboard
            if content_type == ContentType.TEXT.value:
                pyperclip.copy(clipboard_content)
            elif content_type == ContentType.IMAGE.value:
                # Handle image (platform specific)
                self._set_image_clipboard(clipboard_content)
            
            # Add to history
            device = self.paired_devices.get(device_id)
            device_name = device.name if device else device_id
            
            self._add_to_history('received', {
                'content': clipboard_content,
                'content_type': content_type,
                'from_device': device_name,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Clipboard received from {device_name}")
            
        except Exception as e:
            logger.error(f"Error handling incoming clipboard: {e}")
    
    def _should_sync_content(self, clipboard_data: ClipboardContent) -> bool:
        """Check if content should be synced based on settings"""
        if not self.settings.auto_sync:
            return False
        
        # Check content type settings
        if clipboard_data.content_type == ContentType.TEXT and not self.settings.sync_text:
            return False
        if clipboard_data.content_type == ContentType.IMAGE and not self.settings.sync_images:
            return False
        
        # Check size limits
        content_size = len(str(clipboard_data.content))
        if content_size > self.settings.max_size_mb * 1024 * 1024:
            logger.warning(f"Content too large: {content_size / 1024 / 1024:.2f}MB")
            return False
        
        # Require confirmation for sensitive content
        if self.settings.require_confirmation:
            if clipboard_data.content_type in [ContentType.PASSWORD, ContentType.FILE]:
                # In real app, show GUI confirmation
                logger.info("Confirmation required for sensitive content")
                return False
        
        return True
    
    def _content_to_bytes(self, clipboard_data: ClipboardContent) -> bytes:
        """Convert clipboard content to bytes for encryption"""
        content = clipboard_data.content
        
        if isinstance(content, str):
            return content.encode('utf-8')
        elif isinstance(content, bytes):
            return content
        else:
            # Serialize complex types
            return json.dumps({
                'content': str(content),
                'type': clipboard_data.content_type.value
            }).encode('utf-8')
    
    def _bytes_to_content(self, data: bytes, content_type: str):
        """Convert bytes back to appropriate content type"""
        if content_type == ContentType.TEXT.value:
            return data.decode('utf-8')
        elif content_type == ContentType.IMAGE.value:
            return data  # Return as bytes for image processing
        elif content_type == ContentType.JSON.value:
            return json.loads(data.decode('utf-8'))
        else:
            try:
                # Try to deserialize
                obj = json.loads(data.decode('utf-8'))
                return obj.get('content', data.decode('utf-8'))
            except:
                return data.decode('utf-8', errors='ignore')
    
    def _set_image_clipboard(self, image_data: bytes):
        """Set image to clipboard (platform specific)"""
        try:
            from PIL import Image
            import io
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Platform specific clipboard handling
            # This is simplified - real implementation would use platform APIs
            logger.info("Image clipboard set (platform specific implementation needed)")
            
        except Exception as e:
            logger.error(f"Error setting image clipboard: {e}")
    
    def _add_to_history(self, action: str, data: any):
        """Add sync event to history"""
        history_entry = {
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'data': data if isinstance(data, dict) else {
                'content_type': getattr(data, 'content_type', 'unknown'),
                'device': getattr(data, 'device_id', 'unknown')
            }
        }
        
        self.sync_history.append(history_entry)
        
        # Limit history
        if len(self.sync_history) > 1000:
            self.sync_history = self.sync_history[-1000:]
    
    def get_paired_devices(self) -> List[Device]:
        """Get list of paired devices"""
        return list(self.paired_devices.values())
    
    def get_discovered_devices(self) -> List[Device]:
        """Get list of discovered devices"""
        return self.discovery.get_devices()
    
    def get_sync_history(self, limit: int = 50) -> List[Dict]:
        """Get recent sync history"""
        return self.sync_history[-limit:]
    
    def update_settings(self, **kwargs):
        """Update sync settings"""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        logger.info(f"Settings updated: {kwargs.keys()}")
    
    def pair_with_qr_code(self, qr_data: str) -> bool:
        """Pair with device using QR code data"""
        try:
            data = json.loads(qr_data)
            device = Device(
                device_id=data['device_id'],
                name=data['device_name'],
                ip_address=data['ip'],
                port=data['port'],
                status=DeviceStatus.PAIRING,
                last_seen=datetime.now(),
                public_key=data.get('public_key')
            )
            
            if device.public_key:
                self.encryption.import_peer_key(device.device_id, device.public_key)
            
            self._pair_with_device(device)
            return True
            
        except Exception as e:
            logger.error(f"Error pairing with QR code: {e}")
            return False
    
    def generate_pairing_qr(self) -> str:
        """Generate QR code data for pairing"""
        qr_data = {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'ip': self.discovery.local_ip,
            'port': self.discovery.port,
            'public_key': self.encryption.export_public_key(),
            'timestamp': datetime.now().isoformat()
        }
        return json.dumps(qr_data)
    
    # ==================== Cloud Relay Methods ====================
    
    async def connect_to_cloud_relay(self, server_url: str, room_id: str) -> bool:
        """
        Connect to cloud relay server for mobile sync
        
        Args:
            server_url: URL of the cloud relay server (e.g., https://your-app.fly.dev)
            room_id: Room ID to join for syncing
            
        Returns:
            True if connected successfully
        """
        try:
            # Import here to avoid circular dependency
            from .cloud_relay_client import CloudRelayClient
            
            # Create cloud relay client if not exists
            if self.cloud_relay is None:
                self.cloud_relay = CloudRelayClient(
                    on_clipboard_received=self._on_cloud_clipboard_received,
                    on_devices_updated=self._on_devices_updated
                )
            
            # Get device name from system
            import platform
            import socket
            device_name = socket.gethostname() or platform.node() or 'Desktop'
            
            # Connect to server
            success = await self.cloud_relay.connect_to_server(
                server_url, room_id, self.device_id, device_name
            )
            
            if success:
                self.cloud_relay_enabled = True
                logger.info(f"Connected to cloud relay: {server_url} in room {room_id}")
            else:
                logger.error("Failed to connect to cloud relay")
            
            return success
            
        except Exception as e:
            logger.error(f"Error connecting to cloud relay: {e}")
            return False
    
    async def disconnect_from_cloud_relay(self):
        """Disconnect from cloud relay server"""
        try:
            if self.cloud_relay:
                await self.cloud_relay.disconnect_from_server()
                self.cloud_relay_enabled = False
                logger.info("Disconnected from cloud relay")
        except Exception as e:
            logger.error(f"Error disconnecting from cloud relay: {e}")
    
    def _on_devices_updated(self, devices: list):
        """Handle device list update from cloud relay"""
        try:
            logger.info(f"Device list updated: {len(devices)} devices")
            # TODO: Update GUI with device list
        except Exception as e:
            logger.error(f"Error handling devices update: {e}")
    
    def _on_cloud_clipboard_received(self, content: str, data_type: str):
        """Handle clipboard data received from cloud relay"""
        try:
            logger.info(f"Received clipboard from cloud relay: {data_type}")
            
            # Set incoming clipboard to prevent echo
            self.incoming_clipboard = content
            
            # Update local clipboard
            if data_type == 'text':
                pyperclip.copy(content)
                logger.info("✅ Text clipboard updated from cloud relay")
            elif data_type == 'image':
                # Handle image data
                try:
                    from PIL import Image
                    import io
                    
                    # Remove data URL prefix if present
                    if content.startswith('data:image'):
                        content = content.split(',')[1]
                    
                    # Decode base64 image
                    img_data = base64.b64decode(content)
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Copy to clipboard (Windows)
                    import win32clipboard
                    from io import BytesIO
                    
                    output = BytesIO()
                    img.convert('RGB').save(output, 'BMP')
                    data = output.getvalue()[14:]  # Remove BMP header
                    output.close()
                    
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    
                    logger.info("✅ Image clipboard updated from cloud relay")
                except ImportError:
                    logger.warning("PIL or win32clipboard not available, saving image to file instead")
                    # Fallback: save to file
                    import tempfile
                    import os
                    from datetime import datetime
                    
                    if content.startswith('data:image'):
                        content = content.split(',')[1]
                    
                    img_data = base64.b64decode(content)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"clipboard_image_{timestamp}.png"
                    filepath = os.path.join(tempfile.gettempdir(), filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    
                    logger.info(f"✅ Image saved to: {filepath}")
                except Exception as img_err:
                    logger.error(f"Error processing image: {img_err}")
            
            # Clear incoming after a moment
            def clear_incoming():
                import time
                time.sleep(0.5)
                self.incoming_clipboard = None
            
            threading.Thread(target=clear_incoming, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error processing cloud clipboard: {e}")
            import traceback
            traceback.print_exc()
    
    async def _send_to_cloud_relay(self, content: str, content_type: str):
        """Send clipboard data to cloud relay"""
        if not self.cloud_relay_enabled or not self.cloud_relay:
            return
        
        try:
            await self.cloud_relay.send_clipboard(content, content_type)
            logger.info(f"Sent clipboard to cloud relay: {content_type}")
        except Exception as e:
            logger.error(f"Failed to send to cloud relay: {e}")
    
    def is_cloud_relay_connected(self) -> bool:
        """Check if connected to cloud relay"""
        return self.cloud_relay_enabled and self.cloud_relay and self.cloud_relay.is_connected()