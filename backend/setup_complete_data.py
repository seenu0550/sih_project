import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    users_collection, classrooms_collection, subjects_collection,
    faculty_collection, batches_collection
)
from auth import get_password_hash

async def setup_complete_data():
    """Setup complete sample data for the timetable system"""
    
    try:
        # Clear existing data
        await users_collection.delete_many({})
        await classrooms_collection.delete_many({})
        await subjects_collection.delete_many({})
        await faculty_collection.delete_many({})
        await batches_collection.delete_many({})
        
        # Create admin user
        admin_user = {
            "username": "admin",
            "email": "admin@college.edu",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "is_active": True
        }
        await users_collection.insert_one(admin_user)
        
        # Create classrooms
        classrooms = [
            {"name": "Room 101", "capacity": 60, "type": "lecture", "equipment": ["projector", "whiteboard"]},
            {"name": "Room 102", "capacity": 50, "type": "lecture", "equipment": ["projector", "whiteboard"]},
            {"name": "Lab 201", "capacity": 30, "type": "lab", "equipment": ["computers", "projector"]},
            {"name": "Lab 202", "capacity": 25, "type": "lab", "equipment": ["computers", "projector"]},
            {"name": "Seminar Hall", "capacity": 100, "type": "seminar", "equipment": ["projector", "sound_system"]},
        ]
        await classrooms_collection.insert_many(classrooms)
        
        # Create subjects
        subjects = [
            {"name": "Data Structures", "code": "CS201", "credits": 4, "type": "theory", "classes_per_week": 4, "duration": 60},
            {"name": "Database Systems", "code": "CS202", "credits": 4, "type": "theory", "classes_per_week": 4, "duration": 60},
            {"name": "Web Development", "code": "CS203", "credits": 3, "type": "theory", "classes_per_week": 3, "duration": 60},
            {"name": "DS Lab", "code": "CS201L", "credits": 2, "type": "practical", "classes_per_week": 2, "duration": 120},
            {"name": "DB Lab", "code": "CS202L", "credits": 2, "type": "practical", "classes_per_week": 2, "duration": 120},
            {"name": "Web Dev Lab", "code": "CS203L", "credits": 2, "type": "practical", "classes_per_week": 2, "duration": 180},
            {"name": "Mathematics", "code": "MA201", "credits": 4, "type": "theory", "classes_per_week": 4, "duration": 60},
            {"name": "Physics", "code": "PH201", "credits": 3, "type": "theory", "classes_per_week": 3, "duration": 60},
        ]
        await subjects_collection.insert_many(subjects)
        
        # Create faculty with expanded subject coverage
        faculty = [
            {"name": "Dr. Smith", "email": "smith@college.edu", "subjects": ["CS201", "CS201L", "CS202"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
            {"name": "Prof. Johnson", "email": "johnson@college.edu", "subjects": ["CS202", "CS202L", "CS203"], "max_hours_per_day": 6, "avg_leaves_per_month": 1},
            {"name": "Dr. Williams", "email": "williams@college.edu", "subjects": ["CS203", "CS203L", "CS201"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
            {"name": "Prof. Brown", "email": "brown@college.edu", "subjects": ["MA201", "CS201"], "max_hours_per_day": 6, "avg_leaves_per_month": 1},
            {"name": "Dr. Davis", "email": "davis@college.edu", "subjects": ["PH201", "CS202"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
            {"name": "Prof. Anderson", "email": "anderson@college.edu", "subjects": ["CS201", "CS202", "CS203"], "max_hours_per_day": 6, "avg_leaves_per_month": 1},
            {"name": "Dr. Taylor", "email": "taylor@college.edu", "subjects": ["CS201L", "CS202L", "CS203L"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
        ]
        await faculty_collection.insert_many(faculty)
        
        # Create batches
        batches = [
            {
                "name": "CS-2A", 
                "semester": 3, 
                "department": "Computer Science", 
                "student_count": 45,
                "subjects": ["CS201", "CS201L", "CS202", "CS202L", "MA201"]
            },
            {
                "name": "CS-2B", 
                "semester": 3, 
                "department": "Computer Science", 
                "student_count": 40,
                "subjects": ["CS201", "CS201L", "CS203", "CS203L", "PH201"]
            },
            {
                "name": "CS-4A", 
                "semester": 7, 
                "department": "Computer Science", 
                "student_count": 35,
                "subjects": ["CS203", "CS203L", "CS202", "CS202L"]
            }
        ]
        await batches_collection.insert_many(batches)
        
        print("Complete sample data setup successful!")
        print("Admin login: admin / admin123")
        print("Created 5 classrooms, 8 subjects, 7 faculty, 3 batches")
        
    except Exception as e:
        print(f"Error setting up data: {e}")

if __name__ == "__main__":
    asyncio.run(setup_complete_data())