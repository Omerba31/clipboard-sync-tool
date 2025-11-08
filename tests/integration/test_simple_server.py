#!/usr/bin/env python3
"""
Absolute simplest HTTP server to test iOS Chrome compatibility
"""

from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def do_GET(self):
        print(f"\n=== REQUEST from {self.client_address[0]} ===")
        print(f"Path: {self.path}")
        print(f"Headers: {self.headers}")
        
        if self.path == '/test':
            content = b'Hello from simple server!'
            print(f"Sending {len(content)} bytes...")
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Connection', 'close')
            self.end_headers()
            
            self.wfile.write(content)
            print("Response sent!")
            
        elif self.path == '/':
            html = b'<html><body><h1>It Works!</h1><p>Server is responding correctly.</p></body></html>'
            print(f"Sending HTML {len(html)} bytes...")
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(html)))
            self.send_header('Connection', 'close')
            self.end_headers()
            
            self.wfile.write(html)
            print("HTML sent!")
        else:
            self.send_error(404)

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8888), SimpleHandler)
    print("Simple test server running on port 8888")
    print("Try accessing from your phone:")
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"  http://{local_ip}:8888/")
    print(f"  http://{local_ip}:8888/test")
    print("\nWatching for requests...\n")
    server.serve_forever()
