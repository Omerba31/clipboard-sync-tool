# tests/integration/test_http_response.py
"""
Integration tests for HTTP connectivity and responses.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestHTTPConnectivity:
    """Test HTTP connectivity helpers"""
    
    def test_urllib_available(self):
        """Test urllib is available for HTTP requests"""
        import urllib.request
        import urllib.error
        
        assert urllib.request is not None
        assert urllib.error is not None
    
    def test_socket_available(self):
        """Test socket module is available"""
        import socket
        
        assert socket is not None
        assert hasattr(socket, 'socket')
        assert hasattr(socket, 'gethostname')
    
    def test_localhost_resolution(self):
        """Test localhost can be resolved"""
        import socket
        
        try:
            result = socket.gethostbyname('localhost')
            assert result == '127.0.0.1'
        except socket.gaierror:
            pytest.skip("Cannot resolve localhost")


class TestURLParsing:
    """Test URL parsing functionality"""
    
    def test_parse_http_url(self):
        """Test parsing HTTP URLs"""
        from urllib.parse import urlparse
        
        url = "http://192.168.1.100:8080/api/pair"
        parsed = urlparse(url)
        
        assert parsed.scheme == "http"
        assert parsed.hostname == "192.168.1.100"
        assert parsed.port == 8080
        assert parsed.path == "/api/pair"
    
    def test_parse_cloud_relay_url(self):
        """Test parsing cloud relay URL"""
        from urllib.parse import urlparse
        
        url = "https://clipboard-sync.railway.app"
        parsed = urlparse(url)
        
        assert parsed.scheme == "https"
        assert "railway.app" in parsed.hostname
    
    def test_url_building(self):
        """Test building URLs"""
        from urllib.parse import urljoin
        
        base = "http://localhost:8080"
        endpoint = "/api/pair"
        
        full_url = urljoin(base + "/", endpoint.lstrip('/'))
        assert "localhost:8080" in full_url
        assert "api/pair" in full_url


class TestJSONHandling:
    """Test JSON handling for API responses"""
    
    def test_json_encode(self):
        """Test JSON encoding"""
        import json
        
        data = {
            "device_id": "test-123",
            "device_name": "My Device",
            "ip": "192.168.1.100"
        }
        
        encoded = json.dumps(data)
        assert isinstance(encoded, str)
        assert "test-123" in encoded
    
    def test_json_decode(self):
        """Test JSON decoding"""
        import json
        
        json_str = '{"status": "ok", "paired": true}'
        data = json.loads(json_str)
        
        assert data["status"] == "ok"
        assert data["paired"] == True
    
    def test_json_roundtrip(self):
        """Test JSON encode/decode roundtrip"""
        import json
        
        original = {
            "content": "Hello World",
            "timestamp": 1234567890,
            "encrypted": False
        }
        
        encoded = json.dumps(original)
        decoded = json.loads(encoded)
        
        assert decoded == original


class TestNetworkHelpers:
    """Test network helper functions"""
    
    def test_get_local_ip(self):
        """Test getting local IP address"""
        import socket
        
        try:
            # This is the method used in the app
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            assert local_ip is not None
            assert len(local_ip.split('.')) == 4  # IPv4 format
        except OSError:
            pytest.skip("No network connection available")
    
    def test_hostname(self):
        """Test getting hostname"""
        import socket
        
        hostname = socket.gethostname()
        assert hostname is not None
        assert len(hostname) > 0
