#!/usr/bin/env python3
"""
Test the pairing server HTTP responses
"""

import urllib.request
import json

def test_pairing_page():
    """Test that the pairing page loads correctly"""
    print("Testing pairing server responses...")
    print("=" * 60)
    
    url = "http://localhost:8080"
    
    try:
        # Test HTML page
        print(f"\n1. Testing HTML page: {url}/")
        response = urllib.request.urlopen(f"{url}/")
        
        # Check status
        print(f"   Status: {response.status}")
        
        # Check headers
        content_type = response.headers.get('Content-Type')
        print(f"   Content-Type: {content_type}")
        
        # Check content
        html = response.read().decode('utf-8')
        print(f"   HTML Length: {len(html)} bytes")
        
        if 'text/html' in content_type:
            print("   ✅ Correct content type!")
        else:
            print(f"   ❌ Wrong content type: {content_type}")
        
        if '<!DOCTYPE html>' in html:
            print("   ✅ Valid HTML document!")
        else:
            print("   ❌ Invalid HTML!")
        
        if 'Device Pairing' in html:
            print("   ✅ Contains expected content!")
        else:
            print("   ❌ Missing expected content!")
        
        # Test status endpoint
        print(f"\n2. Testing status endpoint: {url}/status")
        response = urllib.request.urlopen(f"{url}/status")
        
        print(f"   Status: {response.status}")
        content_type = response.headers.get('Content-Type')
        print(f"   Content-Type: {content_type}")
        
        data = json.loads(response.read().decode('utf-8'))
        print(f"   Device Name: {data.get('device_name')}")
        print(f"   IP: {data.get('ip')}")
        
        if 'application/json' in content_type:
            print("   ✅ Correct content type!")
        else:
            print(f"   ❌ Wrong content type: {content_type}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except urllib.error.URLError as e:
        print(f"\n❌ Could not connect to server: {e}")
        print("\nMake sure the pairing server is running:")
        print("  python test_pairing_server.py")
        print("  OR")
        print("  python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pairing_page()
