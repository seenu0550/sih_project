import asyncio
import requests
import json

async def test_auth_flow():
    base_url = "http://localhost:8000"
    
    # Test registration
    print("🔧 Testing Registration...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "admin"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        print(f"Registration Status: {response.status_code}")
        print(f"Registration Response: {response.json()}")
    except Exception as e:
        print(f"Registration Error: {e}")
    
    # Test login
    print("\n🔐 Testing Login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Login successful! Token: {token[:20]}...")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"Login Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())