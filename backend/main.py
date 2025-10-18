from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
from typing import List
import asyncio
import os
import uuid
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import (
    users_collection, classrooms_collection, subjects_collection,
    faculty_collection, batches_collection, timetables_collection
)
from models import (
    User, UserCreate, UserLogin, Classroom, Subject, Faculty, Batch,
    Timetable, TimetableRequest, TimetableSlot
)
from auth import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    email: str
from scheduler import TimetableScheduler

app = FastAPI(title="Smart Classroom & Timetable Scheduler", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
scheduler = TimetableScheduler()

# Helper function to check if user is admin
async def verify_admin(current_user: str = Depends(verify_token)):
    user_info = await users_collection.find_one({"username": current_user})
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Create uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Database connection startup
@app.on_event("startup")
async def startup_event():
    try:
        # Test database connection
        await users_collection.find_one({"_id": "test"})
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

# Auth endpoints
@app.post("/auth/register")
async def register(user: UserCreate):
    try:
        logger.info(f"Registration attempt for user: {user.username}")
        
        # Test database connection
        try:
            await users_collection.find_one({"_id": "test"})
            logger.info("Database connection successful")
        except Exception as db_error:
            logger.error(f"Database connection failed: {db_error}")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        existing_email = await users_collection.find_one({"email": user.email})
        if existing_email:
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        user_dict = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "role": user.role,
            "is_active": True
        }
        
        logger.info(f"Inserting user into database: {user.username}")
        result = await users_collection.insert_one(user_dict)
        logger.info(f"User registered successfully: {user.username}, ID: {result.inserted_id}")
        return {"message": "User created successfully", "user_id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
async def login(user: UserLogin):
    try:
        # Ensure database connection with retry
        for attempt in range(3):
            try:
                db_user = await users_collection.find_one({"username": user.username})
                break
            except Exception as e:
                if attempt == 2:
                    raise HTTPException(status_code=500, detail="Database connection failed")
                await asyncio.sleep(0.5)
        
        if not db_user or not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# Classroom endpoints
@app.post("/classrooms/", response_model=dict)
async def create_classroom(classroom: Classroom, current_user: str = Depends(verify_admin)):
    classroom_dict = classroom.dict(by_alias=True, exclude={"id"})
    classroom_dict["user_id"] = current_user
    result = await classrooms_collection.insert_one(classroom_dict)
    return {"message": "Classroom created", "id": str(result.inserted_id)}

@app.get("/classrooms/", response_model=List[dict])
async def get_classrooms(current_user: str = Depends(verify_admin)):
    classrooms = []
    async for classroom in classrooms_collection.find({"user_id": current_user}):
        classroom["_id"] = str(classroom["_id"])
        classrooms.append(classroom)
    return classrooms

@app.delete("/classrooms/{classroom_id}")
async def delete_classroom(classroom_id: str, current_user: str = Depends(verify_admin)):
    from bson import ObjectId
    result = await classrooms_collection.delete_one({"_id": ObjectId(classroom_id), "user_id": current_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return {"message": "Classroom deleted"}

# Subject endpoints
@app.post("/subjects/", response_model=dict)
async def create_subject(subject: Subject, current_user: str = Depends(verify_admin)):
    subject_dict = subject.dict(by_alias=True, exclude={"id"})
    subject_dict["user_id"] = current_user
    result = await subjects_collection.insert_one(subject_dict)
    return {"message": "Subject created", "id": str(result.inserted_id)}

@app.get("/subjects/", response_model=List[dict])
async def get_subjects(current_user: str = Depends(verify_token)):
    # Get user info to determine role
    user_info = await users_collection.find_one({"username": current_user})
    
    subjects = []
    if user_info and user_info.get("role") == "admin":
        # Admins see their own subjects
        async for subject in subjects_collection.find({"user_id": current_user}):
            subject["_id"] = str(subject["_id"])
            subjects.append(subject)
    else:
        # Students see all subjects
        async for subject in subjects_collection.find({}):
            subject["_id"] = str(subject["_id"])
            subjects.append(subject)
    
    return subjects

@app.delete("/subjects/{subject_id}")
async def delete_subject(subject_id: str, current_user: str = Depends(verify_admin)):
    from bson import ObjectId
    result = await subjects_collection.delete_one({"_id": ObjectId(subject_id), "user_id": current_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Subject deleted"}

# Faculty endpoints
@app.post("/faculty/", response_model=dict)
async def create_faculty(faculty: Faculty, current_user: str = Depends(verify_admin)):
    faculty_dict = faculty.dict(by_alias=True, exclude={"id"})
    faculty_dict["user_id"] = current_user
    result = await faculty_collection.insert_one(faculty_dict)
    return {"message": "Faculty created", "id": str(result.inserted_id)}

@app.get("/faculty/", response_model=List[dict])
async def get_faculty(current_user: str = Depends(verify_admin)):
    faculty_list = []
    async for faculty in faculty_collection.find({"user_id": current_user}):
        faculty["_id"] = str(faculty["_id"])
        faculty_list.append(faculty)
    return faculty_list

@app.delete("/faculty/{faculty_id}")
async def delete_faculty(faculty_id: str, current_user: str = Depends(verify_admin)):
    from bson import ObjectId
    result = await faculty_collection.delete_one({"_id": ObjectId(faculty_id), "user_id": current_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"message": "Faculty deleted"}

# Batch endpoints
@app.post("/batches/", response_model=dict)
async def create_batch(batch: Batch, current_user: str = Depends(verify_admin)):
    batch_dict = batch.dict(by_alias=True, exclude={"id"})
    batch_dict["user_id"] = current_user
    result = await batches_collection.insert_one(batch_dict)
    return {"message": "Batch created", "id": str(result.inserted_id)}

@app.get("/batches/", response_model=List[dict])
async def get_batches(current_user: str = Depends(verify_token)):
    # Get user info to determine role
    user_info = await users_collection.find_one({"username": current_user})
    
    batches = []
    if user_info and user_info.get("role") == "admin":
        # Admins see their own batches
        async for batch in batches_collection.find({"user_id": current_user}):
            batch["_id"] = str(batch["_id"])
            batches.append(batch)
    else:
        # Students see all batches
        async for batch in batches_collection.find({}):
            batch["_id"] = str(batch["_id"])
            batches.append(batch)
    
    return batches

@app.delete("/batches/{batch_id}")
async def delete_batch(batch_id: str, current_user: str = Depends(verify_admin)):
    from bson import ObjectId
    result = await batches_collection.delete_one({"_id": ObjectId(batch_id), "user_id": current_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Batch not found")
    return {"message": "Batch deleted"}

# Timetable endpoints
@app.post("/timetables/generate")
async def generate_timetable(request: TimetableRequest, current_user: str = Depends(verify_admin)):
    # Fetch user-specific data
    classrooms = []
    async for classroom in classrooms_collection.find({"user_id": current_user}):
        classrooms.append(classroom)
    
    subjects = []
    async for subject in subjects_collection.find({"user_id": current_user}):
        subjects.append(subject)
    
    faculty = []
    async for f in faculty_collection.find({"user_id": current_user}):
        faculty.append(f)
    
    batches = []
    async for batch in batches_collection.find({"user_id": current_user}):
        batches.append(batch)
    
    # Generate multiple timetable options
    options = scheduler.generate_multiple_options(request, classrooms, subjects, faculty, batches)
    
    if not options:
        raise HTTPException(status_code=400, detail="Could not generate timetable with given constraints")
    
    return {"options": options, "count": len(options)}

@app.post("/timetables/save")
async def save_timetable(timetable: Timetable, current_user: str = Depends(verify_admin)):
    try:
        timetable_dict = timetable.dict(by_alias=True, exclude={"id"})
        timetable_dict["user_id"] = current_user
        result = await timetables_collection.insert_one(timetable_dict)
        logger.info(f"Timetable saved: {timetable.name}")
        return {"message": "Timetable saved", "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error saving timetable: {e}")
        raise HTTPException(status_code=500, detail="Failed to save timetable")

@app.get("/timetables/", response_model=List[dict])
async def get_timetables(current_user: str = Depends(verify_token)):
    # Get user info to determine role
    user_info = await users_collection.find_one({"username": current_user})
    
    timetables = []
    if user_info and user_info.get("role") == "admin":
        # Admins see all their created timetables
        async for timetable in timetables_collection.find({"user_id": current_user}):
            timetable["_id"] = str(timetable["_id"])
            timetables.append(timetable)
    else:
        # Students see all approved timetables
        async for timetable in timetables_collection.find({"status": "approved"}):
            timetable["_id"] = str(timetable["_id"])
            timetables.append(timetable)
    
    return timetables

@app.delete("/timetables/{timetable_id}")
async def delete_timetable(timetable_id: str, current_user: str = Depends(verify_admin)):
    
    from bson import ObjectId
    result = await timetables_collection.delete_one({"_id": ObjectId(timetable_id), "user_id": current_user})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return {"message": "Timetable deleted"}

@app.put("/timetables/{timetable_id}/approve")
async def approve_timetable(timetable_id: str, current_user: str = Depends(verify_admin)):
    
    from bson import ObjectId
    result = await timetables_collection.update_one(
        {"_id": ObjectId(timetable_id), "user_id": current_user},
        {"$set": {"status": "approved"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return {"message": "Timetable approved"}

# Image upload endpoint
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...), current_user: str = Depends(verify_token)):
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate filename exists
        if not file.filename or '.' not in file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Validate file extension
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Validate file size (5MB limit)
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = f"uploads/{filename}"
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File uploaded: {filename}")
        return {"filename": filename, "url": f"/uploads/{filename}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.get("/")
async def root():
    return {"message": "Smart Classroom & Timetable Scheduler API"}

# Profile endpoints
@app.get("/profile")
async def get_profile(current_user: str = Depends(verify_token)):
    user_info = await users_collection.find_one({"username": current_user})
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive information
    user_info.pop("hashed_password", None)
    user_info["_id"] = str(user_info["_id"])
    
    return user_info

@app.put("/profile")
async def update_profile(profile_data: ProfileUpdate, current_user: str = Depends(verify_token)):
    result = await users_collection.update_one(
        {"username": current_user},
        {"$set": {"email": profile_data.email}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated successfully"}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        await users_collection.find_one({"_id": "test"})
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)