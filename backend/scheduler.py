from typing import List, Dict, Set, Tuple
from models import TimetableSlot, TimetableRequest
from collections import defaultdict
import random

class TimetableScheduler:
    LUNCH_TIME = '13:00'
    
    def __init__(self):
        pass
    
    def generate_timetable(self, request: TimetableRequest, classrooms: List[Dict], 
                          subjects: List[Dict], faculty: List[Dict], batches: List[Dict]) -> List[TimetableSlot]:
        """Generate conflict-free timetable with proper resource allocation"""
        
        target_batches = [b for b in batches if b['semester'] == request.semester and b['department'] == request.department]
        if not target_batches:
            return []
        
        slots = []
        valid_time_slots = [t for t in request.time_slots if t != self.LUNCH_TIME]
        
        # Track resource usage to prevent conflicts
        faculty_schedule = defaultdict(lambda: defaultdict(set))  # faculty -> day -> set of times
        classroom_schedule = defaultdict(lambda: defaultdict(set))  # classroom -> day -> set of times
        
        for batch in target_batches:
            batch_subjects = [s for s in subjects if s['code'] in batch['subjects']]
            if not batch_subjects:
                continue
            
            # Create subject distribution
            subject_schedule = []
            for subject in batch_subjects:
                classes_needed = subject.get('classes_per_week', 3)
                for _ in range(classes_needed):
                    subject_schedule.append(subject)
            
            random.shuffle(subject_schedule)
            subject_idx = 0
            
            for day in request.working_days:
                daily_classes = 0
                
                for time in valid_time_slots:
                    if daily_classes >= request.max_classes_per_day or subject_idx >= len(subject_schedule):
                        break
                    
                    subject = subject_schedule[subject_idx]
                    
                    # Find available faculty (no conflicts, no consecutive periods)
                    available_faculty = self._get_available_faculty(
                        subject, faculty, faculty_schedule, day, time, valid_time_slots
                    )
                    
                    if not available_faculty:
                        subject_idx += 1
                        continue
                    
                    assigned_faculty = available_faculty[0]
                    
                    # Find available classroom (no conflicts)
                    available_classroom = self._get_available_classroom(
                        subject, classrooms, classroom_schedule, day, time, batch.get('student_count', 30)
                    )
                    
                    if not available_classroom:
                        subject_idx += 1
                        continue
                    
                    # Create slot
                    slot = TimetableSlot(
                        day=day,
                        time=time,
                        subject_code=subject['code'],
                        faculty_name=assigned_faculty['name'],
                        classroom_name=available_classroom['name'],
                        batch_name=batch['name']
                    )
                    
                    slots.append(slot)
                    
                    # Update resource tracking
                    faculty_schedule[assigned_faculty['name']][day].add(time)
                    classroom_schedule[available_classroom['name']][day].add(time)
                    
                    subject_idx += 1
                    daily_classes += 1
        
        return slots
    
    def _get_available_faculty(self, subject: Dict, faculty: List[Dict], 
                              faculty_schedule: Dict, day: str, time: str, 
                              valid_time_slots: List[str]) -> List[Dict]:
        """Get faculty available for this slot with no conflicts or consecutive periods"""
        
        available = []
        time_idx = valid_time_slots.index(time)
        
        for f in faculty:
            # Check if faculty can teach this subject
            if subject['code'] not in f.get('subjects', []):
                continue
            
            faculty_name = f['name']
            
            # Check if faculty is already scheduled at this time
            if time in faculty_schedule[faculty_name][day]:
                continue
            
            # Check for consecutive periods (avoid back-to-back classes)
            has_consecutive = False
            
            # Check previous time slot
            if time_idx > 0:
                prev_time = valid_time_slots[time_idx - 1]
                if prev_time in faculty_schedule[faculty_name][day]:
                    has_consecutive = True
            
            # Check next time slot
            if time_idx < len(valid_time_slots) - 1:
                next_time = valid_time_slots[time_idx + 1]
                if next_time in faculty_schedule[faculty_name][day]:
                    has_consecutive = True
            
            if not has_consecutive:
                available.append(f)
        
        return available
    
    def _get_available_classroom(self, subject: Dict, classrooms: List[Dict], 
                                classroom_schedule: Dict, day: str, time: str, 
                                student_count: int) -> Dict:
        """Get classroom available for this slot with no conflicts"""
        
        for classroom in classrooms:
            # Check capacity
            if classroom['capacity'] < student_count:
                continue
            
            # Check if classroom is already booked
            if time in classroom_schedule[classroom['name']][day]:
                continue
            
            # Check subject-classroom compatibility
            if subject.get('type') == 'practical' and classroom.get('type') != 'lab':
                continue
            
            if subject.get('type') == 'theory' and classroom.get('type') not in ['lecture', 'seminar']:
                continue
            
            return classroom
        
        # Fallback: return first available classroom regardless of type
        for classroom in classrooms:
            if classroom['capacity'] >= student_count and time not in classroom_schedule[classroom['name']][day]:
                return classroom
        
        return None
    
    def generate_multiple_options(self, request: TimetableRequest, classrooms: List[Dict], 
                                subjects: List[Dict], faculty: List[Dict], 
                                batches: List[Dict]) -> List[List[TimetableSlot]]:
        """Generate multiple conflict-free timetable options"""
        options = []
        
        for i in range(3):
            # Create variations by shuffling order
            shuffled_subjects = subjects.copy()
            shuffled_faculty = faculty.copy()
            
            if i > 0:
                random.shuffle(shuffled_subjects)
                random.shuffle(shuffled_faculty)
            
            timetable = self.generate_timetable(request, classrooms, shuffled_subjects, shuffled_faculty, batches)
            
            if timetable and timetable not in options:
                options.append(timetable)
        
        return options
    
    def validate_timetable(self, slots: List[TimetableSlot]) -> Dict[str, List[str]]:
        """Validate timetable for any conflicts"""
        issues = {
            'faculty_conflicts': [],
            'classroom_conflicts': [],
            'consecutive_faculty': [],
            'warnings': []
        }
        
        # Group by day and time
        schedule_grid = defaultdict(lambda: defaultdict(list))
        faculty_daily = defaultdict(lambda: defaultdict(list))
        
        for slot in slots:
            schedule_grid[slot.day][slot.time].append(slot)
            faculty_daily[slot.faculty_name][slot.day].append(slot.time)
        
        # Check for conflicts
        for day, day_schedule in schedule_grid.items():
            for time, time_slots in day_schedule.items():
                if len(time_slots) <= 1:
                    continue
                
                # Faculty conflicts
                faculty_usage = defaultdict(list)
                classroom_usage = defaultdict(list)
                
                for slot in time_slots:
                    faculty_usage[slot.faculty_name].append(slot)
                    classroom_usage[slot.classroom_name].append(slot)
                
                for faculty_name, faculty_slots in faculty_usage.items():
                    if len(faculty_slots) > 1:
                        batches = [s.batch_name for s in faculty_slots]
                        issues['faculty_conflicts'].append(
                            f"{faculty_name} has conflict on {day} at {time} with batches: {', '.join(batches)}"
                        )
                
                for classroom_name, room_slots in classroom_usage.items():
                    if len(room_slots) > 1:
                        batches = [s.batch_name for s in room_slots]
                        issues['classroom_conflicts'].append(
                            f"{classroom_name} has conflict on {day} at {time} with batches: {', '.join(batches)}"
                        )
        
        # Check consecutive faculty periods
        time_order = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00']
        
        for faculty_name, daily_schedule in faculty_daily.items():
            for day, times in daily_schedule.items():
                if len(times) <= 1:
                    continue
                
                sorted_times = sorted(times, key=lambda t: time_order.index(t) if t in time_order else 999)
                
                for i in range(len(sorted_times) - 1):
                    current_idx = time_order.index(sorted_times[i])
                    next_idx = time_order.index(sorted_times[i + 1])
                    
                    if next_idx == current_idx + 1:  # Consecutive
                        issues['consecutive_faculty'].append(
                            f"{faculty_name} has consecutive periods on {day}: {sorted_times[i]} and {sorted_times[i + 1]}"
                        )
        
        return issues
    
    def get_sample_data(self) -> Dict:
        """Generate sample data for testing the scheduler"""
        
        # Sample Classrooms
        classrooms = [
            {'name': 'LH-101', 'capacity': 60, 'type': 'lecture'},
            {'name': 'LH-102', 'capacity': 80, 'type': 'lecture'},
            {'name': 'SR-201', 'capacity': 40, 'type': 'seminar'},
            {'name': 'LAB-301', 'capacity': 30, 'type': 'lab'},
            {'name': 'LAB-302', 'capacity': 35, 'type': 'lab'},
            {'name': 'LH-103', 'capacity': 100, 'type': 'lecture'}
        ]
        
        # Sample Subjects
        subjects = [
            {'code': 'CS101', 'name': 'Programming Fundamentals', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS102', 'name': 'Data Structures', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS103', 'name': 'Database Systems', 'type': 'theory', 'classes_per_week': 2, 'department': 'CSE'},
            {'code': 'CS104', 'name': 'Programming Lab', 'type': 'practical', 'classes_per_week': 2, 'department': 'CSE'},
            {'code': 'CS105', 'name': 'Web Development', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'MA101', 'name': 'Mathematics', 'type': 'theory', 'classes_per_week': 4, 'department': 'MATH'},
            {'code': 'PH101', 'name': 'Physics', 'type': 'theory', 'classes_per_week': 3, 'department': 'PHY'},
            {'code': 'EN101', 'name': 'English', 'type': 'theory', 'classes_per_week': 2, 'department': 'ENG'}
        ]
        
        # Sample Faculty
        faculty = [
            {'name': 'Dr. Smith', 'department': 'CSE', 'subjects': ['CS101', 'CS102']},
            {'name': 'Prof. Johnson', 'department': 'CSE', 'subjects': ['CS103', 'CS104']},
            {'name': 'Dr. Williams', 'department': 'CSE', 'subjects': ['CS105', 'CS101']},
            {'name': 'Prof. Brown', 'department': 'CSE', 'subjects': ['CS102', 'CS104']},
            {'name': 'Dr. Davis', 'department': 'MATH', 'subjects': ['MA101']},
            {'name': 'Prof. Wilson', 'department': 'PHY', 'subjects': ['PH101']},
            {'name': 'Dr. Miller', 'department': 'ENG', 'subjects': ['EN101']},
            {'name': 'Prof. Garcia', 'department': 'CSE', 'subjects': ['CS103', 'CS105']}
        ]
        
        # Sample Batches
        batches = [
            {
                'name': 'CSE-A-2024',
                'department': 'CSE',
                'semester': 1,
                'student_count': 45,
                'subjects': ['CS101', 'CS102', 'CS104', 'MA101', 'EN101']
            },
            {
                'name': 'CSE-B-2024',
                'department': 'CSE', 
                'semester': 1,
                'student_count': 42,
                'subjects': ['CS101', 'CS103', 'CS105', 'MA101', 'PH101']
            },
            {
                'name': 'CSE-C-2023',
                'department': 'CSE',
                'semester': 3,
                'student_count': 38,
                'subjects': ['CS102', 'CS103', 'CS104', 'CS105']
            }
        ]
        
        return {
            'classrooms': classrooms,
            'subjects': subjects,
            'faculty': faculty,
            'batches': batches
        }