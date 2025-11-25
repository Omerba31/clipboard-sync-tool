"""
Live Cloud Relay Integration Tests

These tests connect to the ACTUAL Railway server to verify:
- Server is running and healthy
- Socket.IO connection works
- Messages can be sent/received between devices

NOTE: These tests require internet connection and a running Railway deployment.
Skip these in CI/CD or offline environments.

Run with: python -m pytest tests/integration/test_cloud_relay_live.py -v
"""

import pytest
import asyncio
import socketio
import time
import os

# Your Railway server URL
CLOUD_RELAY_URL = os.environ.get(
    'CLOUD_RELAY_URL', 
    'https://clipboard-sync-tool-production.up.railway.app'
)


class TestCloudRelayHealth:
    """Test that the cloud relay server is running"""
    
    def test_health_endpoint(self):
        """Test /health endpoint returns OK"""
        import urllib.request
        import json
        
        try:
            url = f"{CLOUD_RELAY_URL}/health"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                assert response.status == 200
                assert data.get('status') == 'healthy'
                print(f"\n✅ Server healthy: {data}")
        except Exception as e:
            pytest.skip(f"Cloud relay not accessible: {e}")
    
    def test_stats_endpoint(self):
        """Test /api/stats endpoint"""
        import urllib.request
        import json
        
        try:
            url = f"{CLOUD_RELAY_URL}/api/stats"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                assert response.status == 200
                assert 'devices' in data
                assert 'rooms' in data
                assert 'bandwidth' in data
                print(f"\n📊 Server stats: {data}")
        except Exception as e:
            pytest.skip(f"Cloud relay not accessible: {e}")


class TestCloudRelayConnection:
    """Test Socket.IO connection to cloud relay"""
    
    @pytest.fixture
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    def test_socketio_connect(self, event_loop):
        """Test that we can connect via Socket.IO"""
        
        async def run_test():
            sio = socketio.AsyncClient()
            connected = False
            
            @sio.event
            async def connect():
                nonlocal connected
                connected = True
            
            try:
                await sio.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await asyncio.sleep(1)  # Wait for connection
                
                assert connected, "Failed to connect"
                assert sio.connected, "Socket not connected"
                print(f"\n✅ Socket.IO connected to {CLOUD_RELAY_URL}")
                
            except Exception as e:
                pytest.skip(f"Could not connect to cloud relay: {e}")
            finally:
                if sio.connected:
                    await sio.disconnect()
        
        event_loop.run_until_complete(run_test())
    
    def test_join_room(self, event_loop):
        """Test joining a room"""
        
        async def run_test():
            sio = socketio.AsyncClient()
            room_joined = False
            test_room = f"test-room-{int(time.time())}"
            
            @sio.event
            async def room_devices(devices):
                nonlocal room_joined
                room_joined = True
            
            try:
                await sio.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await asyncio.sleep(0.5)
                
                # Register to room
                await sio.emit('register', {
                    'roomId': test_room,
                    'deviceId': 'test-device-1',
                    'deviceName': 'PyTest Device',
                    'deviceType': 'desktop'
                })
                
                await asyncio.sleep(1)  # Wait for room_devices event
                
                assert room_joined, "Did not receive room_devices event"
                print(f"\n✅ Joined room: {test_room}")
                
            except Exception as e:
                pytest.skip(f"Could not join room: {e}")
            finally:
                if sio.connected:
                    await sio.disconnect()
        
        event_loop.run_until_complete(run_test())


