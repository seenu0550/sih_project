from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "timetable_scheduler")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
users_collection = database.get_collection("users")
classrooms_collection = database.get_collection("classrooms")
subjects_collection = database.get_collection("subjects")
faculty_collection = database.get_collection("faculty")
batches_collection = database.get_collection("batches")
timetables_collection = database.get_collection("timetables")