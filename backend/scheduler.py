from typing import List, Dict, Set, Tuple
from models import TimetableSlot, TimetableRequest
from collections import defaultdict
import random


class TimetableScheduler:
    LUNCH_TIME = '13:00'
    DEFAULT_FACULTY_DAILY_LIMIT = 6
    DEFAULT_STUDENT_COUNT = 30
    DEFAULT_CLASSES_PER_WEEK = 3
    DEFAULT_DURATION = 1

    def __init__(self):
        pass

    # ======================================================
    # PUBLIC API
    # ======================================================
    def generate_timetable(
        self,
        request: TimetableRequest,
        classrooms: List[Dict],
        subjects: List[Dict],
        faculty: List[Dict],
        batches: List[Dict],
    ) -> List[TimetableSlot]:

        batches = [b.copy() for b in batches]

        target_batches = [
            b for b in batches
            if b['semester'] == request.semester
            and b['department'] == request.department
        ]
        if not target_batches:
            return []

        valid_time_slots = [t for t in request.time_slots if t != self.LUNCH_TIME]

        schedule_plan = self._create_schedule_plan(
            target_batches,
            subjects,
            request.working_days,
            valid_time_slots
        )
        
        print(f"DEBUG: Schedule plan created with {len(schedule_plan)} sessions")
        if not schedule_plan:
            print("DEBUG: No schedule plan created - returning empty")
            return []

        slots = self._assign_resources(
            schedule_plan,
            faculty,
            classrooms,
            valid_time_slots
        )
        
        print(f"DEBUG: Resource assignment completed with {len(slots)} slots")
        return slots

    # ======================================================
    # STEP 1 — SUBJECT & TIME PLANNING
    # ======================================================
    def _create_schedule_plan(
        self,
        batches: List[Dict],
        subjects: List[Dict],
        working_days: List[str],
        time_slots: List[str]
    ) -> List[Dict]:

        lab_sessions = []
        theory_sessions = []

        # Create sessions only for subjects assigned to each batch
        for batch in batches:
            batch_subjects = [s for s in subjects if s['code'] in batch['subjects']]
            print(f"DEBUG: Batch {batch['name']} has {len(batch_subjects)} subjects: {[s['code'] for s in batch_subjects]}")
            
            for subject in batch_subjects:
                classes = subject.get('classes_per_week', self.DEFAULT_CLASSES_PER_WEEK)
                duration = subject.get('duration', 1)
                s_type = subject.get('type', 'theory')
                print(f"DEBUG: Subject {subject['code']} - type: {s_type}, classes: {classes}, duration: {duration}")

                if s_type in ['lab', 'practical']:
                    # Convert duration from minutes to number of time slots (assuming 60 min per slot)
                    duration_slots = max(1, duration // 60) if duration > 60 else 1
                    sessions = classes
                    for i in range(sessions):
                        lab_sessions.append({
                            'subject_code': subject['code'],
                            'subject_name': subject['name'],
                            'subject_type': s_type,
                            'duration': duration_slots,
                            'batch': batch.copy(),
                            'session_id': f"{subject['code']}_{batch['name']}_{i}"
                        })
                else:
                    for i in range(classes):
                        theory_sessions.append({
                            'subject_code': subject['code'],
                            'subject_name': subject['name'],
                            'subject_type': s_type,
                            'duration': 1,
                            'batch': batch.copy(),
                            'session_id': f"{subject['code']}_{batch['name']}_{i}"
                        })

        # Shuffle sessions for variation
        random.shuffle(lab_sessions)
        random.shuffle(theory_sessions)

        all_slots = [
            {'day': d, 'time': t}
            for d in working_days
            for t in time_slots
        ]
        print(f"DEBUG: Available slots: {len(all_slots)} ({len(working_days)} days x {len(time_slots)} times)")

        used = set()
        plan = []
        subject_day_slots = defaultdict(lambda: defaultdict(list))

        # First allocate lab sessions (continuous slots)
        for session in lab_sessions:
            if session['duration'] > 1:
                slots = self._find_continuous_slots(session, all_slots, used, time_slots)
                if slots:
                    for i, s in enumerate(slots):
                        plan.append({
                            **session,
                            'day': s['day'],
                            'time': s['time'],
                            'part': i + 1
                        })
                        used.add((s['day'], s['time']))
                        subject_day_slots[session['subject_code']][s['day']].append(s['time'])
                    print(f"DEBUG: Allocated continuous slots for {session['subject_code']}")
                else:
                    print(f"DEBUG: Failed to find continuous slots for {session['subject_code']}")
            else:
                slot = self._find_single_slot(session, all_slots, used, subject_day_slots)
                if slot:
                    plan.append({
                        **session,
                        'day': slot['day'],
                        'time': slot['time']
                    })
                    used.add((slot['day'], slot['time']))
                    subject_day_slots[session['subject_code']][slot['day']].append(slot['time'])
                    print(f"DEBUG: Allocated single slot for {session['subject_code']}")
                else:
                    print(f"DEBUG: Failed to find single slot for {session['subject_code']}")

        # Then allocate theory sessions (non-continuous)
        for session in theory_sessions:
            slot = self._find_single_slot(session, all_slots, used, subject_day_slots)
            if slot:
                plan.append({
                    **session,
                    'day': slot['day'],
                    'time': slot['time']
                })
                used.add((slot['day'], slot['time']))
                subject_day_slots[session['subject_code']][slot['day']].append(slot['time'])
                print(f"DEBUG: Allocated theory slot for {session['subject_code']}")
            else:
                print(f"DEBUG: Failed to find theory slot for {session['subject_code']}")

        # Fill remaining empty slots by repeating subjects
        remaining_slots = [s for s in all_slots if (s['day'], s['time']) not in used]
        if remaining_slots and (lab_sessions or theory_sessions):
            all_sessions = lab_sessions + theory_sessions
            session_index = 0
            
            for slot in remaining_slots:
                if session_index >= len(all_sessions):
                    session_index = 0
                
                session = all_sessions[session_index].copy()
                session['session_id'] = f"{session['subject_code']}_{session['batch']['name']}_extra_{len(plan)}"
                
                plan.append({
                    **session,
                    'day': slot['day'],
                    'time': slot['time']
                })
                used.add((slot['day'], slot['time']))
                session_index += 1
                print(f"DEBUG: Filled empty slot with {session['subject_code']}")

        print(f"DEBUG: Final plan has {len(plan)} scheduled sessions")
        return plan

    def _find_continuous_slots(self, session, slots, used, time_slots):
        duration = session['duration']

        by_day = defaultdict(list)
        for s in slots:
            if (s['day'], s['time']) not in used:
                by_day[s['day']].append(s)

        for day, day_slots in by_day.items():
            day_slots.sort(key=lambda s: time_slots.index(s['time']))
            for i in range(len(day_slots) - duration + 1):
                block = day_slots[i:i + duration]

                idxs = [time_slots.index(x['time']) for x in block]
                if idxs != list(range(idxs[0], idxs[0] + duration)):
                    continue

                if self._crosses_lunch(idxs, time_slots):
                    continue

                return block
        return None

    def _crosses_lunch(self, indices, time_slots):
        for i in indices:
            if i + 1 < len(time_slots):
                if time_slots[i] == '12:00' and time_slots[i + 1] == '14:00':
                    return True
        return False

    def _find_single_slot(self, session, slots, used, subject_day_slots=None):
        subject_code = session['subject_code']
        subject_type = session['subject_type']
        
        # For theory subjects, avoid continuous allocation
        if subject_type == 'theory' and subject_day_slots:
            non_continuous_slots = []
            continuous_slots = []
            
            for s in slots:
                if (s['day'], s['time']) in used:
                    continue
                    
                # Check if this slot would be continuous with existing slots
                existing_times = subject_day_slots[subject_code][s['day']]
                is_continuous = False
                
                if existing_times:
                    time_idx = slots.index(s) if s in slots else -1
                    for existing_time in existing_times:
                        existing_slot = next((slot for slot in slots if slot['day'] == s['day'] and slot['time'] == existing_time), None)
                        if existing_slot:
                            existing_idx = slots.index(existing_slot) if existing_slot in slots else -1
                            if abs(time_idx - existing_idx) == 1:
                                is_continuous = True
                                break
                
                if not is_continuous:
                    non_continuous_slots.append(s)
                else:
                    continuous_slots.append(s)
            
            # Prefer non-continuous slots for theory subjects
            return non_continuous_slots[0] if non_continuous_slots else (continuous_slots[0] if continuous_slots else None)
        
        # For lab subjects or when no subject_day_slots provided, find any available slot
        for s in slots:
            if (s['day'], s['time']) not in used:
                return s
        return None

    # ======================================================
    # STEP 2 — FACULTY + CLASSROOM ASSIGNMENT (STRICT)
    # ======================================================
    def _assign_resources(self, plan, faculty, classrooms, time_slots):

        slots = []
        faculty_schedule = defaultdict(lambda: defaultdict(set))
        room_schedule = defaultdict(lambda: defaultdict(set))

        # 🔐 HARD LOCK MAP
        faculty_subject_batch = {}

        lab_subjects = {
            p['subject_code'] for p in plan
            if p['subject_type'] in ['lab', 'practical']
        }

        plan.sort(key=lambda x: (x['day'], x['time']))

        for p in plan:
            key = (p['subject_code'], p['batch']['name'])

            if key in faculty_subject_batch:
                fname = faculty_subject_batch[key]
                fac = next((f for f in faculty if f['name'] == fname), None)
                if not fac:
                    continue
                if p['time'] in faculty_schedule[fname][p['day']]:
                    continue
            else:
                fac = self._find_best_faculty(
                    p, faculty, faculty_schedule, time_slots, lab_subjects
                )
                if not fac:
                    continue
                faculty_subject_batch[key] = fac['name']

            room = self._find_best_classroom(
                p['subject_type'],
                classrooms,
                room_schedule,
                p['day'],
                p['time'],
                p['batch'].get('student_count', self.DEFAULT_STUDENT_COUNT)
            )
            if not room:
                continue

            subject_code = p['subject_code']
            if p.get('duration', 1) > 1 and 'part' in p:
                subject_code += f" (Part {p['part']})"

            slots.append(TimetableSlot(
                day=p['day'],
                time=p['time'],
                subject_code=subject_code,
                faculty_name=fac['name'],
                classroom_name=room['name'],
                batch_name=p['batch']['name']
            ))

            faculty_schedule[fac['name']][p['day']].add(p['time'])
            room_schedule[room['name']][p['day']].add(p['time'])

        return slots

    def _find_best_faculty(self, p, faculty, faculty_schedule, time_slots, lab_subjects):
        # Find available faculty for the subject, maintaining consistency
        for f in faculty:
            if p['subject_code'] not in f.get('subjects', []):
                continue
            if p['time'] in faculty_schedule[f['name']][p['day']]:
                continue
            return f
        return None

    def _is_continuous(self, day_times, new_time, time_slots):
        if not day_times:
            return False
        idx = time_slots.index(new_time)
        for t in day_times:
            if abs(idx - time_slots.index(t)) == 1:
                return True
        return False

    def _find_best_classroom(
        self,
        subject_type,
        classrooms,
        room_schedule,
        day,
        time,
        students
    ):
        for c in classrooms:
            if time in room_schedule[c['name']][day]:
                continue
            if c['capacity'] < students:
                continue
            if subject_type == 'lab' and c.get('type') != 'lab':
                continue
            return c
        return None

    def generate_multiple_options(self, request: TimetableRequest, classrooms: List[Dict], 
                                subjects: List[Dict], faculty: List[Dict], 
                                batches: List[Dict]) -> List[List[TimetableSlot]]:
        """Generate multiple timetable options with different arrangements"""
        options = []
        
        for i in range(3):
            # Use different random seeds for variation
            random.seed(i * 123 + 456)
            
            # Shuffle the order of subjects and sessions for variation
            subjects_copy = subjects.copy()
            random.shuffle(subjects_copy)
            
            # Shuffle working days for different day arrangements
            working_days = request.working_days.copy()
            if i > 0:  # Keep first option with original order
                random.shuffle(working_days)
            
            # Create modified request with shuffled days
            modified_request = TimetableRequest(
                name=request.name,
                semester=request.semester,
                department=request.department,
                max_classes_per_day=request.max_classes_per_day,
                working_days=working_days,
                time_slots=request.time_slots
            )
            
            timetable = self.generate_timetable(modified_request, classrooms, subjects_copy, faculty, batches)
            if timetable:
                options.append(timetable)
        
        random.seed()
        return options

    def validate_timetable(self, slots: List[TimetableSlot]) -> Dict[str, List[str]]:
        """Validate timetable for any conflicts"""
        issues = {
            'faculty_conflicts': [],
            'classroom_conflicts': [],
            'continuous_allocation': [],
            'warnings': []
        }
        
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
