import asyncio
from database import users_collection
from auth import get_password_hash

async def test_connection():
    try:
        # Test database connection
        result = await users_collection.find_one({})
        print("✅ Database connection successful!")
        
        # Create test user if none exists
        existing_user = await users_collection.find_one({"username": "admin"})
        if not existing_user:
            admin_user = {
                "username": "admin",
                "email": "admin@college.edu",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "is_active": True
            }
            await users_collection.insert_one(admin_user)
            print("✅ Admin user created: admin/admin123")
        else:
            print("✅ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure MongoDB is running on localhost:27017")

if __name__ == "__main__":
    asyncio.run(test_connection())