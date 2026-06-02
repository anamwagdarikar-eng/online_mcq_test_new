#!/usr/bin/env python3
"""
Sample Data Seeding Script
Run this to populate the database with sample data for testing
"""

import os
import sys

# CRITICAL: Add project root to Python path FIRST, before any other imports
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from datetime import datetime, timedelta
from database import Database
from utils.auth import get_auth

def seed_sample_data():
    print("=" * 60)
    print("MCQ Test System - Sample Data Seeding")
    print("=" * 60)
    
    db = Database()
    auth = get_auth()
    
    if not db.connect():
        print("✗ Database connection failed")
        return False
    
    try:
        # 1. Create Departments
        print("\n📍 Creating departments...")
        departments = [
            ("Computer Science", "CS"),
            ("Mechanical Engineering", "ME"),
            ("Electrical Engineering", "EE"),
            ("Civil Engineering", "CE"),
            ("Electronics Engineering", "EC")
        ]
        
        for dept_name, dept_code in departments:
            db.execute_query(
                "INSERT INTO departments (dept_name, dept_code) VALUES (%s, %s)",
                (dept_name, dept_code)
            )
        print(f"✓ Created {len(departments)} departments")
        
        # 2. Create Subjects
        print("\n📚 Creating subjects...")
        subjects = [
            (1, "Data Structures", "DS", 2),
            (1, "Database Management", "DBMS", 3),
            (1, "Web Development", "WEB", 4),
            (2, "Thermodynamics", "TH", 3),
            (2, "Fluid Mechanics", "FM", 4),
            (3, "Circuit Analysis", "CA", 3),
            (3, "Power Systems", "PS", 4),
        ]
        
        for dept_id, subject_name, subject_code, semester in subjects:
            db.execute_query(
                """INSERT INTO subjects (subject_name, subject_code, dept_id, semester)
                   VALUES (%s, %s, %s, %s)""",
                (subject_name, subject_code, dept_id, semester)
            )
        print(f"✓ Created {len(subjects)} subjects")
        
        # 3. Create admin user
        print("\n👨‍💼 Creating admin user...")
        result = auth.register_user(
            "admin", "admin@college.edu", "Admin@123", "System Administrator", "admin", 
            "Administration", 1
        )
        print(f"✓ Admin user created: {result['message']}")
        
        # 4. Create faculty users
        print("\n👨‍🏫 Creating faculty users...")
        faculties = [
            ("faculty1", "faculty1@college.edu", "Faculty@123", "Dr. Raj Kumar", "CS"),
            ("faculty2", "faculty2@college.edu", "Faculty@123", "Prof. Asha Singh", "ME"),
            ("faculty3", "faculty3@college.edu", "Faculty@123", "Dr. Priya Sharma", "EE"),
        ]
        
        for username, email, password, name, dept in faculties:
            auth.register_user(username, email, password, name, "faculty", dept, 1)
        print(f"✓ Created {len(faculties)} faculty users")
        
        # 5. Create student users
        print("\n👨‍🎓 Creating student users...")
        for i in range(1, 11):
            auth.register_user(
                f"student{i:02d}",
                f"student{i:02d}@college.edu",
                f"Student@{i:03d}",
                f"Student {i}",
                "student",
                "Computer Science",
                2
            )
        print("✓ Created 10 sample students")
        
        # 6. Create Course Outcomes
        print("\n🎯 Creating course outcomes...")
        db.execute_query(
            "INSERT INTO course_outcomes (subject_id, co_code, co_description) VALUES (%s, %s, %s)",
            (1, "CO1", "Understand fundamental data structures")
        )
        db.execute_query(
            "INSERT INTO course_outcomes (subject_id, co_code, co_description) VALUES (%s, %s, %s)",
            (1, "CO2", "Implement and analyze algorithms")
        )
        print("✓ Created course outcomes")
        
        # 7. Create Program Outcomes
        print("\n📋 Creating program outcomes...")
        db.execute_query(
            "INSERT INTO program_outcomes (dept_id, po_code, po_description) VALUES (%s, %s, %s)",
            (1, "PO1", "Engineering Knowledge")
        )
        print("✓ Created program outcomes")
        
        # 8. Create Sample Questions
        print("\n❓ Creating sample questions...")
        questions = [
            (1, "What is the time complexity of Binary Search?", 
             "O(n^2)", "O(n log n)", "O(log n)", "O(1)", "C", "Binary search divides the array in half", 
             "Medium", 1, 0.25, 1),
            (1, "Which data structure uses LIFO principle?",
             "Queue", "Stack", "Array", "Tree", "B", "LIFO = Last In First Out",
             "Easy", 1, 0.25, 1),
            (1, "What is dynamic programming?",
             "Programming at runtime", "Optimization technique using memoization", "Pointer usage", 
             "Memory allocation", "B", "DP solves problems by breaking them into subproblems",
             "Hard", 2, 0.5, 2),
        ]
        
        for question_data in questions:
            db.execute_query(
                """INSERT INTO questions 
                   (subject_id, question_text, option_a, option_b, option_c, option_d,
                    correct_answer, explanation, difficulty_level, marks, negative_marks, co_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                question_data
            )
        print(f"✓ Created {len(questions)} sample questions")
        
        # 9. Create Sample Test
        print("\n📝 Creating sample test...")
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        db.execute_query(
            """INSERT INTO tests 
               (test_name, subject_id, dept_id, created_by, total_marks, duration_minutes,
                passing_marks, negative_marking_enabled, randomize_questions, randomize_options,
                start_time, end_time, is_published, show_results)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            ("Data Structures Mid Term Test", 1, 1, 2, 100, 120, 40, True, True, True,
             start_time, end_time, True, True)
        )
        print("✓ Created sample test")
        
        # 10. Add questions to test
        print("\n🔗 Adding questions to test...")
        test = db.fetch_one("SELECT test_id FROM tests WHERE test_name = %s", 
                           ("Data Structures Mid Term Test",))
        if test:
            test_id = test[0]
            for i, q_id in enumerate([1, 2, 3], 1):
                db.execute_query(
                    """INSERT INTO test_questions (test_id, question_id, question_order)
                       VALUES (%s, %s, %s)""",
                    (test_id, q_id, i)
                )
        print("✓ Added questions to test")
        
        db.disconnect()
        
        print("\n" + "=" * 60)
        print("✓ Sample data seeding completed successfully!")
        print("\nYou can now login with:")
        print("  Admin: admin / Admin@123")
        print("  Faculty: faculty1 / Faculty@123")
        print("  Student: student01 / Student@001")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.disconnect()
        return False

if __name__ == "__main__":
    import sys
    success = seed_sample_data()
    sys.exit(0 if success else 1)
