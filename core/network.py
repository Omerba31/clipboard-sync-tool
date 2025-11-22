# core/network.py
"""
P2P network discovery and communication.
Uses mDNS for automatic discovery - no manual IP entry like chat app.
"""

import socket
import json
import threading
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import asyncio

from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser, ServiceListener
import socketio
from aiohttp import web
from loguru import logger

class DeviceStatus(Enum):
    """Device connection status"""
    ONLINE = "online"
    OFFLINE = "offline"
    PAIRING = "pairing"
    PAIRED = "paired"

@dataclass
class Device:
    """Represents a network device"""
    device_id: str
    name: str
    ip_address: str
    port: int
    status: DeviceStatus
    last_seen: datetime
    trust_level: str = "read-only"  # read-only, read-write, admin
    public_key: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'status': self.status.value,
            'last_seen': self.last_seen.isoformat()
        }

class NetworkDiscovery(ServiceListener):
    """
    Automatic device discovery using mDNS/Bonjour.
    Completely different from manual IP connection in chat app.
    """
    
    SERVICE_TYPE = "_clipsync._tcp.local."
    
    def __init__(self, device_id: str, device_name: str):
        self.device_id = device_id
        self.device_name = device_name
        self.zeroconf = Zeroconf()
        self.browser = None
        self.discovered_devices: Dict[str, Device] = {}
        self.service_info = None
        self.on_device_discovered = None
        self.on_device_lost = None
        
        # Get local IP
        self.local_ip = self._get_local_ip()
        self.port = self._find_free_port()
    
    def start_discovery(self):
        """Start advertising and discovering devices"""
        # Advertise our service
        self._advertise_service()
        
        # Browse for other services
        self.browser = ServiceBrowser(
            self.zeroconf,
            self.SERVICE_TYPE,
            self
        )
        logger.info(f"Network discovery started on {self.local_ip}:{self.port}")
    
    def stop_discovery(self):
        """Stop discovery and cleanup"""
        if self.service_info:
            try:
                self.zeroconf.unregister_service(self.service_info)
            except Exception as e:
                logger.warning(f"Error unregistering service: {e}")
        
        if self.browser:
            try:
                self.browser.cancel()
            except Exception as e:
                logger.warning(f"Error canceling browser: {e}")
        
        try:
            self.zeroconf.close()
        except Exception as e:
            logger.warning(f"Error closing zeroconf: {e}")
        
        # Create new zeroconf instance for restart
        self.zeroconf = Zeroconf()
        self.browser = None
        self.service_info = None
        
        logger.info("Network discovery stopped")
    
    def _advertise_service(self):
        """Advertise our service on the network"""
        self.service_info = ServiceInfo(
            self.SERVICE_TYPE,
            f"{self.device_name}.{self.SERVICE_TYPE}",
            addresses=[socket.inet_aton(self.local_ip)],
            port=self.port,
            properties={
                'device_id': self.device_id,
                'device_name': self.device_name,
                'version': '1.0',
                'capabilities': 'text,image,file',
                'platform': self._get_platform()
            }
        )
        
        self.zeroconf.register_service(self.service_info)
        logger.info(f"Service advertised: {self.device_name}")
    
    def add_service(self, zeroconf, service_type, name):
        """Called when a service is discovered"""
        info = zeroconf.get_service_info(service_type, name)
        if info:
            self._process_discovered_device(info)
    
    def remove_service(self, zeroconf, service_type, name):
        """Called when a service is lost"""
        # Find device by service name
        for device_id, device in self.discovered_devices.items():
            if f"{device.name}.{self.SERVICE_TYPE}" == name:
                device.status = DeviceStatus.OFFLINE
                logger.info(f"Device lost: {device.name}")
                
                if self.on_device_lost:
                    self.on_device_lost(device)
                break
    
    def update_service(self, zeroconf, service_type, name):
        """Called when service is updated"""
        self.remove_service(zeroconf, service_type, name)
        self.add_service(zeroconf, service_type, name)
    
    def _process_discovered_device(self, info: ServiceInfo):
        """Process discovered device information"""
        # Handle different zeroconf versions
        try:
            if hasattr(info, 'decoded_properties'):
                properties = info.decoded_properties
            elif hasattr(info, 'properties'):
                properties = info.properties
            else:
                properties = {}
        except:
            properties = {}
    
        # Helper function to safely extract property value
        def get_property(key):
            # Try bytes key first
            value = properties.get(key.encode() if isinstance(key, str) else key)
            if value is None:
                # Try string key
                value = properties.get(key.decode() if isinstance(key, bytes) else key)
            # Decode if bytes
            if isinstance(value, bytes):
                return value.decode('utf-8', errors='ignore')
            return value if value is not None else ''
        
        # Skip ourselves
        device_id = get_property('device_id')
        if device_id == self.device_id:
            return
        
        device_name = get_property('device_name') or 'Unknown Device'
    
        device = Device(
            device_id=device_id or 'unknown',
            name=device_name,
            ip_address=socket.inet_ntoa(info.addresses[0]) if info.addresses else '0.0.0.0',
            port=info.port,
            status=DeviceStatus.ONLINE,
            last_seen=datetime.now()
    )
        
        logger.debug(f"Processed device - ID: {device.device_id}, Name: '{device.name}', IP: {device.ip_address}")
        
        # Check if already discovered
        if device.device_id not in self.discovered_devices:
            self.discovered_devices[device.device_id] = device
            logger.info(f"New device discovered: {device.name} ({device.ip_address})")
            
            if self.on_device_discovered:
                self.on_device_discovered(device)
        else:
            # Update existing device
            self.discovered_devices[device.device_id] = device
    
    def get_devices(self) -> List[Device]:
        """Get list of discovered devices"""
        return list(self.discovered_devices.values())
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _find_free_port(self) -> int:
        """Find a free port for our service"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def _get_platform(self) -> str:
        """Get platform identifier"""
        import platform
        return platform.system().lower()


class P2PCommunication:
    """
    Real-time P2P communication using SocketIO.
    Supports multiple simultaneous connections unlike chat app.
    """
    
    def __init__(self, device_id: str, encryption_engine):
        self.device_id = device_id
        self.encryption = encryption_engine
        self.sio_server = socketio.AsyncServer(cors_allowed_origins='*')
        self.sio_clients: Dict[str, socketio.AsyncClient] = {}
        self.app = web.Application()
        self.sio_server.attach(self.app)
        self.message_handlers = {}
        self.runner = None
        self.on_device_paired = None  # Callback when device pairs
        
        # Setup server handlers
        self._setup_server_handlers()
    
    def _setup_server_handlers(self):
        """Setup SocketIO server event handlers"""
        
        @self.sio_server.event
        async def connect(sid, environ):
            """Handle client connection"""
            logger.info(f"Client connected: {sid}")
            await self.sio_server.emit('welcome', {
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat()
            }, room=sid)
        
        @self.sio_server.event
        async def disconnect(sid):
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {sid}")
        
        @self.sio_server.event
        async def pair_request(sid, data):
            """Handle pairing request"""
            device_id = data.get('device_id')
            public_key = data.get('public_key')
            
            # Store public key
            self.encryption.import_peer_key(device_id, public_key)
            
            # Send our public key
            await self.sio_server.emit('pair_response', {
                'device_id': self.device_id,
                'public_key': self.encryption.export_public_key(),
                'accepted': True
            }, room=sid)
            
            logger.info(f"Paired with device: {device_id}")
            
            # Notify that pairing succeeded
            if self.on_device_paired:
                self.on_device_paired(device_id)
        
        @self.sio_server.event
        async def clipboard_sync(sid, data):
            """Handle clipboard sync data"""
            try:
                # Decrypt content
                content, content_type = self.encryption.decrypt_content(data)
                
                # Process through handlers
                if 'clipboard' in self.message_handlers:
                    await self.message_handlers['clipboard'](
                        content, 
                        content_type, 
                        data.get('device_id')
                    )
                
                # Send acknowledgment
                await self.sio_server.emit('sync_ack', {
                    'success': True,
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Error processing clipboard sync: {e}")
                await self.sio_server.emit('sync_ack', {
                    'success': False,
                    'error': str(e)
                }, room=sid)
    
    async def start_server(self, host: str, port: int):
        """Start the SocketIO server"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()
        logger.info(f"P2P server started on {host}:{port}")
    
    async def stop_server(self):
        """Stop the server"""
        if self.runner:
            try:
                await self.runner.cleanup()
                logger.debug("P2P server runner cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up P2P runner: {e}")
        
        # Close all client connections
        for device_id, client in list(self.sio_clients.items()):
            try:
                await client.disconnect()
            except Exception as e:
                logger.debug(f"Error disconnecting client {device_id}: {e}")
        
        self.sio_clients.clear()
    
    async def connect_to_device(self, device: Device):
        """Connect to a discovered device"""
        if device.device_id in self.sio_clients:
            logger.debug(f"Already connected to {device.name}")
            return
        
        client = socketio.AsyncClient()
        
        @client.event
        async def connect():
            logger.info(f"Connected to {device.name}")
            
            # Send pairing request
            await client.emit('pair_request', {
                'device_id': self.device_id,
                'public_key': self.encryption.export_public_key()
            })
        
        @client.event
        async def disconnect():
            logger.info(f"Disconnected from {device.name}")
            if device.device_id in self.sio_clients:
                del self.sio_clients[device.device_id]
        
        @client.event
        async def pair_response(data):
            if data.get('accepted'):
                # Store public key
                self.encryption.import_peer_key(
                    data['device_id'],
                    data['public_key']
                )
                logger.info(f"Pairing accepted by {device.name}")
                
                # Notify that pairing succeeded
                if self.on_device_paired:
                    self.on_device_paired(device.device_id)
        
        @client.event
        async def clipboard_sync(data):
            """Receive clipboard sync from peer"""
            try:
                content, content_type = self.encryption.decrypt_content(data)
                
                if 'clipboard' in self.message_handlers:
                    await self.message_handlers['clipboard'](
                        content,
                        content_type,
                        data.get('device_id')
                    )
            except Exception as e:
                logger.error(f"Error receiving clipboard: {e}")
        
        try:
            await client.connect(f'http://{device.ip_address}:{device.port}')
            self.sio_clients[device.device_id] = client
        except Exception as e:
            logger.error(f"Failed to connect to {device.name}: {e}")
    
    async def broadcast_clipboard(self, encrypted_data: Dict):
        """Broadcast clipboard to all connected devices"""
        tasks = []
        
        # Send to server clients
        tasks.append(
            self.sio_server.emit('clipboard_sync', encrypted_data)
        )
        
        # Send to connected peers
        for device_id, client in self.sio_clients.items():
            if device_id in encrypted_data.get('encrypted_keys', {}):
                tasks.append(
                    client.emit('clipboard_sync', encrypted_data)
                )
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"Clipboard broadcasted to {len(self.sio_clients)} devices")
    
    def register_handler(self, event: str, handler: Callable):
        """Register message handler"""
        self.message_handlers[event] = handler
    
    async def disconnect_from_device(self, device_id: str):
        """Disconnect from a specific device"""
        if device_id in self.sio_clients:
            await self.sio_clients[device_id].disconnect()
            del self.sio_clients[device_id]
            logger.info(f"Disconnected from device: {device_id}")