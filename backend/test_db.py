import asyncio
from database import users_collection

async def check_users():
    try:
        count = await users_collection.count_documents({})
        print(f"Users in database: {count}")
        
        # List all users
        async for user in users_collection.find({}, {"username": 1, "email": 1}):
            print(f"User: {user.get('username')} - {user.get('email')}")
            
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(check_users())