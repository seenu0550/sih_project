import asyncio
from database import classrooms_collection, subjects_collection, faculty_collection, batches_collection
from scheduler import TimetableScheduler
from models import TimetableRequest

async def debug_scheduler():
    # Get data
    classrooms = []
    async for classroom in classrooms_collection.find():
        classrooms.append(classroom)
    
    subjects = []
    async for subject in subjects_collection.find():
        subjects.append(subject)
    
    faculty = []
    async for f in faculty_collection.find():
        faculty.append(f)
    
    batches = []
    async for batch in batches_collection.find():
        batches.append(batch)
    
    print("=== DEBUG INFO ===")
    print(f"Classrooms: {len(classrooms)}")
    print(f"Subjects: {len(subjects)}")
    print(f"Faculty: {len(faculty)}")
    print(f"Batches: {len(batches)}")
    
    # Check semester 6 data
    cs_batches = [b for b in batches if b['semester'] == 6 and b['department'] == 'Computer Science']
    print(f"\nSemester 6 CS batches: {len(cs_batches)}")
    if cs_batches:
        batch = cs_batches[0]
        print(f"Batch subjects: {batch['subjects']}")
        
        batch_subjects = [s for s in subjects if s['code'] in batch['subjects']]
        print(f"Found subjects: {[s['code'] for s in batch_subjects]}")
        
        for subject in batch_subjects:
            subject_faculty = [f for f in faculty if subject['code'] in f['subjects']]
            print(f"Subject {subject['code']} faculty: {[f['name'] for f in subject_faculty]}")

if __name__ == "__main__":
    asyncio.run(debug_scheduler())