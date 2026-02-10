from pydantic import BaseModel, Field, ConfigDict, validator, EmailStr
from typing import List, Optional, Dict, Annotated
from datetime import datetime
from bson import ObjectId
import re

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")
        return field_schema

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    role: str = Field(default="admin", pattern="^(admin|student|faculty)$")
    is_active: bool = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="admin", pattern="^(admin|student|faculty)$")
    batch_id: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

class Classroom(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(..., gt=0, le=500)
    type: str = Field(..., pattern="^(lecture|lab|seminar)$")
    equipment: List[str] = Field(default=[], max_items=20)
    user_id: Optional[str] = None
    
    @validator('equipment')
    def validate_equipment(cls, v):
        return [item.strip() for item in v if item.strip()]

class Subject(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    credits: int = Field(..., gt=0, le=10)
    type: str = Field(..., pattern="^(theory|practical|elective)$")
    classes_per_week: int = Field(..., gt=0, le=20)
    duration: int = Field(..., gt=0, le=300)  # in minutes
    user_id: Optional[str] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not re.match(r'^[A-Z0-9]+$', v.upper()):
            raise ValueError('Subject code must contain only uppercase letters and numbers')
        return v.upper()

class Faculty(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    subjects: List[str] = Field(default=[], max_items=10)
    max_hours_per_day: int = Field(default=6, gt=0, le=12)
    avg_leaves_per_month: int = Field(default=2, ge=0, le=10)
    user_id: Optional[str] = None

class Batch(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    semester: int = Field(..., gt=0, le=12)
    department: str = Field(..., min_length=1, max_length=100)
    student_count: int = Field(..., gt=0, le=1000)
    subjects: List[str] = Field(default=[], max_items=20)
    user_id: Optional[str] = None

class TimetableSlot(BaseModel):
    day: str
    time: str
    subject_code: str
    faculty_name: str
    classroom_name: str
    batch_name: str

class Timetable(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    semester: int
    department: str
    slots: List[TimetableSlot]
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "draft"  # "draft", "approved", "active"
    user_id: Optional[str] = None

class TimetableRequest(BaseModel):
    name: str
    semester: int
    department: str
    max_classes_per_day: int = 8
    working_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    time_slots: List[str] = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]