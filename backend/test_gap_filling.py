#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import TimetableScheduler
from models import TimetableRequest
from collections import defaultdict

def test_gap_filling():
    """Test enhanced gap filling with faculty rotation"""
    
    scheduler = TimetableScheduler()
    sample_data = scheduler.get_sample_data()
    
    # Create a test request with more days
    request = TimetableRequest(
        name="Enhanced Gap Filling Test",
        semester=1,
        department="CSE",
        max_classes_per_day=7,
        working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        time_slots=["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    )
    
    # Generate timetable
    slots = scheduler.generate_timetable(
        request,
        sample_data['classrooms'],
        sample_data['subjects'],
        sample_data['faculty'],
        sample_data['batches']
    )
    
    print(f"Generated {len(slots)} time slots")
    
    # Analyze slot distribution
    valid_time_slots = [t for t in request.time_slots if t != "13:00"]
    total_possible_slots = len(request.working_days) * len(valid_time_slots)
    
    print(f"Total possible slots (excluding lunch): {total_possible_slots}")
    print(f"Filled slots: {len(slots)}")
    print(f"Fill percentage: {(len(slots) / total_possible_slots) * 100:.1f}%")
    
    # Show detailed timetable
    print("\n" + "="*80)
    print("DETAILED TIMETABLE")
    print("="*80)
    
    # Group slots by day and time
    timetable_grid = defaultdict(lambda: defaultdict(str))
    for slot in slots:
        timetable_grid[slot.day][slot.time] = f"{slot.subject_code}|{slot.faculty_name}|{slot.classroom_name}"
    
    # Print timetable grid
    print(f"{'Day':<12}", end="")
    for time in valid_time_slots:
        print(f"{time:<25}", end="")
    print()
    print("-" * 200)
    
    for day in request.working_days:
        print(f"{day:<12}", end="")
        for time in valid_time_slots:
            slot_info = timetable_grid[day].get(time, "EMPTY")
            print(f"{slot_info:<25}", end="")
        print()
    
    # Faculty rotation analysis
    print("\n" + "="*50)
    print("FACULTY ROTATION ANALYSIS")
    print("="*50)
    
    faculty_subject_count = defaultdict(lambda: defaultdict(int))
    faculty_total_count = defaultdict(int)
    
    for slot in slots:
        faculty_subject_count[slot.faculty_name][slot.subject_code] += 1
        faculty_total_count[slot.faculty_name] += 1
    
    for faculty_name in sorted(faculty_total_count.keys()):
        print(f"\n{faculty_name} (Total: {faculty_total_count[faculty_name]} classes):")
        for subject, count in sorted(faculty_subject_count[faculty_name].items()):
            print(f"  {subject}: {count} classes")
    
    # Subject distribution analysis
    print("\n" + "="*50)
    print("SUBJECT DISTRIBUTION")
    print("="*50)
    
    subject_count = defaultdict(int)
    for slot in slots:
        subject_count[slot.subject_code] += 1
    
    for subject in sorted(subject_count.keys()):
        required = next((s['classes_per_week'] for s in sample_data['subjects'] if s['code'] == subject), 0)
        actual = subject_count[subject]
        print(f"{subject}: {actual}/{required} classes ({actual/required*100:.1f}% of requirement)")
    
    # Validate for conflicts
    print("\n" + "="*50)
    print("VALIDATION RESULTS")
    print("="*50)
    
    issues = scheduler.validate_timetable(slots)
    
    if any(issues.values()):
        for issue_type, issue_list in issues.items():
            if issue_list:
                print(f"\n{issue_type.upper()}:")
                for issue in issue_list:
                    print(f"  - {issue}")
    else:
        print("No conflicts found!")
    
    return slots

if __name__ == "__main__":
    test_gap_filling()