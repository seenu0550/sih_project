import asyncio
import requests
from database import users_collection
from auth import verify_password

async def test_login():
    # Check user in database
    user = await users_collection.find_one({"username": "admin"})
    if user:
        print(f"User found: {user['username']}")
        print(f"Password verification: {verify_password('admin123', user['hashed_password'])}")
    else:
        print("User not found")
    
    # Test API endpoint
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        print(f"API Response: {response.status_code}")
        print(f"Response body: {response.text}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_login())