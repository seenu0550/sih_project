from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "timetable_scheduler")

# Connection with timeout and retry settings
client = AsyncIOMotorClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    maxPoolSize=10,
    minPoolSize=1
)

database = client[DATABASE_NAME]

# Collections
users_collection = database.get_collection("users")
classrooms_collection = database.get_collection("classrooms")
subjects_collection = database.get_collection("subjects")
faculty_collection = database.get_collection("faculty")
batches_collection = database.get_collection("batches")
timetables_collection = database.get_collection("timetables")

async def check_database_connection():
    """Check if database connection is working."""
    try:
        await client.admin.command('ping')
        logger.info("Database connection successful")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Database connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        return False

async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Drop existing problematic indexes first
        try:
            await subjects_collection.drop_index("code_1")
            logger.info("Dropped old subject code index")
        except Exception:
            pass  # Index might not exist
        
        # Create unique indexes
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("email", unique=True)
        
        # Create compound indexes for user data with proper uniqueness
        await classrooms_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
        await subjects_collection.create_index([("user_id", 1), ("code", 1)], unique=True)
        await faculty_collection.create_index([("user_id", 1), ("email", 1)], unique=True)
        await batches_collection.create_index([("user_id", 1), ("name", 1)], unique=True)
        await timetables_collection.create_index([("user_id", 1), ("name", 1)])
        
        # Ensure data persistence
        await users_collection.create_index("created_at")
        await timetables_collection.create_index("created_at")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")