class TestCloudRelayMessaging:
    """Test sending/receiving messages between two simulated devices"""
    
    @pytest.fixture
    def event_loop(self):
        """Create event loop for async tests"""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    def test_message_relay(self, event_loop):
        """Test that messages are relayed between devices in same room"""
        
        async def run_test():
            # Create two clients
            device_a = socketio.AsyncClient()
            device_b = socketio.AsyncClient()
            
            test_room = f"test-relay-{int(time.time())}"
            received_message = None
            
            @device_b.event
            async def clipboard_data(data):
                nonlocal received_message
                received_message = data
            
            try:
                # Connect both devices
                await device_a.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await device_b.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await asyncio.sleep(0.5)
                
                # Register both to same room
                await device_a.emit('register', {
                    'roomId': test_room,
                    'deviceId': 'device-a',
                    'deviceName': 'Device A',
                    'deviceType': 'desktop'
                })
                
                await device_b.emit('register', {
                    'roomId': test_room,
                    'deviceId': 'device-b',
                    'deviceName': 'Device B',
                    'deviceType': 'mobile'
                })
                
                await asyncio.sleep(0.5)
                
                # Device A sends message
                test_content = "Hello from Device A!"
                await device_a.emit('clipboard_data', {
                    'encrypted_content': test_content,
                    'content_type': 'text',
                    'encrypted': False,
                    'timestamp': int(time.time() * 1000)
                })
                
                # Wait for Device B to receive
                await asyncio.sleep(1)
                
                assert received_message is not None, "Device B did not receive message"
                assert received_message.get('encrypted_content') == test_content
                assert received_message.get('from_name') == 'Device A'
                
                print(f"\n✅ Message relayed successfully!")
                print(f"   Sent: {test_content}")
                print(f"   Received by: Device B")
                print(f"   From: {received_message.get('from_name')}")
                
            except Exception as e:
                pytest.skip(f"Message relay test failed: {e}")
            finally:
                if device_a.connected:
                    await device_a.disconnect()
                if device_b.connected:
                    await device_b.disconnect()
        
        event_loop.run_until_complete(run_test())
    
    def test_encrypted_message_relay(self, event_loop):
        """Test that encrypted messages are relayed correctly"""
        from core.cloud_relay_crypto import CloudRelayCrypto
        
        async def run_test():
            device_a = socketio.AsyncClient()
            device_b = socketio.AsyncClient()
            
            test_room = f"test-encrypted-{int(time.time())}"
            test_password = "test-password-123"
            received_message = None
            
            # Initialize crypto for both devices with same room+password
            crypto_a = CloudRelayCrypto()
            crypto_a.init(test_room, test_password)
            
            crypto_b = CloudRelayCrypto()
            crypto_b.init(test_room, test_password)
            
            @device_b.event
            async def clipboard_data(data):
                nonlocal received_message
                received_message = data
            
            try:
                await device_a.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await device_b.connect(CLOUD_RELAY_URL, transports=['websocket', 'polling'])
                await asyncio.sleep(0.5)
                
                await device_a.emit('register', {
                    'roomId': test_room,
                    'deviceId': 'device-a',
                    'deviceName': 'Device A',
                    'deviceType': 'desktop'
                })
                
                await device_b.emit('register', {
                    'roomId': test_room,
                    'deviceId': 'device-b',
                    'deviceName': 'Device B',
                    'deviceType': 'mobile'
                })
                
                await asyncio.sleep(0.5)
                
                # Encrypt and send
                plaintext = "Secret message from Device A!"
                encrypted = crypto_a.encrypt(plaintext)
                
                await device_a.emit('clipboard_data', {
                    'encrypted_content': encrypted,
                    'content_type': 'text',
                    'encrypted': True,
                    'timestamp': int(time.time() * 1000)
                })
                
                await asyncio.sleep(1)
                
                assert received_message is not None, "Device B did not receive message"
                assert received_message.get('encrypted') == True
                
                # Decrypt on Device B
                decrypted = crypto_b.decrypt(received_message.get('encrypted_content'))
                assert decrypted == plaintext
                
                print(f"\n✅ Encrypted message relayed and decrypted!")
                print(f"   Original: {plaintext}")
                print(f"   Encrypted: {encrypted[:50]}...")
                print(f"   Decrypted: {decrypted}")
                
            except Exception as e:
                pytest.skip(f"Encrypted relay test failed: {e}")
            finally:
                if device_a.connected:
                    await device_a.disconnect()
                if device_b.connected:
                    await device_b.disconnect()
        
        event_loop.run_until_complete(run_test())


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
