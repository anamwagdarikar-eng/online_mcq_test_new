import os
import sys

# CRITICAL: Add project root to Python path FIRST, before any other imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now safe to import other modules
import streamlit as st
import pandas as pd

from database import Database
from utils.analytics import get_analytics

st.set_page_config(page_title="Faculty Panel", layout="wide")

# Check if faculty or admin
if 'user_role' not in st.session_state or st.session_state.user_role not in ['faculty', 'admin']:
    st.error("Access Denied - Faculty/Admin only")
    st.stop()

# Initialize session variables
if 'selected_test_id' not in st.session_state:
    st.session_state.selected_test_id = None

st.markdown("# 👨‍🏫 Faculty Panel")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Manage Questions",
    "📝 Manage Tests",
    "➕ Create Test",
    "📊 Test Analytics",
    "📤 Import Questions"
])

with tab1:
    st.markdown("## Question Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Add New Question")
        
        # Get subjects
        db = Database()
        if db.connect():
            subjects = db.fetch_all("SELECT subject_id, subject_name FROM subjects")
            db.disconnect()
            subject_options = {s[1]: s[0] for s in subjects}
        else:
            subject_options = {}
        
        with st.form("add_question_form"):
            subject_name = st.selectbox("Subject *", list(subject_options.keys()) if subject_options else [])
            subject_id = subject_options.get(subject_name)
            
            question_text = st.text_area("Question *")
            
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
            marks = st.number_input("Marks", min_value=1, max_value=100, value=1)
            
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                negative_marks = st.number_input("Negative Marks", min_value=0.0, max_value=float(marks), 
                                                value=0.25, step=0.25)
            with col_opt2:
                question_type = st.selectbox("Question Type", ["MCQ", "MSQ", "NUMERICAL"])
            
            st.markdown("**Options:**")
            col_a, col_b = st.columns(2)
            with col_a:
                opt_a = st.text_input("Option A *")
                opt_c = st.text_input("Option C *")
            with col_b:
                opt_b = st.text_input("Option B *")
                opt_d = st.text_input("Option D *")
            
            correct_ans = st.selectbox("Correct Answer *", ["A", "B", "C", "D"])
            
            explanation = st.text_area("Explanation (optional)")
            
            if st.form_submit_button("Add Question", use_container_width=True):
                if question_text and opt_a and opt_b and opt_c and opt_d and subject_id:
                    db = Database()
                    if db.connect():
                        db.execute_query(
                            """INSERT INTO questions 
                               (subject_id, question_text, question_type, difficulty_level, 
                                marks, negative_marks, option_a, option_b, option_c, option_d,
                                correct_answer, explanation, created_by)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (subject_id, question_text, question_type, difficulty, marks, 
                             negative_marks, opt_a, opt_b, opt_c, opt_d, correct_ans, 
                             explanation, st.session_state.user_id)
                        )
                        db.disconnect()
                        st.success("✓ Question added successfully!")
                else:
                    st.error("Please fill all required fields")
    
    with col2:
        st.markdown("### Question Bank")
        
        db = Database()
        if db.connect():
            questions = db.fetch_all(
                """SELECT q.question_id, q.question_text, q.difficulty_level, q.marks, s.subject_name
                   FROM questions q
                   JOIN subjects s ON q.subject_id = s.subject_id
                   WHERE q.created_by = %s
                   ORDER BY q.created_at DESC
                   LIMIT 20""",
                (st.session_state.user_id,)
            )
            db.disconnect()
            
            if questions:
                for q in questions:
                    col_q1, col_q2, col_q3 = st.columns([2, 1, 1])
                    with col_q1:
                        st.write(f"**{q[1][:50]}...**")
                    with col_q2:
                        st.write(f"{q[2]} | {q[3]} marks")
                    with col_q3:
                        if st.button("❌", key=f"del_q_{q[0]}"):
                            db = Database()
                            if db.connect():
                                db.execute_query("DELETE FROM questions WHERE question_id = %s", (q[0],))
                                db.disconnect()
                            st.rerun()
                    st.divider()
            else:
                st.info("No questions created yet")

with tab2:
    st.markdown("## Test Management")
    
    db = Database()
    if db.connect():
        if st.session_state.user_role == 'admin':
            tests = db.fetch_all(
                """SELECT test_id, test_name, subject_id, total_marks, duration_minutes, 
                          is_published, (SELECT COUNT(*) FROM test_questions WHERE test_id = tests.test_id)
                   FROM tests LIMIT 20"""
            )
        else:
            tests = db.fetch_all(
                """SELECT test_id, test_name, subject_id, total_marks, duration_minutes, 
                          is_published, (SELECT COUNT(*) FROM test_questions WHERE test_id = tests.test_id)
                   FROM tests WHERE created_by = %s LIMIT 20""",
                (st.session_state.user_id,)
            )
        db.disconnect()
        
        if tests:
            for test in tests:
                col_t1, col_t2, col_t3, col_t4 = st.columns([2, 1, 1, 1])
                with col_t1:
                    status = "✓ Published" if test[5] else "✗ Draft"
                    st.write(f"**{test[1]}** ({status})")
                with col_t2:
                    st.write(f"{test[3]} marks | {test[4]} min")
                with col_t3:
                    st.write(f"{test[6]} questions")
                with col_t4:
                    col_add, col_pub = st.columns(2)
                    with col_add:
                        if not test[5]:
                            if st.button("➕ Add Q", key=f"add_q_{test[0]}", help="Add questions to test"):
                                st.session_state.selected_test_id = test[0]
                                st.session_state.show_add_questions = True
                    with col_pub:
                        if not test[5]:
                            if st.button("📤 Pub", key=f"pub_test_{test[0]}", help="Publish test"):
                                # Check if test has questions
                                db = Database()
                                if db.connect():
                                    q_count = db.fetch_one(
                                        "SELECT COUNT(*) FROM test_questions WHERE test_id = %s",
                                        (test[0],)
                                    )
                                    db.disconnect()
                                    
                                    if q_count and q_count[0] > 0:
                                        db = Database()
                                        if db.connect():
                                            db.execute_query(
                                                "UPDATE tests SET is_published = TRUE WHERE test_id = %s",
                                                (test[0],)
                                            )
                                            db.disconnect()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Cannot publish: Add at least 1 question first!")
                        else:
                            st.write("✓ Published")
                st.divider()
        else:
            st.info("No tests available")
    
    # Add questions to test - Show in a separate section
    st.markdown("---")
    
    if 'selected_test_id' in st.session_state and st.session_state.selected_test_id:
        st.markdown("### ➕ Add Questions to Selected Test")
        
        test_id = st.session_state.selected_test_id
        
        # Get available questions
        db = Database()
        if db.connect():
            questions = db.fetch_all(
                """SELECT question_id, question_text, marks, difficulty_level FROM questions 
                   WHERE created_by = %s AND question_id NOT IN 
                   (SELECT question_id FROM test_questions WHERE test_id = %s)
                   ORDER BY created_at DESC""",
                (st.session_state.user_id, test_id)
            )
            
            # Get already added questions
            added_questions = db.fetch_all(
                """SELECT COUNT(*) FROM test_questions WHERE test_id = %s""",
                (test_id,)
            )
            db.disconnect()
        else:
            questions = []
            added_questions = [(0,)]
        
        already_added = added_questions[0][0] if added_questions else 0
        
        st.info(f"📌 Already added: **{already_added}** questions | Available: **{len(questions)}** new questions")
        
        if questions:
            # Create checkboxes for each question
            st.write("**Select questions to add:**")
            
            selected_ids = []
            for q in questions:
                checkbox = st.checkbox(
                    f"✓ {q[1][:70]}... | {q[2]} marks | {q[3]}",
                    key=f"q_checkbox_{q[0]}"
                )
                if checkbox:
                    selected_ids.append(q[0])
            
            col_add, col_cancel = st.columns(2)
            with col_add:
                if st.button("✓ Add Selected Questions", use_container_width=True, key="add_questions_button"):
                    if selected_ids:
                        db = Database()
                        if db.connect():
                            try:
                                # Get current max order
                                max_order = db.fetch_one(
                                    "SELECT COALESCE(MAX(question_order), 0) FROM test_questions WHERE test_id = %s",
                                    (test_id,)
                                )
                                current_order = max_order[0] if max_order else 0
                                
                                for qid in selected_ids:
                                    current_order += 1
                                    # Get question marks
                                    q_marks = next(q[2] for q in questions if q[0] == qid)
                                    
                                    db.execute_query(
                                        """INSERT INTO test_questions (test_id, question_id, question_order, marks, negative_marks)
                                           VALUES (%s, %s, %s, %s, %s)""",
                                        (test_id, qid, current_order, q_marks, 0.25)
                                    )
                                
                                db.disconnect()
                                st.success(f"✓ Added {len(selected_ids)} questions to test!")
                                st.session_state.selected_test_id = None
                                st.rerun()
                            except Exception as e:
                                db.disconnect()
                                st.error(f"Error adding questions: {str(e)}")
                    else:
                        st.warning("⚠️ Please select at least one question")
            
            with col_cancel:
                if st.button("✕ Cancel", use_container_width=True, key="cancel_add_button"):
                    st.session_state.selected_test_id = None
                    st.rerun()
        else:
            st.warning("⚠️ No new questions available to add. Create some questions first!")
            if st.button("✕ Cancel Selection"):
                st.session_state.selected_test_id = None
                st.rerun()

with tab3:
    st.markdown("## ➕ Create New Test")
    
    with st.form("create_test_form"):
        st.markdown("### Test Details")
        
        # Get subjects
        db = Database()
        if db.connect():
            subjects = db.fetch_all("SELECT subject_id, subject_name, dept_id, semester FROM subjects")
            db.disconnect()
            subject_details = {s[0]: {'name': s[1], 'dept_id': s[2], 'semester': s[3]} for s in subjects}
            subject_options = {f"{s[1]} (Sem {s[3]})": s[0] for s in subjects} if subjects else {}
        else:
            subject_options = {}
            subject_details = {}
        
        col1, col2 = st.columns(2)
        with col1:
            test_name = st.text_input("Test Name *", placeholder="e.g., Physics Mid Term")
            subject_name = st.selectbox("Subject *", list(subject_options.keys()) if subject_options else [])
            
        with col2:
            total_marks = st.number_input("Total Marks", min_value=10, max_value=500, value=100)
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=300, value=60)
        
        passing_marks = st.number_input("Passing Marks", min_value=0, max_value=total_marks, value=int(total_marks * 0.4))
        
        st.markdown("### Test Schedule")
        col_time1, col_time2 = st.columns(2)
        from datetime import datetime, timedelta
        with col_time1:
            start_date = st.date_input("Start Date", datetime.now())
            start_time = st.time_input("Start Time", datetime.now().time())
        with col_time2:
            end_date = st.date_input("End Date", datetime.now() + timedelta(days=1))
            end_time = st.time_input("End Time", (datetime.now() + timedelta(hours=2)).time())
        
        st.markdown("### Test Settings")
        col_set1, col_set2, col_set3 = st.columns(3)
        with col_set1:
            enable_fullscreen = st.checkbox("Enable Fullscreen", value=True)
        with col_set2:
            tab_warnings = st.checkbox("Tab Switch Warnings", value=True)
        with col_set3:
            negative_marking = st.checkbox("Negative Marking", value=True)
        
        col_rand1, col_rand2 = st.columns(2)
        with col_rand1:
            randomize_q = st.checkbox("Randomize Questions", value=True)
        with col_rand2:
            randomize_opt = st.checkbox("Randomize Options", value=True)
        
        test_description = st.text_area("Test Description (optional)", placeholder="Describe the test, instructions, etc.")
        
        if st.form_submit_button("✓ Create Test", use_container_width=True):
            if test_name and subject_name:
                subject_id = subject_options.get(subject_name)
                subject_meta = subject_details.get(subject_id, {})
                dept_id = subject_meta.get('dept_id', 1)
                
                # Convert date and time to datetime
                from datetime import datetime as dt_class
                test_start_time = dt_class.combine(start_date, start_time)
                test_end_time = dt_class.combine(end_date, end_time)
                
                db = Database()
                if db.connect():
                    try:
                        db.execute_query(
                            """INSERT INTO tests 
                               (test_name, subject_id, dept_id, created_by, test_description,
                                total_marks, duration_minutes, passing_marks, negative_marking_enabled,
                                enable_fullscreen, enable_tab_warnings, randomize_questions, randomize_options,
                                start_time, end_time)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (test_name, subject_id, dept_id, st.session_state.user_id, test_description,
                             total_marks, duration, passing_marks, negative_marking,
                             enable_fullscreen, tab_warnings, randomize_q, randomize_opt,
                             test_start_time, test_end_time)
                        )
                        
                        # Get the created test ID
                        test = db.fetch_one("SELECT LASTVAL();")
                        test_id = test[0] if test else None
                        
                        db.disconnect()
                        
                        st.success(f"✓ Test draft created successfully! (ID: {test_id})")
                        st.info("👉 Go to 'Manage Tests' tab and click '➕ Add Q' to add questions to this test before publishing it")
                    except Exception as e:
                        db.disconnect()
                        st.error(f"Error creating test: {str(e)}")
            else:
                st.error("Please fill test name and subject")

