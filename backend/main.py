from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from datetime import timedelta, datetime, timezone
from typing import List
import asyncio
import os
import uuid
import logging
from pathlib import Path
import time
from contextlib import asynccontextmanager
import csv
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from database import (
    users_collection, classrooms_collection, subjects_collection,
    faculty_collection, batches_collection, timetables_collection,
    check_database_connection, create_indexes
)
from models import (
    User, UserCreate, UserLogin, Classroom, Subject, Faculty, Batch,
    Timetable, TimetableRequest, TimetableSlot
)
from auth import (
    verify_password, get_password_hash, create_access_token,
    verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from pydantic import BaseModel, ValidationError
from bson import ObjectId
from bson.errors import InvalidId

class ProfileUpdate(BaseModel):
    email: str

try:
    from scheduler import TimetableScheduler
except ImportError:
    logger.warning("TimetableScheduler not available")
    TimetableScheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    
    # Check database connection
    if not await check_database_connection():
        logger.error("Failed to connect to database")
    else:
        await create_indexes()
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title="Smart Classroom & Timetable Scheduler",
    version="1.0.0",
    description="A secure timetable scheduling system",
    lifespan=lifespan
)

# CORS configuration - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict to frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBearer()
scheduler = TimetableScheduler() if TimetableScheduler else None

