# tests/integration/test_simple_server.py
"""
Integration tests for simple HTTP server functionality.
"""

import pytest
import sys
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class SimpleTestHandler(BaseHTTPRequestHandler):
    """Simple test HTTP handler"""
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        pass  # Suppress logging


@pytest.fixture
def simple_server():
    """Create a simple test HTTP server"""
    server = HTTPServer(('127.0.0.1', 0), SimpleTestHandler)  # port=0 for random
    port = server.server_address[1]
    
    # Run in background thread
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()
    
    yield f"http://127.0.0.1:{port}"
    
    server.server_close()


class TestHTTPServer:
    """Test HTTP server basics"""
    
    def test_http_server_creation(self):
        """Test creating an HTTP server"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        server = HTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler)
        port = server.server_address[1]
        
        assert port > 0
        assert port < 65536
        
        server.server_close()
    
    def test_server_thread_start(self):
        """Test server runs in a thread"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        
        server = HTTPServer(('127.0.0.1', 0), BaseHTTPRequestHandler)
        
        thread = threading.Thread(target=lambda: None)
        thread.daemon = True
        
        assert thread.daemon == True
        
        server.server_close()


class TestHTTPClients:
    """Test HTTP client functionality"""
    
    def test_urllib_request(self, simple_server):
        """Test making HTTP request with urllib"""
        import urllib.request
        
        response = urllib.request.urlopen(simple_server, timeout=5)
        
        assert response.status == 200
        content = response.read()
        assert content == b'OK'
    
    def test_request_headers(self, simple_server):
        """Test request with custom headers"""
        import urllib.request
        
        req = urllib.request.Request(
            simple_server,
            headers={'User-Agent': 'Test Client'}
        )
        response = urllib.request.urlopen(req, timeout=5)
        
        assert response.status == 200


class TestThreading:
    """Test threading for server operations"""
    
    def test_thread_creation(self):
        """Test creating threads"""
        import threading
        
        results = []
        
        def worker():
            results.append(True)
        
        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=1)
        
        assert len(results) == 1
        assert results[0] == True
    
    def test_daemon_thread(self):
        """Test daemon threads"""
        import threading
        
        def worker():
            pass
        
        thread = threading.Thread(target=worker)
        thread.daemon = True
        
        assert thread.daemon == True
    
    def test_lock(self):
        """Test thread locks"""
        import threading
        
        lock = threading.Lock()
        counter = [0]
        
        def increment():
            with lock:
                counter[0] += 1
        
        threads = [threading.Thread(target=increment) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=1)
        
        assert counter[0] == 10
