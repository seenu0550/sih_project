#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler import TimetableScheduler
from models import TimetableRequest

def test_improved_scheduler():
    """Test the improved scheduler to see slot filling"""
    
    scheduler = TimetableScheduler()
    sample_data = scheduler.get_sample_data()
    
    # Create a test request
    request = TimetableRequest(
        name="Test Timetable",
        semester=1,
        department="CSE",
        max_classes_per_day=7,
        working_days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
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
    
    # Show distribution by day
    day_distribution = {}
    for slot in slots:
        if slot.day not in day_distribution:
            day_distribution[slot.day] = []
        day_distribution[slot.day].append(slot)
    
    print("\nSlot distribution by day:")
    for day in request.working_days:
        count = len(day_distribution.get(day, []))
        print(f"{day}: {count} slots")
    
    # Show faculty utilization
    faculty_usage = {}
    for slot in slots:
        if slot.faculty_name not in faculty_usage:
            faculty_usage[slot.faculty_name] = 0
        faculty_usage[slot.faculty_name] += 1
    
    print("\nFaculty utilization:")
    for faculty, count in sorted(faculty_usage.items()):
        print(f"{faculty}: {count} classes")
    
    return slots

if __name__ == "__main__":
    test_improved_scheduler()