# Helper function to validate ObjectId
def validate_object_id(id_str: str) -> ObjectId:
    """Validate and convert string to ObjectId."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=400, detail="Invalid ID format")

# Helper function to check if user is admin
async def verify_admin(current_user: str = Depends(verify_token)):
    """Verify user has admin role."""
    try:
        user_info = await users_collection.find_one({"username": current_user})
        if not user_info or user_info.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user
    except Exception as e:
        logger.error(f"Error verifying admin status for {current_user}: {e}")
        raise HTTPException(status_code=500, detail="Authorization check failed")

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
    """Register a new user with validation."""
    try:
        logger.info(f"Registration attempt for user: {user.username}")
        
        # Check database connection
        if not await check_database_connection():
            raise HTTPException(status_code=503, detail="Database service unavailable")
        
        # Check for existing username
        existing_user = await users_collection.find_one({"username": user.username})
        if existing_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=409, detail="Username already registered")
        
        # Check for existing email
        existing_email = await users_collection.find_one({"email": user.email})
        if existing_email:
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(status_code=409, detail="Email already registered")
        
        # Validate batch_id for students
        if user.role == "student" and user.batch_id:
            batch_exists = await batches_collection.find_one({"_id": ObjectId(user.batch_id)})
            if not batch_exists:
                raise HTTPException(status_code=400, detail="Invalid batch selected")
        
        # Hash password with length check
        try:
            # Ensure password is within bcrypt limits
            if len(user.password.encode('utf-8')) > 72:
                # Truncate to 72 bytes
                truncated_password = user.password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
                hashed_password = get_password_hash(truncated_password)
            else:
                hashed_password = get_password_hash(user.password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Create user document
        user_dict = {
            "username": user.username.lower().strip(),
            "email": user.email.lower().strip(),
            "hashed_password": hashed_password,
            "role": user.role,
            "batch_id": getattr(user, 'batch_id', None),
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insert user
        result = await users_collection.insert_one(user_dict)
        logger.info(f"User registered successfully: {user.username}, ID: {result.inserted_id}")
        
        return {
            "message": "User created successfully",
            "user_id": str(result.inserted_id),
            "username": user.username
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Validation error during registration: {e}")
        raise HTTPException(status_code=422, detail="Invalid input data")
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

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

@app.put("/classrooms/{classroom_id}")
async def update_classroom(classroom_id: str, classroom: Classroom, current_user: str = Depends(verify_admin)):
    classroom_dict = classroom.dict(by_alias=True, exclude={"id"})
    classroom_dict["user_id"] = current_user  # Ensure user_id is preserved
    result = await classrooms_collection.update_one(
        {"_id": ObjectId(classroom_id), "user_id": current_user},
        {"$set": classroom_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return {"message": "Classroom updated"}

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
    try:
        logger.info(f"Creating subject: {subject.dict()}")
        
        # Check if subject code already exists for this user
        existing_subject = await subjects_collection.find_one({
            "code": subject.code,
            "user_id": current_user
        })
        
        if existing_subject:
            raise HTTPException(status_code=400, detail=f"Subject code '{subject.code}' already exists")
        
        subject_dict = subject.dict(by_alias=True, exclude={"id"})
        subject_dict["user_id"] = current_user
        logger.info(f"Subject dict to insert: {subject_dict}")
        result = await subjects_collection.insert_one(subject_dict)
        logger.info(f"Subject created successfully with ID: {result.inserted_id}")
        return {"message": "Subject created", "id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subject: {e}")
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=400, detail=f"Subject code '{subject.code}' already exists")
        raise HTTPException(status_code=500, detail=f"Failed to create subject: {str(e)}")

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

@app.put("/subjects/{subject_id}")
async def update_subject(subject_id: str, subject: Subject, current_user: str = Depends(verify_admin)):
    subject_dict = subject.dict(by_alias=True, exclude={"id"})
    subject_dict["user_id"] = current_user  # Ensure user_id is preserved
    result = await subjects_collection.update_one(
        {"_id": ObjectId(subject_id), "user_id": current_user},
        {"$set": subject_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Subject updated"}

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

@app.put("/faculty/{faculty_id}")
async def update_faculty(faculty_id: str, faculty: Faculty, current_user: str = Depends(verify_admin)):
    faculty_dict = faculty.dict(by_alias=True, exclude={"id"})
    faculty_dict["user_id"] = current_user  # Ensure user_id is preserved
    result = await faculty_collection.update_one(
        {"_id": ObjectId(faculty_id), "user_id": current_user},
        {"$set": faculty_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"message": "Faculty updated"}

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

@app.get("/batches/public")
async def get_public_batches():
    """Get all batches for public access (registration)"""
    batches = []
    async for batch in batches_collection.find({}):
        batch["_id"] = str(batch["_id"])
        batches.append(batch)
    return batches

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

@app.put("/batches/{batch_id}")
async def update_batch(batch_id: str, batch: Batch, current_user: str = Depends(verify_admin)):
    try:
        # Validate ObjectId
        batch_obj_id = validate_object_id(batch_id)
        
        # Create batch dictionary with defensive copying
        batch_dict = batch.dict(by_alias=True, exclude={"id"})
        
        # Ensure we don't modify any existing references
        batch_dict = {
            "name": batch_dict["name"],
            "semester": batch_dict["semester"],
            "department": batch_dict["department"],
            "student_count": batch_dict["student_count"],
            "subjects": list(batch_dict.get("subjects", [])),  # Create new list
            "user_id": current_user
        }
        
        result = await batches_collection.update_one(
            {"_id": batch_obj_id, "user_id": current_user},
            {"$set": batch_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Batch not found")
            
        logger.info(f"Batch updated successfully: {batch_id}")
        return {"message": "Batch updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating batch {batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update batch")

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
    try:
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
        
        # Debug logging
        logger.info(f"\n=== TIMETABLE GENERATION DEBUG ===")
        logger.info(f"Request: {request.dict()}")
        logger.info(f"Data counts - Classrooms: {len(classrooms)}, Subjects: {len(subjects)}, Faculty: {len(faculty)}, Batches: {len(batches)}")
        
        # Check if we have minimum required data
        if not classrooms:
            raise HTTPException(status_code=400, detail="No classrooms found. Please add classrooms first.")
        if not subjects:
            raise HTTPException(status_code=400, detail="No subjects found. Please add subjects first.")
        if not faculty:
            raise HTTPException(status_code=400, detail="No faculty found. Please add faculty first.")
        if not batches:
            raise HTTPException(status_code=400, detail="No batches found. Please add batches first.")
        
        # Debug: Check target batches
        target_batches = [b for b in batches if b['semester'] == request.semester and b['department'] == request.department]
        logger.info(f"Target batches for semester {request.semester}, department {request.department}: {len(target_batches)}")
        for batch in target_batches:
            logger.info(f"  - Batch: {batch['name']}, Subjects: {batch.get('subjects', [])}")
        
        if not target_batches:
            raise HTTPException(status_code=400, detail=f"No batches found for semester {request.semester} and department {request.department}")
        
        # Debug: Check subject-faculty mapping
        logger.info(f"\nSubject-Faculty Mapping:")
        constraint_issues = []
        for subject in subjects:
            teaching_faculty = [f['name'] for f in faculty if subject['code'] in f.get('subjects', [])]
            logger.info(f"  - {subject['code']} ({subject['name']}): {teaching_faculty}")
            
            # Debug: Show exact faculty subjects for troubleshooting
            if not teaching_faculty:
                logger.info(f"    DEBUG: No faculty found for {subject['code']}")
                for f in faculty:
                    logger.info(f"    Faculty {f['name']} subjects: {f.get('subjects', [])}")
                constraint_issues.append(f"No faculty can teach {subject['code']}")
        
        # Debug: Check batch subjects vs available subjects
        logger.info(f"\nBatch Subject Validation:")
        all_subject_codes = {s['code'] for s in subjects}
        for batch in target_batches:
            batch_subjects = set(batch.get('subjects', []))
            missing_subjects = batch_subjects - all_subject_codes
            if missing_subjects:
                constraint_issues.append(f"Batch {batch['name']} has missing subjects: {missing_subjects}")
                logger.info(f"  - Batch {batch['name']} has missing subjects: {missing_subjects}")
                logger.info(f"    Available subject codes: {all_subject_codes}")
                logger.info(f"    Batch subject codes: {batch_subjects}")
            else:
                logger.info(f"  - Batch {batch['name']} subjects are valid")
        
        # Debug: Check classroom capacity
        logger.info(f"\nClassroom Capacity Check:")
        for batch in target_batches:
            suitable_rooms = [c for c in classrooms if c['capacity'] >= batch.get('student_count', 30)]
            logger.info(f"  - Batch {batch['name']} ({batch.get('student_count', 30)} students): {len(suitable_rooms)} suitable rooms")
            if not suitable_rooms:
                constraint_issues.append(f"No classroom has sufficient capacity for batch {batch['name']} ({batch.get('student_count', 30)} students)")
        
        # If we found constraint issues, return them immediately
        if constraint_issues:
            error_detail = "Cannot generate timetable due to data constraints: " + "; ".join(constraint_issues)
            raise HTTPException(status_code=400, detail=error_detail)
        
        # Check if scheduler is available
        if not scheduler:
            raise HTTPException(status_code=500, detail="Timetable scheduler not available")
        
        # Generate multiple timetable options
        options = scheduler.generate_multiple_options(request, classrooms, subjects, faculty, batches)
        
        logger.info(f"Generated {len(options)} timetable options")
        
        if not options:
            raise HTTPException(status_code=400, detail="Could not generate timetable with given constraints. All data appears valid but scheduling algorithm failed.")
        
        return {"options": options, "count": len(options)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating timetable: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Timetable generation failed: {str(e)}")

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

@app.put("/timetables/{timetable_id}")
async def update_timetable(timetable_id: str, timetable: Timetable, current_user: str = Depends(verify_admin)):
    timetable_dict = timetable.dict(by_alias=True, exclude={"id"})
    result = await timetables_collection.update_one(
        {"_id": ObjectId(timetable_id), "user_id": current_user},
        {"$set": timetable_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return {"message": "Timetable updated"}

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

# Image upload endpoint with enhanced security
@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...), current_user: str = Depends(verify_token)):
    try:
        # Validate file exists
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate filename
        if not file.filename or '.' not in file.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Sanitize filename
        filename = file.filename.replace("..", "").replace("/", "").replace("\\", "")
        
        # Validate file extension
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Read and validate file size
        content = await file.read()
        MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)")
        
        # Validate file content (basic check)
        if len(content) < 100:  # Too small to be a valid image
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Generate secure filename
        secure_filename = f"{current_user}_{uuid.uuid4()}{file_ext}"
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        file_path = os.path.join(upload_dir, secure_filename)
        
        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        # Write file securely
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"File uploaded by {current_user}: {secure_filename}")
        return {"filename": secure_filename, "url": f"/{upload_dir}/{secure_filename}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error for user {current_user}: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

# CSV Upload endpoints
@app.post("/classrooms/upload-csv")
async def upload_classrooms_csv(file: UploadFile = File(...), current_user: str = Depends(verify_admin)):
    """Upload classrooms from CSV. Format: name,capacity,type,equipment"""
    try:
        content = await file.read()
        csv_data = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, 1):
            try:
                equipment = row.get('equipment', '').split(';') if row.get('equipment') else []
                classroom_data = {
                    "name": row['name'],
                    "capacity": int(row['capacity']),
                    "type": row['type'],
                    "equipment": equipment,
                    "user_id": current_user
                }
                
                classroom = Classroom(**classroom_data)
                await classrooms_collection.insert_one(classroom.dict(by_alias=True, exclude={"id"}))
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": f"Created {created_count} classrooms",
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")

@app.post("/subjects/upload-csv")
async def upload_subjects_csv(file: UploadFile = File(...), current_user: str = Depends(verify_admin)):
    """Upload subjects from CSV. Format: name,code,credits,type,classes_per_week,duration"""
    try:
        content = await file.read()
        csv_data = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, 1):
            try:
                subject_data = {
                    "name": row['name'],
                    "code": row['code'].upper(),
                    "credits": int(row['credits']),
                    "type": row['type'],
                    "classes_per_week": int(row['classes_per_week']),
                    "duration": int(row['duration']),
                    "user_id": current_user
                }
                
                subject = Subject(**subject_data)
                await subjects_collection.insert_one(subject.dict(by_alias=True, exclude={"id"}))
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": f"Created {created_count} subjects",
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")

@app.post("/faculty/upload-csv")
async def upload_faculty_csv(file: UploadFile = File(...), current_user: str = Depends(verify_admin)):
    """Upload faculty from CSV. Format: name,email,subjects,max_hours_per_day,avg_leaves_per_month"""
    try:
        content = await file.read()
        csv_data = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, 1):
            try:
                subjects = row.get('subjects', '').split(';') if row.get('subjects') else []
                faculty_data = {
                    "name": row['name'],
                    "email": row['email'],
                    "subjects": subjects,
                    "max_hours_per_day": int(row.get('max_hours_per_day', 6)),
                    "avg_leaves_per_month": int(row.get('avg_leaves_per_month', 2)),
                    "user_id": current_user
                }
                
                faculty = Faculty(**faculty_data)
                await faculty_collection.insert_one(faculty.dict(by_alias=True, exclude={"id"}))
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": f"Created {created_count} faculty",
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")

@app.post("/batches/upload-csv")
async def upload_batches_csv(file: UploadFile = File(...), current_user: str = Depends(verify_admin)):
    """Upload batches from CSV. Format: name,semester,department,student_count,subjects"""
    try:
        content = await file.read()
        csv_data = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, 1):
            try:
                subjects = row.get('subjects', '').split(';') if row.get('subjects') else []
                batch_data = {
                    "name": row['name'],
                    "semester": int(row['semester']),
                    "department": row['department'],
                    "student_count": int(row['student_count']),
                    "subjects": subjects,
                    "user_id": current_user
                }
                
                batch = Batch(**batch_data)
                await batches_collection.insert_one(batch.dict(by_alias=True, exclude={"id"}))
                created_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "message": f"Created {created_count} batches",
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV processing failed: {str(e)}")

# Profile endpoints
@app.get("/profile")
async def get_profile(current_user: str = Depends(verify_token)):
    user_info = await users_collection.find_one({"username": current_user})
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive information
    user_info.pop("hashed_password", None)
    user_info["_id"] = str(user_info["_id"])
    
    # If user has a batch_id, get batch details
    if user_info.get("batch_id"):
        try:
            batch_info = await batches_collection.find_one({"_id": ObjectId(user_info["batch_id"])})
            if batch_info:
                user_info["batch_name"] = batch_info["name"]
                user_info["batch_department"] = batch_info["department"]
                user_info["batch_semester"] = batch_info["semester"]
        except Exception as e:
            logger.error(f"Error fetching batch info for user {current_user}: {e}")
    
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
# CSV Template endpoints
@app.get("/templates/classrooms-csv")
async def get_classrooms_csv_template():
    """Get CSV template for classrooms upload"""
    return {
        "template": "name,capacity,type,equipment\nLecture Hall 1,100,lecture,projector;whiteboard\nLab 1,30,lab,computers;projector",
        "format": {
            "name": "string (required)",
            "capacity": "integer (required, 1-500)",
            "type": "string (required: lecture/lab/seminar)",
            "equipment": "string (optional, separate multiple with ;)"
        }
    }

@app.get("/templates/subjects-csv")
async def get_subjects_csv_template():
    """Get CSV template for subjects upload"""
    return {
        "template": "name,code,credits,type,classes_per_week,duration\nMathematics,MATH101,3,theory,4,60\nPhysics Lab,PHY101L,1,practical,2,120",
        "format": {
            "name": "string (required)",
            "code": "string (required, 2-20 chars)",
            "credits": "integer (required, 1-10)",
            "type": "string (required: theory/practical/elective)",
            "classes_per_week": "integer (required, 1-20)",
            "duration": "integer (required, minutes 1-300)"
        }
    }

@app.get("/templates/faculty-csv")
async def get_faculty_csv_template():
    """Get CSV template for faculty upload"""
    return {
        "template": "name,email,subjects,max_hours_per_day,avg_leaves_per_month\nDr. Smith,smith@college.edu,MATH101;PHY101,6,2\nProf. Johnson,johnson@college.edu,CS101,8,1",
        "format": {
            "name": "string (required)",
            "email": "email (required)",
            "subjects": "string (optional, separate codes with ;)",
            "max_hours_per_day": "integer (optional, default 6, 1-12)",
            "avg_leaves_per_month": "integer (optional, default 2, 0-10)"
        }
    }

@app.get("/templates/batches-csv")
async def get_batches_csv_template():
    """Get CSV template for batches upload"""
    return {
        "template": "name,semester,department,student_count,subjects\nCS-A,3,Computer Science,45,MATH101;PHY101;CS101\nEE-B,2,Electrical Engineering,40,MATH101;PHY101",
        "format": {
            "name": "string (required)",
            "semester": "integer (required, 1-12)",
            "department": "string (required)",
            "student_count": "integer (required, 1-1000)",
            "subjects": "string (optional, separate codes with ;)"
        }
    }