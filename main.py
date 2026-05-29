import os
import sys
from pathlib import Path

# CRITICAL: Find project root before importing modules
# Search upward and downward from the current file to support different deploy layouts.
_current_file = Path(__file__).resolve()
_start_path = _current_file.parent

print(f"[DEBUG] main.py path={_current_file} cwd={Path.cwd()}", file=sys.stderr)

def _find_project_root(start_path: Path) -> Path:
    def has_required_files(root: Path) -> bool:
        return (root / "config.py").is_file() and (
            (root / "auth.py").is_file() or (root / "utils" / "auth.py").is_file()
        )

    candidates = []
    for path in [start_path, Path.cwd()]:
        if path is None:
            continue
        candidates.append(path)
        candidates.extend(path.parents)

    seen = set()
    for candidate in candidates:
        try:
            candidate = candidate.resolve()
        except Exception:
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        print(f"[DEBUG] checking upward candidate={candidate}", file=sys.stderr)
        if has_required_files(candidate):
            print(f"[DEBUG] found project root upward={candidate}", file=sys.stderr)
            return candidate

    for base in [start_path, Path.cwd()]:
        if base is None:
            continue
        for config_path in base.rglob("config.py"):
            root = config_path.parent
            if root in seen:
                continue
            seen.add(root)
            print(f"[DEBUG] scanning tree under={base}, found config={config_path}", file=sys.stderr)
            if has_required_files(root):
                print(f"[DEBUG] found project root via rglob={root}", file=sys.stderr)
                return root

    raise FileNotFoundError(
        "Could not locate project root containing config.py and auth.py or utils/auth.py. "
        f"Checked: {_current_file.parent}, cwd={Path.cwd()}, its parents, and immediate tree scans."
    )

_project_root = _find_project_root(_start_path)
_project_root_str = str(_project_root)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)

import streamlit as st
from datetime import datetime, timedelta

from config import APP_NAME, COLLEGE_NAME, ACADEMIC_YEAR, SESSION_TIMEOUT
from utils.auth import get_auth
from utils.security import get_security
from database import Database

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for college-style UI
st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .college-logo {
        text-align: center;
        font-size: 48px;
        margin-bottom: 10px;
    }
    .college-info {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
    }
    .login-container {
        max-width: 400px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .timer {
        font-size: 24px;
        font-weight: bold;
        color: #ff6b6b;
        text-align: center;
        padding: 10px;
    }
    .question-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .option-button {
        margin: 10px 0;
        padding: 15px;
        border: 2px solid #ddd;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .option-button:hover {
        border-color: #667eea;
        background-color: #f0f4ff;
    }
    </style>
""", unsafe_allow_html=True)

# Session state management
if 'session_token' not in st.session_state:
    st.session_state.session_token = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_test' not in st.session_state:
    st.session_state.current_test = None
if 'attempt_id' not in st.session_state:
    st.session_state.attempt_id = None

def show_header():
    """Display college header"""
    st.markdown(f"""
    <div class="header-container">
        <div class="college-logo">🎓</div>
        <div class="college-info">{COLLEGE_NAME}</div>
        <div style="text-align: center; font-size: 14px; margin-top: 10px;">
            Academic Year: {ACADEMIC_YEAR}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_login():
    """Show login page"""
    show_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["student", "faculty", "admin"])
            submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit and username and password:
            auth = get_auth()
            security = get_security()
            
            # Get client IP
            ip_address = "192.168.1.1"  # In production, get from request headers
            
            # Attempt login
            result = auth.login_user(username, password, ip_address)
            
            if result['success']:
                st.session_state.session_token = result['session_token']
                st.session_state.user_id = result['user_id']
                st.session_state.user_role = result['role']
                st.session_state.username = result['username']
                
                # Log action
                security.log_audit(
                    result['user_id'],
                    'LOGIN',
                    f'User {username} logged in',
                    ip_address,
                    'Mozilla/5.0'
                )
                
                st.success("✓ Login successful!")
                st.rerun()
            else:
                st.error(f"✗ {result['message']}")
        
        # Info for new users
        st.info("👨‍🎓 Use your college username or email to login")

def show_main():
    """Show main application after login"""
    if st.session_state.user_role == 'student':
        show_student_dashboard()
    elif st.session_state.user_role == 'faculty':
        show_faculty_dashboard()
    elif st.session_state.user_role == 'admin':
        show_admin_dashboard()

