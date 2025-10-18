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
        """Generate timetable with strict anti-continuous allocation"""
        
        target_batches = [b for b in batches if b['semester'] == request.semester and b['department'] == request.department]
        if not target_batches:
            return []
        
        valid_time_slots = [t for t in request.time_slots if t != self.LUNCH_TIME]
        
        # Create a comprehensive schedule plan first
        schedule_plan = self._create_schedule_plan(target_batches, subjects, request.working_days, valid_time_slots)
        
        # Now assign faculty and classrooms to the plan
        slots = self._assign_resources(schedule_plan, faculty, classrooms, valid_time_slots)
        
        return slots
    
    def _create_schedule_plan(self, batches: List[Dict], subjects: List[Dict], 
                            working_days: List[str], time_slots: List[str]) -> List[Dict]:
        """Create a schedule plan with proper subject distribution"""
        
        # Calculate subject requirements
        subject_sessions = []
        
        for batch in batches:
            batch_subjects = [s for s in subjects if s['code'] in batch['subjects']]
            
            for subject in batch_subjects:
                classes_needed = subject.get('classes_per_week', 3)
                
                for session_num in range(classes_needed):
                    subject_sessions.append({
                        'subject_code': subject['code'],
                        'subject_name': subject['name'],
                        'subject_type': subject.get('type', 'theory'),
                        'batch': batch,
                        'session_id': f"{subject['code']}_{batch['name']}_{session_num}"
                    })
        
        # Create time slots grid
        all_time_slots = []
        for day in working_days:
            for time in time_slots:
                all_time_slots.append({'day': day, 'time': time, 'assigned': None})
        
        # Distribute subjects across time slots with anti-continuous logic
        random.shuffle(subject_sessions)  # Initial randomization
        
        scheduled_plan = []
        used_slots = set()
        
        # For each subject session, find the best non-continuous slot
        for session in subject_sessions:
            best_slot = self._find_best_time_slot(
                session, all_time_slots, scheduled_plan, time_slots, used_slots
            )
            
            if best_slot:
                scheduled_plan.append({
                    'day': best_slot['day'],
                    'time': best_slot['time'],
                    'subject_code': session['subject_code'],
                    'subject_name': session['subject_name'],
                    'subject_type': session['subject_type'],
                    'batch': session['batch'],
                    'session_id': session['session_id']
                })
                used_slots.add((best_slot['day'], best_slot['time']))
        
        return scheduled_plan
    
    def _find_best_time_slot(self, session: Dict, available_slots: List[Dict], 
                           current_plan: List[Dict], time_slots: List[str], 
                           used_slots: Set[Tuple]) -> Dict:
        """Find best time slot avoiding continuous allocation"""
        
        subject_code = session['subject_code']
        
        # Get already scheduled slots for this subject
        subject_scheduled_slots = [
            (p['day'], p['time']) for p in current_plan 
            if p['subject_code'] == subject_code
        ]
        
        # Score each available slot
        slot_scores = []
        
        for slot in available_slots:
            if (slot['day'], slot['time']) in used_slots:
                continue
            
            score = self._calculate_slot_score(
                slot, subject_code, subject_scheduled_slots, time_slots, current_plan
            )
            
            if score > 0:  # Only consider valid slots
                slot_scores.append((slot, score))
        
        if not slot_scores:
            return None
        
        # Sort by score (higher is better) and return best slot
        slot_scores.sort(key=lambda x: x[1], reverse=True)
        return slot_scores[0][0]
    
    def _calculate_slot_score(self, slot: Dict, subject_code: str, 
                            existing_slots: List[Tuple], time_slots: List[str],
                            current_plan: List[Dict]) -> float:
        """Calculate score for a time slot (higher = better, 0 = invalid)"""
        
        day = slot['day']
        time = slot['time']
        time_index = time_slots.index(time)
        
        score = 100.0  # Base score
        
        # Check for continuous allocation with existing slots of same subject
        for existing_day, existing_time in existing_slots:
            if existing_day == day:  # Same day
                existing_index = time_slots.index(existing_time)
                
                # Heavily penalize adjacent time slots
                if abs(time_index - existing_index) == 1:
                    return 0  # Invalid - continuous allocation
                
                # Penalize close time slots
                if abs(time_index - existing_index) == 2:
                    score -= 40
        
        # Check day distribution - prefer spreading across different days
        days_used = set(existing_day for existing_day, _ in existing_slots)
        if day not in days_used:
            score += 30  # Bonus for new day
        
        # Prefer middle slots over edge slots for better distribution
        if 1 <= time_index <= len(time_slots) - 2:
            score += 10
        
        # Check subject density in this day
        subjects_this_day = [p['subject_code'] for p in current_plan if p['day'] == day]
        if subject_code in subjects_this_day:
            score -= 20  # Penalty for same subject already scheduled this day
        
        # Prefer balanced time distribution
        time_usage = defaultdict(int)
        for p in current_plan:
            time_usage[p['time']] += 1
        
        current_time_usage = time_usage[time]
        if current_time_usage == 0:
            score += 15  # Bonus for unused time slots
        else:
            score -= current_time_usage * 5  # Penalty for overused times
        
        return score
    
    def _assign_resources(self, schedule_plan: List[Dict], faculty: List[Dict], 
                         classrooms: List[Dict], time_slots: List[str]) -> List[TimetableSlot]:
        """Assign faculty and classrooms to the schedule plan"""
        
        slots = []
        faculty_schedule = defaultdict(lambda: defaultdict(set))
        classroom_schedule = defaultdict(lambda: defaultdict(set))
        faculty_subject_rotation = defaultdict(lambda: defaultdict(int))
        
        # Sort plan to prioritize difficult-to-schedule items
        schedule_plan.sort(key=lambda x: (x['day'], x['time']))
        
        for plan_item in schedule_plan:
            day = plan_item['day']
            time = plan_item['time']
            subject_code = plan_item['subject_code']
            batch = plan_item['batch']
            
            # Find best faculty for this assignment
            best_faculty = self._find_best_faculty(
                subject_code, faculty, faculty_schedule, faculty_subject_rotation,
                day, time, time_slots
            )
            
            if not best_faculty:
                continue  # Skip if no faculty available
            
            # Find available classroom
            best_classroom = self._find_best_classroom(
                plan_item['subject_type'], classrooms, classroom_schedule,
                day, time, batch.get('student_count', 30)
            )
            
            if not best_classroom:
                continue  # Skip if no classroom available
            
            # Create the slot
            slot = TimetableSlot(
                day=day,
                time=time,
                subject_code=subject_code,
                faculty_name=best_faculty['name'],
                classroom_name=best_classroom['name'],
                batch_name=batch['name']
            )
            
            slots.append(slot)
            
            # Update tracking
            faculty_schedule[best_faculty['name']][day].add(time)
            classroom_schedule[best_classroom['name']][day].add(time)
            faculty_subject_rotation[best_faculty['name']][subject_code] += 1
        
        # Fill remaining gaps with intelligent rotation
        self._fill_gaps(slots, faculty, classrooms, schedule_plan, faculty_schedule, classroom_schedule, time_slots)
        
        # Additional gap filling for better coverage
        self._fill_subject_gaps(slots, faculty, classrooms, schedule_plan, faculty_schedule, classroom_schedule, time_slots)
        
        # Fill all remaining empty slots
        self._fill_all_remaining_gaps(slots, faculty, classrooms, schedule_plan, faculty_schedule, classroom_schedule, time_slots)
        
        return slots
    
    def _find_best_faculty(self, subject_code: str, faculty: List[Dict],
                          faculty_schedule: Dict, faculty_subject_rotation: Dict,
                          day: str, time: str, time_slots: List[str]) -> Dict:
        """Find best faculty avoiding continuous allocation"""
        
        available_faculty = []
        
        for f in faculty:
            # Check if faculty can teach this subject
            if subject_code not in f.get('subjects', []):
                continue
            
            faculty_name = f['name']
            
            # Check availability
            if time in faculty_schedule[faculty_name][day]:
                continue
            
            # Check daily load limit
            if len(faculty_schedule[faculty_name][day]) >= 4:
                continue
            
            # Check for continuous teaching (same faculty, same day)
            is_continuous = self._would_be_continuous(
                faculty_schedule[faculty_name][day], time, time_slots
            )
            
            if is_continuous:
                continue  # Skip continuous allocation
            
            available_faculty.append(f)
        
        if not available_faculty:
            return None
        
        # Select faculty with least teaching load for this subject (rotation)
        best_faculty = min(
            available_faculty,
            key=lambda f: (
                faculty_subject_rotation[f['name']][subject_code],  # Subject rotation
                len(faculty_schedule[f['name']][day])  # Daily load
            )
        )
        
        return best_faculty
    
    def _would_be_continuous(self, faculty_day_schedule: Set[str], 
                           new_time: str, time_slots: List[str]) -> bool:
        """Check if adding new_time would create continuous allocation"""
        
        if not faculty_day_schedule:
            return False
        
        try:
            new_time_index = time_slots.index(new_time)
            
            for scheduled_time in faculty_day_schedule:
                scheduled_index = time_slots.index(scheduled_time)
                
                # Check if adjacent (continuous)
                if abs(new_time_index - scheduled_index) == 1:
                    return True
                    
        except ValueError:
            pass
        
        return False
    
    def _find_best_classroom(self, subject_type: str, classrooms: List[Dict],
                           classroom_schedule: Dict, day: str, time: str,
                           student_count: int) -> Dict:
        """Find best available classroom"""
        
        available_classrooms = []
        
        for classroom in classrooms:
            # Check availability
            if time in classroom_schedule[classroom['name']][day]:
                continue
            
            # Check capacity
            if classroom['capacity'] < student_count:
                continue
            
            available_classrooms.append(classroom)
        
        if not available_classrooms:
            return None
        
        # Prefer classrooms that match subject type
        type_matched = [
            c for c in available_classrooms
            if (subject_type == 'practical' and c.get('type') == 'lab') or
               (subject_type == 'theory' and c.get('type') in ['lecture', 'seminar'])
        ]
        
        if type_matched:
            return type_matched[0]
        
        return available_classrooms[0]
    
    def generate_multiple_options(self, request: TimetableRequest, classrooms: List[Dict], 
                                subjects: List[Dict], faculty: List[Dict], 
                                batches: List[Dict]) -> List[List[TimetableSlot]]:
        """Generate multiple timetable options with different arrangements"""
        options = []
        
        for i in range(3):
            # Set different random seeds for variation
            random.seed(i * 456 + 789)
            
            timetable = self.generate_timetable(request, classrooms, subjects, faculty, batches)
            
            if timetable:
                options.append(timetable)
        
        # Reset random seed
        random.seed()
        return options
    
    def validate_timetable(self, slots: List[TimetableSlot]) -> Dict[str, List[str]]:
        """Validate timetable for any conflicts"""
        issues = {
            'faculty_conflicts': [],
            'classroom_conflicts': [],
            'heavy_load': [],
            'continuous_allocation': [],
            'warnings': []
        }
        
        # Group by faculty and day
        faculty_daily = defaultdict(lambda: defaultdict(list))
        
        for slot in slots:
            faculty_daily[slot.faculty_name][slot.day].append(slot)
        
        # Check for continuous allocation
        time_slots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00']
        
        for faculty_name, daily_schedule in faculty_daily.items():
            for day, day_slots in daily_schedule.items():
                # Sort by time
                day_slots.sort(key=lambda x: time_slots.index(x.time))
                
                # Check for continuous slots
                for i in range(len(day_slots) - 1):
                    current_time_idx = time_slots.index(day_slots[i].time)
                    next_time_idx = time_slots.index(day_slots[i + 1].time)
                    
                    if next_time_idx == current_time_idx + 1:  # Continuous
                        issues['continuous_allocation'].append(
                            f"{faculty_name} has continuous classes on {day}: "
                            f"{day_slots[i].time}({day_slots[i].subject_code}) -> "
                            f"{day_slots[i + 1].time}({day_slots[i + 1].subject_code})"
                        )
        
        # Standard conflict checking
        schedule_grid = defaultdict(lambda: defaultdict(list))
        for slot in slots:
            schedule_grid[slot.day][slot.time].append(slot)
        
        for day, day_schedule in schedule_grid.items():
            for time, time_slots_list in day_schedule.items():
                if len(time_slots_list) <= 1:
                    continue
                
                faculty_usage = defaultdict(list)
                classroom_usage = defaultdict(list)
                
                for slot in time_slots_list:
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
            {'code': 'CS201', 'name': 'Advanced Programming', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS202', 'name': 'Algorithms', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS203', 'name': 'Software Engineering', 'type': 'theory', 'classes_per_week': 2, 'department': 'CSE'},
            {'code': 'CS301', 'name': 'Machine Learning', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS401', 'name': 'Computer Networks', 'type': 'theory', 'classes_per_week': 3, 'department': 'CSE'},
            {'code': 'CS402', 'name': 'Database Management', 'type': 'theory', 'classes_per_week': 2, 'department': 'CSE'},
            {'code': 'CS403', 'name': 'Web Development', 'type': 'practical', 'classes_per_week': 2, 'department': 'CSE'},
            {'code': 'MA201', 'name': 'Discrete Mathematics', 'type': 'theory', 'classes_per_week': 4, 'department': 'MATH'}
        ]
        
        # Enhanced Faculty with broader subject coverage
        faculty = [
            {'name': 'Ram', 'department': 'CSE', 'subjects': ['CS401', 'CS201', 'CS202']},
            {'name': 'Manoj', 'department': 'CSE', 'subjects': ['CS201', 'CS203', 'CS301']},
            {'name': 'Koushe', 'department': 'CSE', 'subjects': ['CS202', 'CS203', 'CS401']},
            {'name': 'John', 'department': 'CSE', 'subjects': ['CS203', 'CS301', 'CS402']},
            {'name': 'RC', 'department': 'CSE', 'subjects': ['CS301', 'CS401', 'CS403']},
            {'name': 'Charan', 'department': 'CSE', 'subjects': ['CS402', 'CS403', 'CS201']},
            {'name': 'akhil', 'department': 'CSE', 'subjects': ['CS403', 'CS201', 'CS202']},
            {'name': 'Prof. Math', 'department': 'MATH', 'subjects': ['MA201']},
        ]
        
        # Sample Batches
        batches = [
            {
                'name': 'CSE-1',
                'department': 'CSE',
                'semester': 1,
                'student_count': 45,
                'subjects': ['CS201', 'CS202', 'CS203', 'CS301', 'MA201']
            }
        ]
        
        return {
            'classrooms': classrooms,
            'subjects': subjects,
            'faculty': faculty,
            'batches': batches
        }
    
    def _fill_gaps(self, slots: List[TimetableSlot], faculty: List[Dict], 
                   classrooms: List[Dict], original_plan: List[Dict],
                   faculty_schedule: Dict, classroom_schedule: Dict, 
                   time_slots: List[str]):
        """Fill empty slots with intelligent faculty rotation"""
        
        # Get all days from original plan
        all_days = set(item['day'] for item in original_plan)
        
        # Find scheduled slots
        scheduled_slots = set((slot.day, slot.time) for slot in slots)
        
        # Track faculty workload per subject for rotation
        faculty_subject_load = defaultdict(lambda: defaultdict(int))
        for slot in slots:
            faculty_subject_load[slot.faculty_name][slot.subject_code] += 1
        
        # Create prioritized subject options
        subject_demand = defaultdict(int)
        for item in original_plan:
            subject_demand[item['subject_code']] += 1
        
        # Sort subjects by demand (higher demand = higher priority)
        subject_options = []
        for item in original_plan:
            subject_options.append({
                'subject_code': item['subject_code'],
                'batch': item['batch'],
                'priority': subject_demand[item['subject_code']]
            })
        
        # Sort by priority (higher first)
        subject_options.sort(key=lambda x: x['priority'], reverse=True)
        
        # Fill gaps with rotation logic
        for day in all_days:
            for time in time_slots:
                if (day, time) in scheduled_slots:
                    continue
                
                best_assignment = None
                best_score = -1
                
                # Try each subject option and score the assignment
                for option in subject_options:
                    subject_code = option['subject_code']
                    batch = option['batch']
                    
                    # Find best faculty for this subject with rotation
                    best_faculty = self._find_rotation_faculty(
                        subject_code, faculty, faculty_schedule, 
                        faculty_subject_load, day, time, time_slots
                    )
                    
                    if not best_faculty:
                        continue
                    
                    # Find suitable classroom
                    best_classroom = self._find_best_classroom(
                        option.get('subject_type', 'theory'), classrooms, 
                        classroom_schedule, day, time, batch.get('student_count', 30)
                    )
                    
                    if not best_classroom:
                        continue
                    
                    # Calculate assignment score
                    score = self._calculate_assignment_score(
                        best_faculty, subject_code, faculty_subject_load,
                        faculty_schedule, day, time, option['priority']
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_assignment = {
                            'faculty': best_faculty,
                            'classroom': best_classroom,
                            'subject_code': subject_code,
                            'batch': batch
                        }
                
                # Make the best assignment
                if best_assignment:
                    slot = TimetableSlot(
                        day=day,
                        time=time,
                        subject_code=best_assignment['subject_code'],
                        faculty_name=best_assignment['faculty']['name'],
                        classroom_name=best_assignment['classroom']['name'],
                        batch_name=best_assignment['batch']['name']
                    )
                    
                    slots.append(slot)
                    faculty_schedule[best_assignment['faculty']['name']][day].add(time)
                    classroom_schedule[best_assignment['classroom']['name']][day].add(time)
                    faculty_subject_load[best_assignment['faculty']['name']][best_assignment['subject_code']] += 1
                    scheduled_slots.add((day, time))
    
    def _find_rotation_faculty(self, subject_code: str, faculty: List[Dict],
                              faculty_schedule: Dict, faculty_subject_load: Dict,
                              day: str, time: str, time_slots: List[str]) -> Dict:
        """Find faculty using rotation logic to balance workload"""
        
        available_faculty = []
        
        for f in faculty:
            # Check if faculty can teach this subject
            if subject_code not in f.get('subjects', []):
                continue
            
            faculty_name = f['name']
            
            # Check availability
            if time in faculty_schedule[faculty_name][day]:
                continue
            
            # Check daily load limit (max 5 classes per day)
            if len(faculty_schedule[faculty_name][day]) >= 5:
                continue
            
            # Check for continuous teaching
            if self._would_be_continuous(faculty_schedule[faculty_name][day], time, time_slots):
                continue
            
            available_faculty.append(f)
        
        if not available_faculty:
            return None
        
        # Select faculty with least load for this subject (rotation)
        best_faculty = min(
            available_faculty,
            key=lambda f: (
                faculty_subject_load[f['name']][subject_code],  # Subject-specific load
                sum(faculty_subject_load[f['name']].values()),  # Total load
                len(faculty_schedule[f['name']][day])  # Daily load
            )
        )
        
        return best_faculty
    
    def _calculate_assignment_score(self, faculty: Dict, subject_code: str,
                                   faculty_subject_load: Dict, faculty_schedule: Dict,
                                   day: str, time: str, subject_priority: int) -> float:
        """Calculate score for faculty assignment (higher = better)"""
        
        faculty_name = faculty['name']
        
        # Base score from subject priority
        score = subject_priority * 10
        
        # Bonus for balanced faculty rotation (less load = higher score)
        current_subject_load = faculty_subject_load[faculty_name][subject_code]
        total_faculty_load = sum(faculty_subject_load[faculty_name].values())
        
        # Prefer faculty with less load for this subject
        score += (10 - current_subject_load) * 5
        
        # Prefer faculty with less total load
        score += (20 - total_faculty_load) * 2
        
        # Prefer faculty with less daily load
        daily_load = len(faculty_schedule[faculty_name][day])
        score += (5 - daily_load) * 3
        
        return score
    
    def _fill_subject_gaps(self, slots: List[TimetableSlot], faculty: List[Dict],
                          classrooms: List[Dict], schedule_plan: List[Dict],
                          faculty_schedule: Dict, classroom_schedule: Dict,
                          time_slots: List[str]):
        """Fill gaps to meet minimum subject requirements"""
        
        # Get all days from schedule plan
        all_days = set(item['day'] for item in schedule_plan)
        
        # Count current subject allocations
        subject_counts = defaultdict(int)
        for slot in slots:
            subject_counts[slot.subject_code] += 1
        
        # Find subjects that need more classes
        subject_requirements = defaultdict(int)
        for item in schedule_plan:
            subject_requirements[item['subject_code']] += 1
        
        # Find empty slots to fill
        empty_slots = self._find_empty_slots(slots, all_days, time_slots)
        
        # Fill gaps for subjects that are under-represented
        for subject_code, required_count in subject_requirements.items():
            current_count = subject_counts[subject_code]
            
            if current_count < required_count:
                needed = required_count - current_count
                filled = 0
                
                for day, time in empty_slots:
                    if filled >= needed:
                        break
                    
                    # Find best faculty for this subject
                    best_faculty = self._find_rotation_faculty(
                        subject_code, faculty, faculty_schedule,
                        defaultdict(lambda: defaultdict(int)), day, time, time_slots
                    )
                    
                    if not best_faculty:
                        continue
                    
                    # Find available classroom
                    best_classroom = None
                    for classroom in classrooms:
                        if time not in classroom_schedule[classroom['name']][day]:
                            best_classroom = classroom
                            break
                    
                    if not best_classroom:
                        continue
                    
                    # Get batch info from schedule plan
                    batch_info = None
                    for item in schedule_plan:
                        if item['subject_code'] == subject_code:
                            batch_info = item['batch']
                            break
                    
                    if not batch_info:
                        continue
                    
                    # Create the slot
                    slot = TimetableSlot(
                        day=day,
                        time=time,
                        subject_code=subject_code,
                        faculty_name=best_faculty['name'],
                        classroom_name=best_classroom['name'],
                        batch_name=batch_info['name']
                    )
                    
                    slots.append(slot)
                    faculty_schedule[best_faculty['name']][day].add(time)
                    classroom_schedule[best_classroom['name']][day].add(time)
                    subject_counts[subject_code] += 1
                    filled += 1
                    
                    # Remove from empty slots
                    if (day, time) in empty_slots:
                        empty_slots.remove((day, time))
    
    def _find_empty_slots(self, slots: List[TimetableSlot], working_days: Set[str],
                         time_slots: List[str]) -> List[Tuple[str, str]]:
        """Find all empty time slots"""
        
        occupied = set((slot.day, slot.time) for slot in slots)
        empty_slots = []
        
        for day in working_days:
            for time in time_slots:
                if time == self.LUNCH_TIME:  # Skip lunch time
                    continue
                if (day, time) not in occupied:
                    empty_slots.append((day, time))
        
        return empty_slots
    
    def _fill_all_remaining_gaps(self, slots: List[TimetableSlot], faculty: List[Dict],
                               classrooms: List[Dict], schedule_plan: List[Dict],
                               faculty_schedule: Dict, classroom_schedule: Dict,
                               time_slots: List[str]):
        """Fill all remaining empty slots with available subjects"""
        
        # Get all days from schedule plan
        all_days = set(item['day'] for item in schedule_plan)
        
        # Get unique subjects from schedule plan
        unique_subjects = {}
        for item in schedule_plan:
            if item['subject_code'] not in unique_subjects:
                unique_subjects[item['subject_code']] = {
                    'subject_code': item['subject_code'],
                    'batch': item['batch'],
                    'subject_type': item.get('subject_type', 'theory')
                }
        
        available_subjects = list(unique_subjects.values())
        
        # Track faculty load for better rotation
        faculty_load = defaultdict(lambda: defaultdict(int))
        for slot in slots:
            faculty_load[slot.faculty_name][slot.subject_code] += 1
        
        # Fill each empty slot
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            empty_slots = self._find_empty_slots(slots, all_days, time_slots)
            if not empty_slots:
                break
                
            filled_any = False
            
            for day, time in empty_slots:
                best_assignment = None
                best_score = -1
                
                # Try each available subject
                for subject_info in available_subjects:
                    subject_code = subject_info['subject_code']
                    batch = subject_info['batch']
                    
                    # Find available faculty (relaxed constraints for gap filling)
                    available_faculty = []
                    for f in faculty:
                        if subject_code not in f.get('subjects', []):
                            continue
                        
                        faculty_name = f['name']
                        
                        # Check availability
                        if time in faculty_schedule[faculty_name][day]:
                            continue
                        
                        # Relaxed daily load limit for gap filling
                        if len(faculty_schedule[faculty_name][day]) >= 6:
                            continue
                        
                        available_faculty.append(f)
                    
                    if not available_faculty:
                        continue
                    
                    # Select faculty with least load
                    best_faculty = min(
                        available_faculty,
                        key=lambda f: (
                            faculty_load[f['name']][subject_code],
                            sum(faculty_load[f['name']].values()),
                            len(faculty_schedule[f['name']][day])
                        )
                    )
                    
                    # Find available classroom
                    best_classroom = None
                    for classroom in classrooms:
                        if time not in classroom_schedule[classroom['name']][day]:
                            if classroom['capacity'] >= batch.get('student_count', 30):
                                best_classroom = classroom
                                break
                    
                    if not best_classroom:
                        continue
                    
                    # Calculate score
                    current_subject_count = sum(1 for slot in slots if slot.subject_code == subject_code)
                    score = 100 - current_subject_count + random.randint(1, 10)
                    
                    if score > best_score:
                        best_score = score
                        best_assignment = {
                            'faculty': best_faculty,
                            'classroom': best_classroom,
                            'subject_code': subject_code,
                            'batch': batch
                        }
                
                # Make assignment if found
                if best_assignment:
                    slot = TimetableSlot(
                        day=day,
                        time=time,
                        subject_code=best_assignment['subject_code'],
                        faculty_name=best_assignment['faculty']['name'],
                        classroom_name=best_assignment['classroom']['name'],
                        batch_name=best_assignment['batch']['name']
                    )
                    
                    slots.append(slot)
                    faculty_schedule[best_assignment['faculty']['name']][day].add(time)
                    classroom_schedule[best_assignment['classroom']['name']][day].add(time)
                    faculty_load[best_assignment['faculty']['name']][best_assignment['subject_code']] += 1
                    filled_any = True
                    break  # Move to next iteration to recalculate empty slots
            
            if not filled_any:
                break  # No more slots can be filled
            
            iteration += 1