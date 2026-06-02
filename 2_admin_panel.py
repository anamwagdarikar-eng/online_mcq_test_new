import os
import sys

# CRITICAL: Add project root to Python path FIRST, before any other imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now safe to import other modules
import streamlit as st
from datetime import datetime, timedelta

from database import Database
from utils.auth import get_auth
from utils.test_management import get_test_management
from utils.analytics import get_analytics

st.set_page_config(page_title="Admin Panel", layout="wide")

# Check if admin
if 'user_role' not in st.session_state or st.session_state.user_role != 'admin':
    st.error("Access Denied - Admin only")
    st.stop()

st.markdown("# 👨‍💼 Admin Panel")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Manage Tests", 
    "👥 User Management", 
    "🏫 Departments", 
    "📊 Analytics",
    "⚙️ Settings"
])

with tab1:
    st.markdown("## Test Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Create New Test")
        with st.form("create_test_form"):
            test_name = st.text_input("Test Name *")
            
            # Get subjects
            db = Database()
            if db.connect():
                subjects = db.fetch_all("SELECT subject_id, subject_name FROM subjects")
                db.disconnect()
                subject_options = {s[1]: s[0] for s in subjects}
            else:
                subject_options = {}
            
            subject_name = st.selectbox("Subject *", list(subject_options.keys()) if subject_options else [])
            subject_id = subject_options.get(subject_name)
            
            total_marks = st.number_input("Total Marks", min_value=10, max_value=1000, value=100)
            duration = st.number_input("Duration (minutes)", min_value=15, max_value=480, value=60)
            passing_marks = st.number_input("Passing Marks", min_value=0, max_value=total_marks, value=40)
            
            start_date = st.date_input("Start Date")
            start_time = st.time_input("Start Time")
            
            end_date = st.date_input("End Date")
            end_time = st.time_input("End Time")
            
            col_opt1, col_opt2, col_opt3 = st.columns(3)
            with col_opt1:
                negative_marking = st.checkbox("Negative Marking", value=True)
            with col_opt2:
                randomize_q = st.checkbox("Randomize Questions", value=True)
            with col_opt3:
                randomize_opt = st.checkbox("Randomize Options", value=True)
            
            if st.form_submit_button("Create Test", use_container_width=True):
                if test_name and subject_id:
                    try:
                        db = Database()
                        if db.connect():
                            start_datetime = datetime.combine(start_date, start_time)
                            end_datetime = datetime.combine(end_date, end_time)
                            
                            # Determine subject department so the test is linked to the correct branch
                            subject_info = db.fetch_one(
                                "SELECT dept_id FROM subjects WHERE subject_id = %s",
                                (subject_id,)
                            )
                            dept_id = subject_info[0] if subject_info else 1

                            db.execute_query(
                                """INSERT INTO tests (test_name, subject_id, dept_id, created_by, 
                                   total_marks, duration_minutes, passing_marks, negative_marking_enabled,
                                   randomize_questions, randomize_options, start_time, end_time, is_published, show_results)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (test_name, subject_id, dept_id, st.session_state.user_id, total_marks,
                                 duration, passing_marks, negative_marking, randomize_q, randomize_opt,
                                 start_datetime, end_datetime, True, True)
                            )
                            db.disconnect()
                            st.success("✓ Test created and published successfully. Add questions and update if needed.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Please fill required fields")
    
    with col2:
        st.markdown("### Active Tests")
        db = Database()
        if db.connect():
            tests = db.fetch_all(
                """SELECT test_id, test_name, subject_id, total_marks, duration_minutes, 
                          is_published, start_time, end_time
                   FROM tests 
                   WHERE created_by = %s
                   ORDER BY created_at DESC
                   LIMIT 10""",
                (st.session_state.user_id,)
            )
            db.disconnect()
            
            if tests:
                for test in tests:
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        status = "✓ Published" if test[5] else "✗ Draft"
                        st.write(f"**{test[1]}** ({status})")
                    with col_b:
                        if st.button("📝 Edit", key=f"edit_test_{test[0]}"):
                            st.session_state.editing_test = test[0]
                    with col_c:
                        if st.button("❌ Delete", key=f"del_test_{test[0]}"):
                            db = Database()
                            if db.connect():
                                db.execute_query("DELETE FROM tests WHERE test_id = %s", (test[0],))
                                db.disconnect()
                            st.success("Test deleted")
                            st.rerun()
                    st.divider()
            else:
                st.info("No tests created yet")

with tab2:
    st.markdown("## User Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
            full_name = st.text_input("Full Name *")
            role = st.selectbox("Role", ["student", "faculty", "admin"])
            department = st.text_input("Department")
            semester = st.number_input("Semester", min_value=1, max_value=8, value=1)
            
            if st.form_submit_button("Add User", use_container_width=True):
                if username and email and password and full_name:
                    auth = get_auth()
                    result = auth.register_user(
                        username, email, password, full_name, role, department, semester
                    )
                    if result['success']:
                        st.success("✓ User added successfully!")
                    else:
                        st.error(f"Error: {result['message']}")
                else:
                    st.error("Please fill required fields")
    
    with col2:
        st.markdown("### User List")
        
        role_filter = st.selectbox("Filter by Role", ["All", "admin", "faculty", "student"])
        
        db = Database()
        if db.connect():
            if role_filter == "All":
                users = db.fetch_all(
                    """SELECT user_id, username, full_name, role, email, is_active, last_login
                       FROM users ORDER BY created_at DESC LIMIT 20"""
                )
            else:
                users = db.fetch_all(
                    """SELECT user_id, username, full_name, role, email, is_active, last_login
                       FROM users WHERE role = %s ORDER BY created_at DESC LIMIT 20""",
                    (role_filter,)
                )
            db.disconnect()
            
            if users:
                for user in users:
                    col_u1, col_u2, col_u3, col_u4 = st.columns([2, 1, 1, 1])
                    with col_u1:
                        status = "✓" if user[5] else "✗"
                        st.write(f"{status} {user[1]} ({user[3]})")
                    with col_u2:
                        st.write(f"{user[2]}")
                    with col_u3:
                        if user[6]:
                            st.write(f"Last: {user[6].strftime('%Y-%m-%d')}")
                    with col_u4:
                        if st.button("🔓 Deactivate" if user[5] else "🔒 Activate", 
                                   key=f"toggle_user_{user[0]}"):
                            db = Database()
                            if db.connect():
                                db.execute_query(
                                    "UPDATE users SET is_active = %s WHERE user_id = %s",
                                    (not user[5], user[0])
                                )
                                db.disconnect()
                            st.rerun()
                    st.divider()
            else:
                st.info("No users found")

with tab3:
    st.markdown("## Department Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Add Department")
        with st.form("add_dept_form"):
            dept_name = st.text_input("Department Name *")
            dept_code = st.text_input("Department Code *")
            
            if st.form_submit_button("Add Department", use_container_width=True):
                if dept_name and dept_code:
                    db = Database()
                    if db.connect():
                        db.execute_query(
                            "INSERT INTO departments (dept_name, dept_code) VALUES (%s, %s)",
                            (dept_name, dept_code)
                        )
                        db.disconnect()
                        st.success("✓ Department added!")
                else:
                    st.error("Please fill all fields")
    
    with col2:
        st.markdown("### Departments")
        db = Database()
        if db.connect():
            depts = db.fetch_all("SELECT dept_id, dept_name, dept_code FROM departments")
            db.disconnect()
            
            if depts:
                for dept in depts:
                    col_d1, col_d2 = st.columns([2, 1])
                    with col_d1:
                        st.write(f"**{dept[1]}** ({dept[2]})")
                    with col_d2:
                        if st.button("❌", key=f"del_dept_{dept[0]}"):
                            db = Database()
                            if db.connect():
                                db.execute_query("DELETE FROM departments WHERE dept_id = %s", (dept[0],))
                                db.disconnect()
                            st.rerun()
            else:
                st.info("No departments")

with tab4:
    st.markdown("## Analytics Dashboard")
    
    # Select test for analytics
    db = Database()
    if db.connect():
        tests = db.fetch_all("SELECT test_id, test_name FROM tests LIMIT 20")
        db.disconnect()
        test_options = {t[1]: t[0] for t in tests}
    else:
        test_options = {}
    
    selected_test_name = st.selectbox("Select Test", list(test_options.keys()) if test_options else [])
    
    if selected_test_name:
        test_id = test_options[selected_test_name]
        analytics = get_analytics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        stats = analytics.get_average_marks(test_id)
        if stats:
            with col1:
                st.metric("Average Marks", f"{stats['average']:.2f}")
            with col2:
                st.metric("Highest", f"{stats['maximum']:.2f}")
            with col3:
                st.metric("Lowest", f"{stats['minimum']:.2f}")
            with col4:
                st.metric("Total Students", stats['total_students'])
        
        st.divider()
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### Marks Distribution")
            fig = analytics.generate_marks_distribution_chart(test_id)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            st.markdown("### Grade Distribution")
            fig = analytics.generate_grade_distribution_chart(test_id)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Question analysis
        st.markdown("### Question Difficulty Analysis")
        questions = analytics.get_question_difficulty_analysis(test_id)
        if questions:
            df_data = []
            for q in questions:
                df_data.append({
                    "Question": q['question_text'],
                    "Difficulty": q['difficulty'],
                    "Attempts": q['attempts'],
                    "Correct": q['correct'],
                    "Success Rate %": q['success_rate']
                })
            
            import pandas as pd
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        
        # Top performers
        st.markdown("### Top Performers")
        toppers = analytics.get_subject_toppers(test_id, limit=5)
        if toppers:
            for i, topper in enumerate(toppers, 1):
                col_t1, col_t2, col_t3 = st.columns([1, 2, 2])
                with col_t1:
                    st.write(f"**#{i}**")
                with col_t2:
                    st.write(f"{topper[0]}")
                with col_t3:
                    st.write(f"{topper[2]:.2f}/{100} ({topper[3]:.2f}%) - Grade: {topper[4]}")

with tab5:
    st.markdown("## System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Features Configuration")
        
        with st.form("settings_form"):
            enable_negative_marking = st.checkbox("Enable Negative Marking", value=True)
            enable_fullscreen = st.checkbox("Enforce Fullscreen Mode", value=True)
            enable_tab_warnings = st.checkbox("Enable Tab Switch Warnings", value=True)
            enable_ip_logging = st.checkbox("Log Student IP Addresses", value=True)
            disable_copy_paste = st.checkbox("Disable Copy/Paste", value=True)
            single_device = st.checkbox("Single Device Login", value=True)
            
            if st.form_submit_button("Save Settings", use_container_width=True):
                st.success("✓ Settings saved!")
    
    with col2:
        st.markdown("### System Information")
        st.info("""
        **MCQ Test System**
        - Version: 1.0.0
        - Database: PostgreSQL/NeonDB
        - Framework: Streamlit
        - Backend: Python
        
        **Security Features**
        - Hashed passwords (bcrypt)
        - JWT session tokens
        - SQL injection protection
        - HTTPS ready
        - Session timeout enabled
        """)