def show_student_dashboard():
    """Student dashboard"""
    show_header()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Welcome", st.session_state.username)
    
    with col2:
        if st.button("📝 Available Tests"):
            st.session_state.page = "available_tests"
    
    with col3:
        if st.button("📊 My Results"):
            st.session_state.page = "my_results"
    
    st.divider()
    
    # Content based on page
    if st.session_state.get('page') == 'available_tests':
        show_available_tests()
    elif st.session_state.get('page') == 'my_results':
        show_my_results()
    else:
        st.markdown("### 📚 Available Tests")
        db = Database()
        if db.connect():
            tests = db.fetch_all(
                """SELECT test_id, test_name, subject_id, duration_minutes, total_marks, start_time, end_time
                   FROM tests WHERE is_published = TRUE AND NOW() < end_time
                   ORDER BY start_time"""
            )
            db.disconnect()
            
            if tests:
                for test in tests:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{test[1]}**")
                    with col2:
                        st.write(f"⏱️ {test[3]} mins | 📍 {test[4]} marks")
                    with col3:
                        if st.button(f"Start Test", key=f"test_{test[0]}"):
                            st.session_state.current_test = test[0]
                            st.rerun()
            else:
                st.info("No tests available at the moment.")

def show_available_tests():
    """Show available tests"""
    st.markdown("### 📝 Available Tests")
    # Implementation similar to dashboard

def show_my_results():
    """Show student results"""
    st.markdown("### 📊 My Test Results")
    db = Database()
    if db.connect():
        results = db.fetch_all(
            """SELECT tr.result_id, t.test_name, tr.marks_obtained, tr.percentage, tr.grade, tr.passed, tr.created_at
               FROM test_results tr
               JOIN tests t ON tr.test_id = t.test_id
               WHERE tr.student_id = %s
               ORDER BY tr.created_at DESC""",
            (st.session_state.user_id,)
        )
        db.disconnect()
        
        if results:
            for result in results:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(result[1])
                with col2:
                    st.write(f"{result[2]:.2f}/{100}")
                with col3:
                    st.write(f"{result[3]:.2f}%")
                with col4:
                    st.write(f"Grade: **{result[4]}**")
                with col5:
                    status = "✓ PASS" if result[5] else "✗ FAIL"
                    st.write(status)
                st.divider()
        else:
            st.info("No results available yet.")

def show_faculty_dashboard():
    """Faculty dashboard"""
    show_header()
    
    st.markdown(f"### Welcome, {st.session_state.username}!")
    
    tab1, tab2, tab3 = st.tabs(["📋 My Tests", "📊 Analytics", "👥 Students"])
    
    with tab1:
        st.markdown("#### Create/Manage Tests")
        if st.button("+ Create New Test"):
            st.session_state.page = "create_test"
    
    with tab2:
        st.markdown("#### Test Analytics")
        st.info("Analytics dashboard coming soon")
    
    with tab3:
        st.markdown("#### View Students")
        st.info("Student management coming soon")

def show_admin_dashboard():
    """Admin dashboard"""
    show_header()
    
    st.markdown(f"### 👨‍💼 Admin Panel - Welcome, {st.session_state.username}!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "🏫 Departments", "📚 Subjects", "⚙️ Settings"])
    
    with tab1:
        st.markdown("#### User Management")
        if st.button("+ Add New User"):
            st.session_state.page = "add_user"
        
        # List users
        db = Database()
        if db.connect():
            users = db.fetch_all(
                "SELECT user_id, username, full_name, role, email, is_active FROM users LIMIT 20"
            )
            db.disconnect()
            
            if users:
                for user in users:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.write(user[1])
                    with col2:
                        st.write(user[2])
                    with col3:
                        st.write(user[3])
                    with col4:
                        status = "✓ Active" if user[5] else "✗ Inactive"
                        st.write(status)
                    with col5:
                        if st.button("Edit", key=f"edit_user_{user[0]}"):
                            st.session_state.page = "edit_user"
    
    with tab2:
        st.markdown("#### Department Management")
        st.info("Department management coming soon")
    
    with tab3:
        st.markdown("#### Subject Management")
        st.info("Subject management coming soon")
    
    with tab4:
        st.markdown("#### System Settings")
        st.info("Settings coming soon")

def show_logout():
    """Logout button and session management"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Logged in as:** {st.session_state.username}")
    with col2:
        if st.button("🚪 Logout"):
            auth = get_auth()
            auth.logout_user(st.session_state.session_token)
            st.session_state.session_token = None
            st.session_state.user_id = None
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()

# Main app logic
if st.session_state.session_token is None:
    show_login()
else:
    # Verify session
    auth = get_auth()
    if not auth.db.connect():
        st.error("Database connection failed")
    else:
        session_valid = auth.db.fetch_one(
            "SELECT is_active FROM sessions WHERE session_token = %s",
            (st.session_state.session_token,)
        )
        auth.db.disconnect()
        
        if not session_valid or not session_valid[0]:
            st.error("Session expired. Please login again.")
            st.session_state.session_token = None
            st.rerun()
        else:
            with st.sidebar:
                st.divider()
                show_logout()
                st.divider()
            
            show_main()