with tab4:
    st.markdown("## Test Analytics")
    
    db = Database()
    if db.connect():
        if st.session_state.user_role == 'admin':
            tests = db.fetch_all("SELECT test_id, test_name FROM tests ORDER BY created_at DESC LIMIT 20")
        else:
            tests = db.fetch_all(
                """SELECT test_id, test_name FROM tests WHERE created_by = %s 
                   ORDER BY created_at DESC LIMIT 20""",
                (st.session_state.user_id,)
            )
        db.disconnect()
        
        test_options = {t[1]: t[0] for t in tests}
    else:
        test_options = {}
    
    if test_options:
        selected_test_name = st.selectbox("Select Test", list(test_options.keys()))
        test_id = test_options[selected_test_name]
        
        analytics = get_analytics()
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        stats = analytics.get_average_marks(test_id)
        
        if stats:
            with col1:
                st.metric("Avg Marks", f"{stats['average']:.2f}")
            with col2:
                st.metric("Max Marks", f"{stats['maximum']:.2f}")
            with col3:
                st.metric("Min Marks", f"{stats['minimum']:.2f}")
            with col4:
                st.metric("Students", stats['total_students'])
        
        st.divider()
        
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### Marks Distribution")
            fig = analytics.generate_marks_distribution_chart(test_id)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            st.markdown("### Performance by Difficulty")
            fig = analytics.generate_performance_by_difficulty_chart(test_id)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Question difficulty analysis
        st.markdown("### Question Performance Analysis")
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
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Export option
            if st.button("📥 Export as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"analysis_{selected_test_name}.csv",
                    mime="text/csv"
                )
        
        st.divider()
        
        # Top performers
        st.markdown("### Top Performers")
        toppers = analytics.get_subject_toppers(test_id, limit=10)
        
        if toppers:
            for i, topper in enumerate(toppers, 1):
                col_rank, col_name, col_score = st.columns([1, 2, 2])
                with col_rank:
                    st.write(f"**#{i}** 🥇" if i == 1 else f"**#{i}** 🥈" if i == 2 else f"**#{i}** 🥉" if i == 3 else f"**#{i}**")
                with col_name:
                    st.write(topper[0])
                with col_score:
                    st.write(f"{topper[2]:.2f}/100 ({topper[3]:.2f}%) - **{topper[4]}**")

