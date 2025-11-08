"""
Cloud Relay Client - Connects desktop app to cloud relay server for mobile sync
"""

import asyncio
import base64
from datetime import datetime
from typing import Optional, Callable
from loguru import logger
import socketio


class CloudRelayClient:
    """Client for connecting to cloud relay server"""
    
    def __init__(self, on_clipboard_received: Optional[Callable] = None, on_devices_updated: Optional[Callable] = None):
        """
        Initialize cloud relay client
        
        Args:
            on_clipboard_received: Callback function when clipboard data is received
            on_devices_updated: Callback function when device list is updated
        """
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            logger=False,
            engineio_logger=False
        )
        self.server_url: Optional[str] = None
        self.room_id: Optional[str] = None
        self.device_id: Optional[str] = None
        self.device_name: str = 'Desktop'
        self.connected = False
        self.on_clipboard_received = on_clipboard_received
        self.on_devices_updated = on_devices_updated
        
        # Setup event handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup Socket.IO event handlers"""
        
        @self.sio.event
        async def connect():
            """Handle successful connection"""
            self.connected = True
            logger.info(f"Connected to cloud relay: {self.server_url}")
            
            # Register device if we have room_id
            if self.room_id:
                await self.sio.emit('register', {
                    'roomId': self.room_id,
                    'deviceId': self.device_id,
                    'deviceName': self.device_name if hasattr(self, 'device_name') else 'Desktop',
                    'deviceType': 'desktop'
                })
                logger.info(f"Registered to room: {self.room_id}")
        
        @self.sio.event
        async def disconnect():
            """Handle disconnection"""
            self.connected = False
            logger.warning("Disconnected from cloud relay")
        
        @self.sio.event
        async def connect_error(data):
            """Handle connection error"""
            logger.error(f"Connection error: {data}")
        
        @self.sio.event
        async def room_joined(data):
            """Handle room joined confirmation"""
            logger.info(f"Room joined confirmation: {data}")
        
        @self.sio.event
        async def room_devices(devices):
            """Handle room devices list"""
            logger.info(f"Room devices updated: {len(devices)} devices")
            if self.on_devices_updated:
                self.on_devices_updated(devices)
        
        @self.sio.event
        async def device_joined(data):
            """Handle new device joining"""
            logger.info(f"Device joined: {data.get('deviceName', 'Unknown')}")
        
        @self.sio.event
        async def device_left(data):
            """Handle device leaving"""
            logger.info(f"Device left: {data.get('deviceName', 'Unknown')}")
        
        @self.sio.event
        async def clipboard_data(data):
            """Handle received clipboard data"""
            try:
                # Extract data
                content = data.get('data', '')
                data_type = data.get('type', 'text')
                from_device = data.get('from_device', 'unknown')
                
                logger.info(f"Received clipboard from {from_device}: {data_type} ({len(content)} bytes)")
                
                # Decode base64 if it's text
                if data_type == 'text':
                    try:
                        content = base64.b64decode(content).decode('utf-8')
                    except Exception as e:
                        logger.warning(f"Could not decode base64, using raw: {e}")
                
                # Call callback if provided
                if self.on_clipboard_received:
                    self.on_clipboard_received(content, data_type)
                    
            except Exception as e:
                logger.error(f"Error processing clipboard data: {e}")
        
        @self.sio.event
        async def error(data):
            """Handle error from server"""
            logger.error(f"Server error: {data.get('message', 'Unknown error')}")
    
    async def connect_to_server(self, server_url: str, room_id: str, device_id: str, device_name: str = 'Desktop') -> bool:
        """
        Connect to cloud relay server
        
        Args:
            server_url: URL of the cloud relay server (e.g., https://your-app.fly.dev)
            room_id: Room ID to join for syncing
            device_id: Unique device identifier
            device_name: Name of this device (default: 'Desktop')
            
        Returns:
            True if connected successfully
        """
        try:
            # If already connected, disconnect first
            if self.sio.connected:
                logger.info("Already connected, disconnecting first...")
                await self.disconnect_from_server()
                await asyncio.sleep(0.5)
            
            # Store connection info
            self.server_url = server_url
            self.room_id = room_id
            self.device_id = device_id
            self.device_name = device_name
            
            # Ensure URL has protocol
            if not server_url.startswith(('http://', 'https://')):
                server_url = 'https://' + server_url
            
            logger.info(f"Connecting to cloud relay: {server_url}")
            
            # Connect to server
            await self.sio.connect(
                server_url,
                transports=['websocket', 'polling']
            )
            
            # Wait a moment for connection to establish
            await asyncio.sleep(0.5)
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Failed to connect to cloud relay: {e}")
            self.connected = False
            return False
    
    async def disconnect_from_server(self):
        """Disconnect from cloud relay server"""
        try:
            if self.sio.connected:
                # Leave room
                if self.room_id:
                    await self.sio.emit('leave_room', {
                        'room_id': self.room_id,
                        'device_id': self.device_id
                    })
                
                # Disconnect
                await self.sio.disconnect()
                logger.info("Disconnected from cloud relay")
            
            self.connected = False
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    async def send_clipboard(self, content, data_type: str = 'text'):
        """
        Send clipboard data to cloud relay
        
        Args:
            content: Clipboard content to send (str for text, bytes for image)
            data_type: Type of data ('text', 'image', etc.)
        """
        if not self.connected:
            logger.warning("Not connected to cloud relay")
            return False
        
        try:
            # Encode content based on type
            if data_type == 'text':
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            elif data_type == 'image':
                # Image is already bytes, encode to base64
                if isinstance(content, bytes):
                    # Convert to data URL format
                    import io
                    from PIL import Image
                    img = Image.open(io.BytesIO(content))
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    img_bytes = buffered.getvalue()
                    encoded_content = f"data:image/png;base64,{base64.b64encode(img_bytes).decode('utf-8')}"
                else:
                    encoded_content = content
            else:
                logger.warning(f"Unsupported data type: {data_type}")
                return False
            
            # Send to server
            await self.sio.emit('clipboard_data', {
                'encrypted_content': encoded_content,
                'content_type': data_type,
                'timestamp': int(datetime.now().timestamp() * 1000)
            })
            
            logger.info(f"Sent clipboard to cloud relay: {data_type} ({len(str(encoded_content))} chars)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send clipboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to cloud relay"""
        return self.connected and self.sio.connected
