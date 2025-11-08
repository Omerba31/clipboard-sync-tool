# gui/pairing_server.py
"""
Simple HTTP server for mobile device pairing.
Mobile devices scan QR code to open pairing page.
"""

import json
import socket
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urllib.parse import parse_qs, urlparse
from typing import Callable, Optional
import qrcode
import io
import base64

class PairingHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for pairing requests"""
    
    # Use HTTP/1.1 protocol
    protocol_version = 'HTTP/1.1'
    
    # Disable buffering for immediate write
    wbufsize = 0
    
    sync_engine = None
    on_pair_callback: Optional[Callable] = None
    
    def log_message(self, format, *args):
        """Log HTTP requests"""
        import sys
        msg = f"[HTTP] {format % args}"
        print(msg, flush=True)
        sys.stdout.flush()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Log the request with full details
        import sys
        user_agent = self.headers.get('User-Agent', 'Unknown')
        print(f"\n{'='*60}", flush=True)
        print(f"[HTTP] GET request:", flush=True)
        print(f"  Path: {path}", flush=True)
        print(f"  From: {self.client_address[0]}", flush=True)
        print(f"  User-Agent: {user_agent}", flush=True)
        print(f"  Accept: {self.headers.get('Accept', 'Not specified')}", flush=True)
        print(f"{'='*60}\n", flush=True)
        sys.stdout.flush()
        
        if path == '/' or path == '/index.html':
            self.serve_pairing_page()
        elif path == '/pair':
            self.handle_pair_request()
        elif path == '/status':
            self.serve_status()
        elif path == '/test':
            # Simple test endpoint
            content = b'Server is working!'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(content)
            self.wfile.flush()
            print(f"[HTTP] Test endpoint accessed - sent {len(content)} bytes", flush=True)
        else:
            print(f"[HTTP] 404 Not Found: {path}", flush=True)
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        print(f"\n[HTTP] POST request to: {self.path}")
        if self.path == '/pair':
            self.handle_pair_post()
        else:
            print(f"[HTTP] 404 Not Found: {self.path}")
            self.send_error(404)
    
    def do_HEAD(self):
        """Handle HEAD requests (some browsers do this first)"""
        print(f"\n[HTTP] HEAD request to: {self.path}", flush=True)
        if self.path == '/' or self.path == '/index.html':
            # Calculate content length
            html = """<!DOCTYPE html>..."""  # Would be the same HTML
            html_bytes = html.encode('utf-8')
            
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', '8211')  # Approximate
            self.send_header('Connection', 'close')
            self.send_header('Content-Disposition', 'inline')
            self.end_headers()
        else:
            self.send_error(404)
    
    def serve_pairing_page(self):
        """Serve the HTML pairing page"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clipboard Sync - Pairing</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: white;
        }
        .container {
            background: white;
            color: #333;
            border-radius: 20px;
            padding: 40px 30px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideUp 0.5s ease;
        }
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
            color: #667eea;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .device-info {
            background: #f5f7fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .info-row:last-child {
            border-bottom: none;
        }
        .info-label {
            font-weight: 600;
            color: #666;
        }
        .info-value {
            color: #333;
            font-family: monospace;
            font-size: 13px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:active {
            transform: scale(0.98);
        }
        .btn:hover {
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            display: none;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 20px;
            text-align: center;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 10px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📱💻</div>
        <h1>Device Pairing</h1>
        <p class="subtitle">Pair this device with Clipboard Sync</p>
        
        <div class="device-info">
            <div class="info-row">
                <span class="info-label">Device Name:</span>
                <span class="info-value" id="device-name">Loading...</span>
            </div>
            <div class="info-row">
                <span class="info-label">IP Address:</span>
                <span class="info-value" id="device-ip">Loading...</span>
            </div>
            <div class="info-row">
                <span class="info-label">Status:</span>
                <span class="info-value">🟢 Ready to Pair</span>
            </div>
        </div>
        
        <form id="pairForm">
            <div class="form-group">
                <label for="mobileName">Your Device Name</label>
                <input type="text" id="mobileName" name="mobileName" 
                       placeholder="e.g., My iPhone" required>
            </div>
            
            <button type="submit" class="btn">
                🔗 Pair Devices
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
        </div>
        
        <div class="status" id="status"></div>
    </div>
    
    <script>
        // Load device info
        fetch('/status')
            .then(r => r.json())
            .then(data => {
                document.getElementById('device-name').textContent = data.device_name;
                document.getElementById('device-ip').textContent = data.ip;
            });
        
        // Handle form submission
        document.getElementById('pairForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const mobileName = document.getElementById('mobileName').value;
            const statusDiv = document.getElementById('status');
            const loadingDiv = document.getElementById('loading');
            const form = document.getElementById('pairForm');
            
            // Show loading
            form.style.display = 'none';
            loadingDiv.style.display = 'block';
            statusDiv.style.display = 'none';
            
            try {
                const response = await fetch('/pair', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `mobile_name=${encodeURIComponent(mobileName)}`
                });
                
                const result = await response.json();
                
                loadingDiv.style.display = 'none';
                statusDiv.style.display = 'block';
                
                if (result.success) {
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = '✅ Pairing Successful!<br><small>You can now close this page</small>';
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Pairing Failed<br><small>' + result.message + '</small>';
                    form.style.display = 'block';
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                statusDiv.style.display = 'block';
                statusDiv.className = 'status error';
                statusDiv.innerHTML = '❌ Connection Error<br><small>Please try again</small>';
                form.style.display = 'block';
            }
        });
    </script>
</body>
</html>
        """
        
        # Encode HTML
        html_bytes = html.encode('utf-8')
        
        import sys
        print(f"[HTTP] Serving HTML page, size: {len(html_bytes)} bytes", flush=True)
        sys.stdout.flush()
        
        # Send response with proper headers for iOS Safari/Chrome
        self.send_response(200, 'OK')
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html_bytes)))
        self.send_header('Connection', 'close')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        # Explicitly tell iOS this is NOT a download
        self.send_header('Content-Disposition', 'inline')
        self.end_headers()
        
        print(f"[HTTP] Headers sent, writing {len(html_bytes)} bytes to response...", flush=True)
        
        # Write in chunks to ensure it's sent
        chunk_size = 4096
        for i in range(0, len(html_bytes), chunk_size):
            chunk = html_bytes[i:i+chunk_size]
            self.wfile.write(chunk)
        
        self.wfile.flush()
        print(f"[HTTP] HTML page sent successfully! Total: {len(html_bytes)} bytes", flush=True)
        sys.stdout.flush()
    
    def serve_status(self):
        """Return device status as JSON"""
        if self.sync_engine:
            data = {
                'device_name': self.sync_engine.device_name,
                'device_id': self.sync_engine.device_id,
                'ip': self.sync_engine.discovery.local_ip,
                'port': self.sync_engine.discovery.port
            }
        else:
            data = {
                'device_name': 'Unknown',
                'device_id': 'N/A',
                'ip': 'N/A',
                'port': 'N/A'
            }
        
        json_data = json.dumps(data).encode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(json_data)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_data)
    
    def handle_pair_post(self):
        """Handle pairing POST request"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            mobile_name = params.get('mobile_name', ['Unknown Device'])[0]
            
            if self.sync_engine:
                # Create a device entry for the mobile device
                from core.network import Device, DeviceStatus
                from datetime import datetime
                
                # Get mobile IP
                mobile_ip = self.client_address[0]
                
                mobile_device = Device(
                    device_id=f"mobile-{mobile_ip.replace('.', '-')}",
                    name=mobile_name,
                    ip_address=mobile_ip,
                    port=8888,  # Default port
                    status=DeviceStatus.PAIRING,
                    last_seen=datetime.now()
                )
                
                # Pair the device
                self.sync_engine._pair_with_device(mobile_device)
                
                # Call callback if set
                if self.on_pair_callback:
                    self.on_pair_callback(mobile_device)
                
                response = {'success': True, 'message': 'Device paired successfully'}
            else:
                response = {'success': False, 'message': 'Sync engine not available'}
            
            json_response = json.dumps(response).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_response)
            
        except Exception as e:
            response = {'success': False, 'message': str(e)}
            json_response = json.dumps(response).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(json_response)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_response)


class PairingServer:
    """HTTP server for mobile device pairing"""
    
    def __init__(self, sync_engine, port: int = 8080):
        self.sync_engine = sync_engine
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False
        
        # Set sync engine for handler
        PairingHTTPHandler.sync_engine = sync_engine
    
    def start(self, on_pair_callback: Optional[Callable] = None):
        """Start the pairing server"""
        if self.is_running:
            return
        
        PairingHTTPHandler.on_pair_callback = on_pair_callback
        
        try:
            # Use ThreadingHTTPServer for better connection handling
            self.server = ThreadingHTTPServer(('0.0.0.0', self.port), PairingHTTPHandler)
            self.server.timeout = 30  # 30 second timeout for requests
            self.is_running = True
            
            self.thread = Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            print(f"Pairing server started on port {self.port}")
        except Exception as e:
            print(f"Failed to start pairing server: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the pairing server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            print("Pairing server stopped")
    
    def get_pairing_url(self) -> str:
        """Get the pairing URL for QR code"""
        if self.sync_engine:
            local_ip = self.sync_engine.discovery.local_ip
            return f"http://{local_ip}:{self.port}"
        return f"http://localhost:{self.port}"