with tab5:
    st.markdown("## Bulk Import Questions")
    
    st.info("""
    Upload CSV file with questions. Format:
    - question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, marks
    """)
    
    db = Database()
    if db.connect():
        subjects = db.fetch_all("SELECT subject_id, subject_name, semester FROM subjects")
        db.disconnect()
        subject_options = {f"{s[1]} (Sem {s[2]})": s[0] for s in subjects} if subjects else {}
    else:
        subject_options = {}
    
    subject_name = st.selectbox("Subject for Import *", list(subject_options.keys()) if subject_options else [])
    subject_id = subject_options.get(subject_name, 1)
    
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:")
        st.dataframe(df.head())
        
        if st.button("Import Questions"):
            db = Database()
            if db.connect():
                success_count = 0
                error_count = 0
                
                for idx, row in df.iterrows():
                    try:
                        db.execute_query(
                            """INSERT INTO questions 
                               (subject_id, question_text, option_a, option_b, option_c, option_d,
                                correct_answer, difficulty_level, marks, created_by)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                subject_id,
                                row['question_text'],
                                row['option_a'],
                                row['option_b'],
                                row['option_c'],
                                row['option_d'],
                                row['correct_answer'],
                                row['difficulty_level'],
                                int(row.get('marks', 1)),
                                st.session_state.user_id,
                            )
                        )
                        success_count += 1
                    except Exception:
                        error_count += 1
                
                db.disconnect()
                st.success(f"✓ Imported {success_count} questions")
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} questions failed to import")
