import asyncio
from database import users_collection
from auth import get_password_hash

async def setup_admin():
    # Delete existing admin if exists
    await users_collection.delete_one({"username": "admin"})
    
    # Create new admin with known password
    hashed_password = get_password_hash("admin123")
    user_dict = {
        "username": "admin",
        "email": "admin@college.edu",
        "hashed_password": hashed_password,
        "role": "admin",
        "is_active": True
    }
    
    await users_collection.insert_one(user_dict)
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(setup_admin())