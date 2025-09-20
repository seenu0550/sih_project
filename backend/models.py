from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Annotated
from datetime import datetime
from bson import ObjectId

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
    username: str
    email: str
    hashed_password: str
    role: str = "admin"
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "admin"

class UserLogin(BaseModel):
    username: str
    password: str

class Classroom(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    capacity: int
    type: str  # "lecture", "lab", "seminar"
    equipment: List[str] = []
    user_id: Optional[str] = None

class Subject(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    code: str
    credits: int
    type: str  # "theory", "practical", "elective"
    classes_per_week: int
    duration: int  # in minutes
    user_id: Optional[str] = None

class Faculty(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    email: str
    subjects: List[str] = []  # subject codes
    max_hours_per_day: int = 6
    avg_leaves_per_month: int = 2
    user_id: Optional[str] = None

class Batch(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    semester: int
    department: str
    student_count: int
    subjects: List[str] = []  # subject codes
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