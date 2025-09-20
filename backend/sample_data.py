#!/usr/bin/env python3
"""
Sample data insertion script for Smart Classroom & Timetable Scheduler
"""

import asyncio
from database import (
    classrooms_collection, subjects_collection, 
    faculty_collection, batches_collection, users_collection
)
from auth import get_password_hash

async def insert_sample_data():
    print("Inserting sample data...")
    
    # Clear existing data
    await users_collection.delete_many({})
    await classrooms_collection.delete_many({})
    await subjects_collection.delete_many({})
    await faculty_collection.delete_many({})
    await batches_collection.delete_many({})
    
    # Sample Users
    users = [
        {
            "username": "admin",
            "email": "admin@college.edu",
            "hashed_password": get_password_hash("admin123"),
            "role": "admin",
            "is_active": True
        }
    ]
    
    # Sample Classrooms
    classrooms = [
        {"name": "Room 101", "capacity": 60, "type": "lecture", "equipment": ["Projector", "Whiteboard", "AC"]},
        {"name": "Room 102", "capacity": 40, "type": "seminar", "equipment": ["Projector", "Whiteboard"]},
        {"name": "Room 103", "capacity": 50, "type": "lecture", "equipment": ["Projector", "Whiteboard", "AC"]},
        {"name": "Lab 201", "capacity": 30, "type": "lab", "equipment": ["Computers", "Projector", "AC"]},
        {"name": "Lab 202", "capacity": 25, "type": "lab", "equipment": ["Computers", "Whiteboard"]},
        {"name": "Lab 203", "capacity": 35, "type": "lab", "equipment": ["Computers", "Projector", "AC"]},
        {"name": "Hall A", "capacity": 100, "type": "lecture", "equipment": ["Projector", "Sound System", "AC"]},
        {"name": "Hall B", "capacity": 80, "type": "lecture", "equipment": ["Projector", "Sound System", "AC"]},
    ]
    
    # Sample Subjects
    subjects = [
        {"name": "Data Structures", "code": "CS201", "credits": 4, "type": "theory", "classes_per_week": 3, "duration": 60},
        {"name": "Database Systems", "code": "CS202", "credits": 4, "type": "theory", "classes_per_week": 3, "duration": 60},
        {"name": "Web Development", "code": "CS203", "credits": 3, "type": "practical", "classes_per_week": 2, "duration": 90},
        {"name": "Machine Learning", "code": "CS301", "credits": 4, "type": "theory", "classes_per_week": 3, "duration": 60},
        {"name": "Software Engineering", "code": "CS302", "credits": 3, "type": "theory", "classes_per_week": 2, "duration": 60},
        {"name": "Computer Networks", "code": "CS303", "credits": 4, "type": "theory", "classes_per_week": 3, "duration": 60},
    ]
    
    # Sample Faculty
    faculty = [
        {"name": "Dr. John Smith", "email": "john@college.edu", "subjects": ["CS201", "CS202"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
        {"name": "Prof. Sarah Johnson", "email": "sarah@college.edu", "subjects": ["CS203", "CS301"], "max_hours_per_day": 5, "avg_leaves_per_month": 1},
        {"name": "Dr. Michael Brown", "email": "michael@college.edu", "subjects": ["CS302", "CS303"], "max_hours_per_day": 6, "avg_leaves_per_month": 2},
        {"name": "Prof. Emily Davis", "email": "emily@college.edu", "subjects": ["CS201", "CS301"], "max_hours_per_day": 5, "avg_leaves_per_month": 1},
    ]
    
    # Sample Batches
    batches = [
        {"name": "CS-2A", "semester": 4, "department": "Computer Science", "student_count": 45, "subjects": ["CS201", "CS202", "CS203"]},
        {"name": "CS-2B", "semester": 4, "department": "Computer Science", "student_count": 40, "subjects": ["CS201", "CS202", "CS203"]},
        {"name": "CS-3A", "semester": 6, "department": "Computer Science", "student_count": 35, "subjects": ["CS301", "CS302", "CS303"]},
        {"name": "IT-2A", "semester": 4, "department": "Information Technology", "student_count": 42, "subjects": ["CS201", "CS202", "CS203"]},
        {"name": "ECE-3A", "semester": 6, "department": "Electronics", "student_count": 38, "subjects": ["CS301", "CS302"]},
        {"name": "CS-1A", "semester": 2, "department": "Computer Science", "student_count": 50, "subjects": ["CS201", "CS202"]},
    ]
    
    # Insert data
    try:
        await users_collection.insert_many(users)
        print("Users inserted")
        
        await classrooms_collection.insert_many(classrooms)
        print("Classrooms inserted")
        
        await subjects_collection.insert_many(subjects)
        print("Subjects inserted")
        
        await faculty_collection.insert_many(faculty)
        print("Faculty inserted")
        
        await batches_collection.insert_many(batches)
        print("Batches inserted")
        
        print("\nSample data inserted successfully!")
        print("\nDefault login credentials:")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as e:
        print(f"Error inserting data: {e}")

if __name__ == "__main__":
    asyncio.run(insert_sample_data())