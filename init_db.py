#!/usr/bin/env python3
"""
Database Initialization Script
Run this script to initialize the PostgreSQL/NeonDB database
"""

import os
import sys

# CRITICAL: Add project root to Python path FIRST, before any other imports
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
from database import Database

load_dotenv()

def main():
    print("=" * 60)
    print("MCQ Test System - Database Initialization")
    print("=" * 60)
    
    db = Database()
    
    print("\n📡 Connecting to database...")
    if db.init_database():
        print("\n✓ Database initialized successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - departments")
        print("  - subjects")
        print("  - course_outcomes")
        print("  - program_outcomes")
        print("  - questions")
        print("  - tests")
        print("  - test_questions")
        print("  - student_responses")
        print("  - test_attempts")
        print("  - test_results")
        print("  - sessions")
        print("  - login_attempts")
        print("  - audit_log")
        print("  - co_po_mapping")
        print("  - student_registry")
        
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("1. Run: streamlit run main.py")
        print("2. Create admin user through the application")
        print("3. Login and configure departments/subjects")
        print("=" * 60)
        
        return 0
    else:
        print("\n✗ Failed to initialize database")
        print("Check your DATABASE_URL in .env file")
        return 1

if __name__ == "__main__":
    sys.exit(main())
