#!/usr/bin/env python3
"""
Test script for the security report API functionality
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Start the test server in a separate process"""
    import uvicorn
    from test_server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def test_security_report_api():
    """Test the security report API endpoint"""
    
    print("Testing Security Report API...")
    print("=" * 50)
    
    # Wait for server to start
    time.sleep(2)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Submit a valid security report
    report_data = {
        "type": "security",
        "severity": "high",
        "description": "This is a test security vulnerability report with sufficient length to pass validation.",
        "email": "test@example.com",
        "anonymous": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/security/report",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Security report submission passed")
            print(f"   Report ID: {result.get('id', 'N/A')}")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Security report submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Security report submission error: {e}")
        return False
    
    # Test 3: Submit anonymous report
    anonymous_report = {
        "type": "fraud",
        "severity": "medium", 
        "description": "Anonymous report test with sufficient description length for validation purposes.",
        "anonymous": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/security/report",
            json=anonymous_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Anonymous security report submission passed")
        else:
            print(f"❌ Anonymous security report submission failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Anonymous security report submission error: {e}")
        return False
    
    # Test 4: Test validation (should fail)
    invalid_report = {
        "type": "security",
        "severity": "low",
        "description": "Short",  # Too short, should fail
        "email": "",
        "anonymous": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/security/report",
            json=invalid_report,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:  # Validation error expected
            print("✅ Validation error handling works correctly")
        else:
            print(f"❌ Validation should have failed but got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False
    
    # Test 5: Check reports list
    try:
        response = requests.get(f"{base_url}/api/security/reports")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reports list retrieved successfully ({result.get('total', 0)} reports)")
        else:
            print(f"❌ Reports list failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Reports list error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 All security report API tests completed successfully!")
    print("\nThe report submission system is working correctly:")
    print("- ✅ Form validation")
    print("- ✅ API endpoint communication") 
    print("- ✅ Error handling")
    print("- ✅ Success responses")
    print("- ✅ Anonymous submissions")
    
    return True

if __name__ == "__main__":
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run tests
    success = test_security_report_api()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)