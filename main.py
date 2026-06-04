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
import pandas as pd
from datetime import datetime, timedelta, timezone

from config import APP_NAME, COLLEGE_NAME, ACADEMIC_YEAR, SESSION_TIMEOUT, AUTO_SUBMIT_ON_TIMEOUT, ENABLE_WEBCAM_INTEGRATION
from utils.auth import get_auth
from utils.security import get_security
from utils.test_management import get_test_management
from database import Database

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def ensure_database_ready():
    """Ensure the application database schema exists and seed default data."""
    db = Database()
    if not db.connect():
        return False, (
            "Database connection failed. "
            "Check Streamlit Cloud DATABASE_URL and NEON_CONNECTION_STRING settings."
        )
    try:
        if not db.table_exists("users"):
            db.disconnect()
            initializer = Database()
            if not initializer.init_database():
                return False, (
                    "Database schema initialization failed. "
                    "Check the database connection and permissions."
                )
            from seed_data import seed_sample_data
            if not seed_sample_data():
                return False, (
                    "Sample data seeding failed. "
                    "Verify your database connection and try again."
                )
            return True, "Database schema created and default users seeded."
        # Apply schema updates for existing databases
        db.execute_query("ALTER TABLE tests ADD COLUMN IF NOT EXISTS allowed_ips TEXT;")
        db.execute_query("ALTER TABLE tests ADD COLUMN IF NOT EXISTS access_password_hash VARCHAR(255);")
        return True, ""
    finally:
        db.disconnect()

ready, ready_message = ensure_database_ready()
if not ready:
    st.error(ready_message)

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
    .timer-clock {
        display: inline-block;
        background: #1f2937;
        color: #f8fafc;
        font-family: 'Courier New', Courier, monospace;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        letter-spacing: 0.1em;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    .timer-clock .timer-label {
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .timer-clock .timer-value {
        font-size: 42px;
        font-weight: 700;
    }
    .timer-warning {
        color: #d97706;
        font-weight: bold;
    }
    .timer-normal {
        color: #10b981;
        font-weight: bold;
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
if 'department' not in st.session_state:
    st.session_state.department = None
if 'semester' not in st.session_state:
    st.session_state.semester = None
if 'current_test' not in st.session_state:
    st.session_state.current_test = None
if 'attempt_id' not in st.session_state:
    st.session_state.attempt_id = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration_minutes' not in st.session_state:
    st.session_state.duration_minutes = None
if 'test_attempt_started' not in st.session_state:
    st.session_state.test_attempt_started = False

WEBCAM_AVAILABLE = hasattr(st, 'camera_input')

def render_webcam_proctoring():
    """Render webcam proctoring panel for students."""
    if not ENABLE_WEBCAM_INTEGRATION:
        return False

    if not WEBCAM_AVAILABLE:
        st.warning("⚠️ Webcam proctoring is enabled but not supported in this browser.")
        return False

    picture = st.camera_input("📹 Webcam Proctoring - Please allow camera access.", key="webcam_proctoring")
    if picture is not None:
        st.image(picture, caption="Webcam feed captured", use_column_width=True)
        st.success("✓ Webcam proctoring active")
        return True

    st.info("Please allow camera access for webcam monitoring. If your webcam is not detected, refresh the page and allow browser access.")
    return False

IST_ZONE = timezone(timedelta(hours=5, minutes=30))

def convert_to_ist(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        # Try ISO first, then fall back to common DB string format
        parsed = None
        try:
            parsed = datetime.fromisoformat(dt)
        except ValueError:
            try:
                parsed = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None
        dt = parsed
    # If datetime is naive (no tzinfo) assume it's stored in IST (database TIMESTAMP)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=IST_ZONE)
    return dt.astimezone(IST_ZONE)


def format_ist(dt):
    dt = convert_to_ist(dt)
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S IST")


def get_client_ip():
    forwarded = os.environ.get("HTTP_X_FORWARDED_FOR") or os.environ.get("HTTP_CLIENT_IP")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = os.environ.get("HTTP_X_REAL_IP")
    if real_ip:
        return real_ip.strip()
    return "127.0.0.1"


def is_ip_allowed(allowed_ips, ip_address):
    if not allowed_ips:
        return True
    allowed = [ip.strip() for ip in str(allowed_ips).split(",") if ip.strip()]
    return ip_address in allowed


def validate_four_digit_pin(pin):
    return isinstance(pin, str) and pin.isdigit() and len(pin) == 4


def get_student_test_attempt_status(test_id, student_id):
    db = Database()
    if not db.connect():
        return None
    attempt = db.fetch_one(
        """SELECT status FROM test_attempts
           WHERE test_id = %s AND student_id = %s
           ORDER BY attempt_id DESC LIMIT 1""",
        (test_id, student_id)
    )
    db.disconnect()
    return attempt[0] if attempt else None


def get_in_progress_attempt(test_id, student_id):
    db = Database()
    if not db.connect():
        return None
    attempt = db.fetch_one(
        """SELECT attempt_id, start_time FROM test_attempts
           WHERE test_id = %s AND student_id = %s AND status = 'in_progress'
           ORDER BY attempt_id DESC LIMIT 1""",
        (test_id, student_id)
    )
    db.disconnect()
    if not attempt:
        return None
    return {'attempt_id': attempt[0], 'start_time': attempt[1]}


def fetch_available_tests_for_student(department, semester, student_ip):
    db = Database()
    if not db.connect():
        return [], []
    # Fetch published tests first (don't rely on DB NOW() to avoid timezone issues)
    if department and semester is not None:
        tests = db.fetch_all(
            """SELECT t.test_id, t.test_name, t.subject_id, t.duration_minutes, t.total_marks,
                          t.start_time, t.end_time, t.allowed_ips, d.dept_name, d.dept_code, s.semester
               FROM tests t
               JOIN subjects s ON t.subject_id = s.subject_id
               JOIN departments d ON t.dept_id = d.dept_id
               WHERE t.is_published = TRUE
                 AND (
                     regexp_replace(LOWER(regexp_replace(d.dept_name, '&', 'and', 'g')), '[^a-z0-9]+', '', 'g') = regexp_replace(LOWER(regexp_replace(%s, '&', 'and', 'g')), '[^a-z0-9]+', '', 'g')
                     OR LOWER(d.dept_code) = LOWER(%s)
                 )
                 AND s.semester = %s
               ORDER BY t.start_time""",
            (department, department, semester)
        )
    else:
        tests = db.fetch_all(
            """SELECT t.test_id, t.test_name, t.subject_id, t.duration_minutes, t.total_marks,
                          t.start_time, t.end_time, t.allowed_ips, NULL AS dept_name, NULL AS dept_code, NULL AS semester
               FROM tests t
               WHERE t.is_published = TRUE
               ORDER BY t.start_time"""
        )
    db.disconnect()

    # Time-based filtering: convert DB timestamps to IST and decide availability here
    now = datetime.now(IST_ZONE)
    time_filtered = []
    for test in tests:
        start_time = test[5]
        end_time = test[6]
        try:
            start_ist = convert_to_ist(start_time) if start_time else None
        except Exception:
            start_ist = None
        try:
            end_ist = convert_to_ist(end_time) if end_time else None
        except Exception:
            end_ist = None

        # Include tests that are currently live or scheduled for the future
        if (start_ist and end_ist and start_ist <= now <= end_ist) or (start_ist and start_ist > now):
            time_filtered.append(test)

    accessible_tests = [test for test in time_filtered if is_ip_allowed(test[7], student_ip)]
    # Return accessible tests and the time-filtered set for diagnostics
    return accessible_tests, time_filtered


def get_time_remaining():
    try:
        if not st.session_state.get('start_time') or not st.session_state.get('duration_minutes'):
            return None
        start_time = st.session_state.start_time
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time)
            except ValueError:
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=IST_ZONE)
        else:
            start_time = start_time.astimezone(IST_ZONE)

        elapsed = (datetime.now(IST_ZONE) - start_time).total_seconds()
        remaining = st.session_state.duration_minutes * 60 - elapsed
        return max(0, remaining)
    except Exception as e:
        return None


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def render_timer():
    remaining = get_time_remaining()
    if remaining is None:
        return None

    timer_element_id = f"timer_value_{st.session_state.get('current_test', 'test')}"
    timer_html = f"""
    <div class='timer-clock'>
        <div class='timer-label'>⏱️ Time Remaining</div>
        <div class='timer-value' id='{timer_element_id}'>{format_time(remaining)}</div>
    </div>
    <script>
    (function() {{
        const elementId = '{timer_element_id}';
        const element = document.getElementById(elementId);
        if (!element) return;
        
        let remainingSeconds = {int(remaining)};
        const pad = (value) => String(value).padStart(2, '0');
        
        const updateTimer = () => {{
            if (remainingSeconds <= 0) {{
                element.textContent = '00:00:00';
                element.parentElement.style.color = '#ef4444';
                setTimeout(() => window.location.reload(), 500);
                return;
            }}
            const hours = Math.floor(remainingSeconds / 3600);
            const minutes = Math.floor((remainingSeconds % 3600) / 60);
            const seconds = remainingSeconds % 60;
            element.textContent = `${{pad(hours)}}:${{pad(minutes)}}:${{pad(seconds)}}`;
            
            if (remainingSeconds < 300) {{
                element.parentElement.style.color = '#d97706';
            }}
            remainingSeconds -= 1;
        }};
        
        updateTimer();
        const timerInterval = setInterval(updateTimer, 1000);
        
        window.addEventListener('beforeunload', () => clearInterval(timerInterval));
    }})();
    </script>
    """
    st.markdown(timer_html, unsafe_allow_html=True)
    return remaining


def normalize_semester(value):
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return value


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
            ip_address = get_client_ip()
            
            # Attempt login
            result = auth.login_user(username, password, ip_address)
            
            if result['success']:
                if result['role'] != role:
                    st.error("✗ Selected role does not match your account role.")
                else:
                    st.session_state.session_token = result['session_token']
                    st.session_state.user_id = result['user_id']
                    st.session_state.user_role = result['role']
                    st.session_state.username = result['username']
                    st.session_state.department = result.get('department')
                    st.session_state.semester = result.get('semester')
                    
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
    
    if st.session_state.get('current_test'):
        show_student_test()
        return

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
        student_semester = normalize_semester(st.session_state.semester)
        current_ip = get_client_ip()
        accessible_tests, all_tests = fetch_available_tests_for_student(
            st.session_state.department,
            student_semester,
            current_ip
        )

        if accessible_tests:
            now = datetime.now()
            for test in accessible_tests:
                status = "Upcoming" if test[5] and test[5] > now else "Live"
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{test[1]}** — {status}")
                with col2:
                    st.write(f"⏱️ {test[3]} mins | 📍 {test[4]} marks")
                with col3:
                    test_id = test[0]
                    attempt_status = get_student_test_attempt_status(test_id, st.session_state.user_id)
                    if attempt_status in ('submitted', 'auto_submitted'):
                        st.warning("You have already attempted this test. You can view your score in My Results.")
                    elif attempt_status == 'in_progress':
                        if st.button("Resume Test", key=f"avail_test_{test_id}"):
                            st.session_state.current_test = test_id
                            st.rerun()
                    else:
                        if st.button(f"Start Test", key=f"avail_test_{test_id}"):
                            st.session_state.current_test = test_id
                            st.rerun()
        elif all_tests:
            st.warning("Tests are scheduled, but your current network IP is not authorized for access. Contact the administrator.")
            # Diagnostic details to help debug why tests are not accessible
            st.markdown("**Debug: Why tests are not accessible for you**")
            st.write("- Current user department:", st.session_state.department)
            st.write("- Current user semester:", student_semester)
            st.write("- Your detected IP:", current_ip)
            now_ist = datetime.now(IST_ZONE)
            for test in all_tests:
                start_ist = convert_to_ist(test[5])
                end_ist = convert_to_ist(test[6])
                ip_allowed = is_ip_allowed(test[7], current_ip)
                status = "Upcoming" if start_ist and start_ist > now_ist else ("Live" if start_ist and end_ist and start_ist <= now_ist <= end_ist else ("Ended" if end_ist and end_ist < now_ist else "Unknown"))
                st.write(f"- Test `{test[0]}`: **{test[1]}** — {status}")
                st.write(f"  - Start: {format_ist(start_ist)} | End: {format_ist(end_ist)}")
                st.write(f"  - Allowed IPs (test): {test[7]}")
                st.write(f"  - IP allowed for you: {ip_allowed}")
        else:
            st.info("No tests available at the moment.")

def show_available_tests():
    """Show available tests"""
    st.markdown("### 📝 Available Tests")
    student_semester = normalize_semester(st.session_state.semester)
    current_ip = get_client_ip()
    accessible_tests, all_tests = fetch_available_tests_for_student(
        st.session_state.department,
        student_semester,
        current_ip
    )

    if accessible_tests:
        now = datetime.now()
        for test in accessible_tests:
            status = "Upcoming" if test[5] and test[5] > now else "Live"
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{test[1]}** — {status}")
            with col2:
                st.write(f"⏱️ {test[3]} mins | 📍 {test[4]} marks")
            with col3:
                test_id = test[0]
                attempt_status = get_student_test_attempt_status(test_id, st.session_state.user_id)
                if attempt_status in ('submitted', 'auto_submitted'):
                    st.warning("You have already attempted this test. You can view your score in My Results.")
                elif attempt_status == 'in_progress':
                    if st.button("Resume Test", key=f"avail_test_{test_id}"):
                        st.session_state.current_test = test_id
                        st.rerun()
                else:
                    if st.button(f"Start Test", key=f"avail_test_{test_id}"):
                        st.session_state.current_test = test_id
                        st.rerun()
    elif all_tests:
        st.warning("Tests are scheduled, but your current network IP is not authorized for access. Contact the administrator.")
        # Diagnostic details for debugging
        st.markdown("**Debug: Why tests are not accessible for you**")
        st.write("- Current user department:", st.session_state.department)
        st.write("- Current user semester:", student_semester)
        st.write("- Your detected IP:", current_ip)
        now_ist = datetime.now(IST_ZONE)
        for test in all_tests:
            start_ist = convert_to_ist(test[5])
            end_ist = convert_to_ist(test[6])
            ip_allowed = is_ip_allowed(test[7], current_ip)
            status = "Upcoming" if start_ist and start_ist > now_ist else ("Live" if start_ist and end_ist and start_ist <= now_ist <= end_ist else ("Ended" if end_ist and end_ist < now_ist else "Unknown"))
            st.write(f"- Test `{test[0]}`: **{test[1]}** — {status}")
            st.write(f"  - Start: {format_ist(start_ist)} | End: {format_ist(end_ist)}")
            st.write(f"  - Allowed IPs (test): {test[7]}")
            st.write(f"  - IP allowed for you: {ip_allowed}")
    else:
        st.info("No tests available at the moment.")
def show_student_test():
    """Render the selected student test page"""
    test_id = st.session_state.get('current_test')
    if not test_id:
        st.error("No test selected.")
        return

    db = Database()
    if db.connect():
        test = db.fetch_one(
            "SELECT test_name, total_marks, duration_minutes, start_time, end_time, allowed_ips, access_password_hash FROM tests WHERE test_id = %s",
            (test_id,)
        )
        db.disconnect()
    else:
        test = None

    if not test:
        st.error("Unable to load the selected test.")
        return

    test_name, total_marks, duration_minutes, start_time, end_time, allowed_ips, access_password_hash = test
    st.markdown(f"### 📝 Test: {test_name}")
    st.write(f"Total Marks: {total_marks} | Duration: {duration_minutes} minutes")
    st.write(f"Start Time: {format_ist(start_time)} | End Time: {format_ist(end_time)}")

    if allowed_ips:
        st.info(f"This test is restricted to these IP addresses: {allowed_ips}")
    if access_password_hash:
        st.info("This test requires a 4-digit password provided by the administrator.")

    if ENABLE_WEBCAM_INTEGRATION:
        render_webcam_proctoring()

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_test = None
        st.session_state.test_attempt_started = False
        st.session_state.attempt_id = None
        st.session_state.responses = {}
        st.rerun()

    if not st.session_state.test_attempt_started:
        attempt_status = get_student_test_attempt_status(test_id, st.session_state.user_id)
        if attempt_status in ('submitted', 'auto_submitted'):
            st.warning("You have already attempted this test. You cannot retake it.")
            if st.button("Return to Dashboard"):
                st.session_state.current_test = None
                st.session_state.page = None
                st.rerun()
            return

        in_progress = get_in_progress_attempt(test_id, st.session_state.user_id)
        if in_progress:
            st.info("✅ Resuming your in-progress attempt. Keep your webcam enabled and finish the test.")
            st.session_state.attempt_id = in_progress['attempt_id']
            st.session_state.start_time = in_progress['start_time']
            st.session_state.duration_minutes = duration_minutes
            st.session_state.test_attempt_started = True
            st.rerun()
            return

        current_ip = get_client_ip()
        if not is_ip_allowed(allowed_ips, current_ip):
            st.error("Your current network IP is not authorized to access this test. Contact the admin for access.")
            return

        if access_password_hash:
            with st.form("start_test_form"):
                entered_password = st.text_input("Enter 4-digit test password", type="password")
                start = st.form_submit_button("Start Test", use_container_width=True)

            if start:
                if not validate_four_digit_pin(entered_password):
                    st.error("Please enter the 4-digit test password provided by your admin.")
                elif not get_auth().verify_password(entered_password, access_password_hash):
                    st.error("Incorrect test password. Please check with your administrator.")
                else:
                    test_mgmt = get_test_management()
                    attempt = test_mgmt.start_test_attempt(
                        test_id,
                        st.session_state.user_id,
                        current_ip,
                        "streamlit"
                    )
                    if attempt:
                        st.session_state.attempt_id = attempt['attempt_id']
                        st.session_state.duration_minutes = attempt['duration_minutes']
                        st.session_state.start_time = attempt['start_time']
                        st.session_state.test_attempt_started = True
                        st.success("✓ Test attempt started")
                        st.rerun()
                    else:
                        st.error("Unable to start the test attempt. Please contact admin.")
        else:
            if st.button("Start Test", use_container_width=True):
                test_mgmt = get_test_management()
                attempt = test_mgmt.start_test_attempt(
                    test_id,
                    st.session_state.user_id,
                    current_ip,
                    "streamlit"
                )
                if attempt:
                    st.session_state.attempt_id = attempt['attempt_id']
                    st.session_state.duration_minutes = attempt['duration_minutes']
                    st.session_state.start_time = attempt['start_time']
                    st.session_state.test_attempt_started = True
                    st.success("✓ Test attempt started")
                    st.rerun()
                else:
                    st.error("Unable to start the test attempt. Please contact admin.")
        return

    test_mgmt = get_test_management()
    questions = test_mgmt.get_test_questions(test_id, randomize=True)
    if not questions:
        st.info("No questions are configured for this test yet.")
        return

    remaining_time = render_timer()
    
    # Check if time has expired and auto-submit
    if remaining_time is not None and remaining_time <= 0:
        if AUTO_SUBMIT_ON_TIMEOUT:
            st.warning("⏱️ Time's up! Auto-submitting your test...")
            result = test_mgmt.submit_test(test_id, st.session_state.user_id)
            if result.get('success'):
                output = result['results']
                st.success("✓ Test auto-submitted successfully.")
                st.markdown(f"**Score:** {output['marks_obtained']:.2f} / {output['total_marks']}")
                st.markdown(f"**Grade:** {output['grade']} | **Percentage:** {output['percentage']}%")
                st.session_state.current_test = None
                st.session_state.test_attempt_started = False
                st.session_state.attempt_id = None
                st.session_state.responses = {}
            else:
                st.error("Unable to auto-submit the test. Please contact support.")
        return

    if 'student_current_question' not in st.session_state:
        st.session_state.student_current_question = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    current_index = st.session_state.student_current_question
    if current_index < 0:
        st.session_state.student_current_question = 0
        current_index = 0
    if current_index >= len(questions):
        st.session_state.student_current_question = len(questions) - 1
        current_index = len(questions) - 1

    question = questions[current_index]
    st.markdown(f"#### Question {current_index + 1} of {len(questions)}")
    st.write(question['question_text'])
    answer = st.radio(
        "Choose your answer:",
        list(question['options'].keys()),
        index=list(question['options'].keys()).index(st.session_state.responses.get(current_index, list(question['options'].keys())[0])) if st.session_state.responses.get(current_index) else 0,
        key=f"question_{current_index}_answer"
    )

    st.session_state.responses[current_index] = answer

    if st.button("Save Answer", key=f"save_answer_{current_index}"):
        test_mgmt.submit_response(test_id, st.session_state.user_id, question['question_id'], answer)
        st.success("Answer saved")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous") and current_index > 0:
            st.session_state.student_current_question -= 1
            st.rerun()
    with col2:
        if st.button("Next ➡️") and current_index < len(questions) - 1:
            st.session_state.student_current_question += 1
            st.rerun()
    with col3:
        if st.button("✅ Submit Test", use_container_width=True):
            result = test_mgmt.submit_test(test_id, st.session_state.user_id)
            if result.get('success'):
                st.success("✓ Test submitted successfully")
                output = result['results']
                st.markdown(f"**Score:** {output['marks_obtained']:.2f} / {output['total_marks']}")
                st.markdown(f"**Grade:** {output['grade']} | **Percentage:** {output['percentage']}%")
                st.session_state.current_test = None
                st.session_state.test_attempt_started = False
                st.session_state.attempt_id = None
                st.session_state.responses = {}
            else:
                st.error("Unable to submit the test")


def show_my_results():
    """Student results page"""
    st.markdown("### 📊 My Results")
    db = Database()
    if db.connect():
        results = db.fetch_all(
            """SELECT tr.test_id, t.test_name, tr.marks_obtained, tr.percentage, tr.grade, tr.passed, tr.created_at
               FROM test_results tr
               JOIN tests t ON tr.test_id = t.test_id
               WHERE tr.student_id = %s
               ORDER BY tr.created_at DESC""",
            (st.session_state.user_id,)
        )
        db.disconnect()
    else:
        results = []

    if results:
        for row in results:
            status = "✓ PASS" if row[5] else "✗ FAIL"
            st.write(f"**{row[1]}** — {row[2]:.2f} marks — {row[3]:.2f}% — {row[4]} — {status}")
    else:
        st.info("No results found. Take a test to generate your first result.")


def show_create_test():
    """Faculty/admin create test"""
    st.markdown("### 📝 Create New Test")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = None

    db = Database()
    if db.connect():
        subjects = db.fetch_all("SELECT subject_id, subject_name, dept_id, semester FROM subjects")
        db.disconnect()
        subject_details = {s[0]: {'name': s[1], 'dept_id': s[2], 'semester': s[3]} for s in subjects}
        subject_options = {f"{s[1]} (Sem {s[3]})": s[0] for s in subjects}
    else:
        subject_options = {}
        subject_details = {}

    with st.form("create_test_form"):
        test_name = st.text_input("Test Name *")
        subject_name = st.selectbox("Subject *", list(subject_options.keys()) if subject_options else [])
        subject_id = subject_options.get(subject_name)
        subject_meta = subject_details.get(subject_id, {})
        dept_id = subject_meta.get('dept_id', 1)
        subject_semester = subject_meta.get('semester')
        total_marks = st.number_input("Total Marks", min_value=10, max_value=1000, value=100)
        duration = st.number_input("Duration (minutes)", min_value=15, max_value=480, value=60)
        default_passing = min(40, total_marks)
        passing_marks = st.number_input(
            "Passing Marks",
            min_value=0,
            max_value=total_marks,
            value=default_passing,
        )
        start_date = st.date_input("Start Date")
        start_time = st.time_input("Start Time")
        end_date = st.date_input("End Date")
        end_time = st.time_input("End Time")
        negative_marking = st.checkbox("Negative Marking", value=True)
        randomize_q = st.checkbox("Randomize Questions", value=True)
        randomize_opt = st.checkbox("Randomize Options", value=True)
        allowed_ips = st.text_input(
            "Allowed IP Addresses",
            placeholder="Comma-separated IP addresses allowed to access this test",
        )
        password_pin = st.text_input("Test Password (4 digits)", type="password")

        if st.form_submit_button("Create Test", use_container_width=True):
            if test_name and subject_id:
                if password_pin and not validate_four_digit_pin(password_pin):
                    st.error("Test password must be exactly 4 numeric digits.")
                else:
                    start_datetime = datetime.combine(start_date, start_time)
                    end_datetime = datetime.combine(end_date, end_time)
                    password_hash = get_auth().hash_password(password_pin) if password_pin else None
                    db = Database()
                    if db.connect():
                        db.execute_query(
                            """INSERT INTO tests (test_name, subject_id, dept_id, created_by, total_marks,
                               duration_minutes, passing_marks, negative_marking_enabled, randomize_questions,
                               randomize_options, allowed_ips, access_password_hash, start_time, end_time, is_published, show_results)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, TRUE)""",
                            (test_name, subject_id, dept_id, st.session_state.user_id,
                             total_marks, duration, passing_marks, negative_marking,
                             randomize_q, randomize_opt, allowed_ips, password_hash,
                             start_datetime, end_datetime)
                        )
                        db.disconnect()
                        st.success("✓ Test created and published automatically. Students can now see it if timing and branch match.")
                        st.session_state.page = None
            else:
                st.error("Please fill required fields")


def show_add_user():
    """Admin add new user"""
    st.markdown("### ➕ Add New User")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = None

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
                    st.session_state.page = None
                else:
                    st.error(f"Error: {result['message']}")
            else:
                st.error("Please fill required fields")


def show_edit_user():
    """Admin edit existing user"""
    user_id = st.session_state.get('edit_user_id')
    if not user_id:
        st.error("No user selected for editing")
        return

    st.markdown("### ✏️ Edit User")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = None
        st.session_state.edit_user_id = None

    db = Database()
    if db.connect():
        user = db.fetch_one(
            "SELECT username, email, full_name, role, department, semester, is_active FROM users WHERE user_id = %s",
            (user_id,)
        )
        db.disconnect()
    else:
        user = None

    if not user:
        st.error("Unable to load selected user.")
        return

    username, email, full_name, role, department, semester, is_active = user

    with st.form("edit_user_form"):
        new_username = st.text_input("Username *", value=username)
        new_email = st.text_input("Email *", value=email)
        new_full_name = st.text_input("Full Name *", value=full_name)
        new_role = st.selectbox("Role", ["student", "faculty", "admin"], index=["student", "faculty", "admin"].index(role))
        new_department = st.text_input("Department", value=department or "")
        new_semester = st.number_input("Semester", min_value=1, max_value=8, value=int(semester) if semester else 1)
        active = st.checkbox("Active User", value=is_active)

        if st.form_submit_button("Update User", use_container_width=True):
            db = Database()
            if db.connect():
                db.execute_query(
                    """UPDATE users SET username = %s, email = %s, full_name = %s, role = %s,
                       department = %s, semester = %s, is_active = %s WHERE user_id = %s""",
                    (new_username, new_email, new_full_name, new_role,
                     new_department, new_semester, active, user_id)
                )
                db.disconnect()
                st.success("✓ User updated successfully!")
                st.session_state.page = None
                st.session_state.edit_user_id = None
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


def show_admin_departments():
    st.markdown("#### Department Management")
    db = Database()
    if db.connect():
        departments = db.fetch_all(
            "SELECT dept_id, dept_name, dept_code, created_at FROM departments ORDER BY dept_name"
        )
        db.disconnect()
    else:
        departments = []

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("##### Add New Department")
        with st.form("add_department_form"):
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
                        st.success("✓ Department added successfully")
                        st.rerun()
                else:
                    st.error("Please fill in both fields")

    with col2:
        st.markdown("##### Existing Departments")
        if departments:
            for dept in departments:
                col_d1, col_d2 = st.columns([4, 1])
                with col_d1:
                    st.write(f"**{dept[1]}** ({dept[2]})")
                with col_d2:
                    if st.button("Delete", key=f"delete_dept_{dept[0]}"):
                        db = Database()
                        if db.connect():
                            db.execute_query("DELETE FROM departments WHERE dept_id = %s", (dept[0],))
                            db.disconnect()
                        st.success("✓ Department deleted")
                        st.rerun()
        else:
            st.info("No departments defined yet")


def show_admin_subjects():
    st.markdown("#### Subject Management")
    db = Database()
    if db.connect():
        departments = db.fetch_all("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
        subjects = db.fetch_all(
            """SELECT s.subject_id, s.subject_name, s.subject_code, d.dept_name, s.semester
               FROM subjects s
               JOIN departments d ON s.dept_id = d.dept_id
               ORDER BY s.subject_name"""
        )
        db.disconnect()
    else:
        departments = []
        subjects = []

    dept_options = {dept[1]: dept[0] for dept in departments}

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("##### Add New Subject")
        with st.form("add_subject_form"):
            subject_name = st.text_input("Subject Name *")
            subject_code = st.text_input("Subject Code *")
            department_name = st.selectbox(
                "Department *",
                list(dept_options.keys()) if dept_options else ["No departments available"]
            )
            semester = st.number_input("Semester", min_value=1, max_value=8, value=1)
            if st.form_submit_button("Add Subject", use_container_width=True):
                if subject_name and subject_code and department_name and department_name in dept_options:
                    db = Database()
                    if db.connect():
                        db.execute_query(
                            "INSERT INTO subjects (subject_name, subject_code, dept_id, semester) VALUES (%s, %s, %s, %s)",
                            (subject_name, subject_code, dept_options[department_name], semester)
                        )
                        db.disconnect()
                        st.success("✓ Subject added successfully")
                        st.rerun()
                else:
                    st.error("Please select a valid department and enter the subject details")

    with col2:
        st.markdown("##### Existing Subjects")
        if subjects:
            for subj in subjects:
                col_s1, col_s2 = st.columns([4, 1])
                with col_s1:
                    st.write(f"**{subj[1]}** ({subj[2]}) — {subj[3]} | Semester {subj[4]}")
                with col_s2:
                    if st.button("Delete", key=f"delete_subj_{subj[0]}"):
                        db = Database()
                        if db.connect():
                            db.execute_query("DELETE FROM subjects WHERE subject_id = %s", (subj[0],))
                            db.disconnect()
                        st.success("✓ Subject deleted")
                        st.rerun()
        else:
            st.info("No subjects defined yet")


def show_admin_settings():
    st.markdown("#### System Settings")
    st.write("**College:**", COLLEGE_NAME)
    st.write("**Academic Year:**", ACADEMIC_YEAR)
    st.write("**App Name:**", APP_NAME)

    db = Database()
    counts = {}
    if db.connect():
        counts['users'] = db.fetch_one("SELECT COUNT(*) FROM users")[0]
        counts['departments'] = db.fetch_one("SELECT COUNT(*) FROM departments")[0]
        counts['subjects'] = db.fetch_one("SELECT COUNT(*) FROM subjects")[0]
        counts['tests'] = db.fetch_one("SELECT COUNT(*) FROM tests")[0]
        db.disconnect()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Users", counts.get('users', 0))
    with col2:
        st.metric("Departments", counts.get('departments', 0))
    with col3:
        st.metric("Subjects", counts.get('subjects', 0))
    with col4:
        st.metric("Tests", counts.get('tests', 0))

    st.markdown("---")
    st.info("Use the other tabs to manage users, departments, subjects, and tests.")


def show_faculty_analytics():
    st.markdown("#### Test Analytics")
    db = Database()
    if db.connect():
        if st.session_state.user_role == 'admin':
            tests = db.fetch_all("SELECT test_id, test_name FROM tests ORDER BY created_at DESC LIMIT 20")
        else:
            tests = db.fetch_all(
                "SELECT test_id, test_name FROM tests WHERE created_by = %s ORDER BY created_at DESC LIMIT 20",
                (st.session_state.user_id,)
            )
        db.disconnect()
    else:
        tests = []

    if not tests:
        st.info("No tests available yet.")
        return

    test_map = {test[1]: test[0] for test in tests}
    selected_test = st.selectbox("Select Test", list(test_map.keys()))
    test_id = test_map[selected_test]

    db = Database()
    if db.connect():
        stats = db.fetch_one(
            "SELECT COUNT(*), COALESCE(AVG(marks_obtained), 0), SUM(CASE WHEN passed THEN 1 ELSE 0 END) FROM test_results WHERE test_id = %s",
            (test_id,)
        )
        results = db.fetch_all(
            """SELECT u.full_name, tr.marks_obtained, tr.percentage, tr.grade, tr.passed
               FROM test_results tr
               JOIN users u ON tr.student_id = u.user_id
               WHERE tr.test_id = %s
               ORDER BY tr.created_at DESC
               LIMIT 10""",
            (test_id,)
        )
        db.disconnect()
    else:
        stats = (0, 0, 0)
        results = []

    st.metric("Total Attempts", stats[0])
    st.metric("Average Marks", f"{stats[1]:.2f}")
    st.metric("Pass Count", stats[2])

    if results:
        st.markdown("##### Recent Results")
        for row in results:
            status = "✓ PASS" if row[4] else "✗ FAIL"
            st.write(f"{row[0]} — {row[1]:.2f}/100 — {row[3]} — {status}")
    else:
        st.info("No result records found for this test yet.")


def show_faculty_students():
    st.markdown("#### Students")
    db = Database()
    if db.connect():
        students = db.fetch_all(
            "SELECT username, full_name, email, department, semester, is_active FROM users WHERE role = 'student' ORDER BY full_name LIMIT 50"
        )
        db.disconnect()
    else:
        students = []

    if students:
        for student in students:
            status = "Active" if student[5] else "Inactive"
            st.write(f"**{student[1]}** ({student[0]}) — {student[3]} | Sem {student[4]} — {status}")
    else:
        st.info("No students available yet.")


def show_faculty_tests():
    """Display faculty-created tests and publish workflow."""
    st.markdown("#### My Tests")
    st.write("Create tests, then add questions and publish them for students in the matching branch and semester.")

    db = Database()
    if db.connect():
        tests = db.fetch_all(
            """SELECT t.test_id, t.test_name, t.total_marks, t.duration_minutes, t.is_published,
                         t.start_time, t.end_time,
                         (SELECT COUNT(*) FROM test_questions tq WHERE tq.test_id = t.test_id)
                FROM tests t
                WHERE t.created_by = %s
                ORDER BY t.created_at DESC
            """,
            (st.session_state.user_id,)
        )
        db.disconnect()
    else:
        tests = []

    if tests:
        now = datetime.now()
        for test in tests:
            status = "Published" if test[4] else "Draft"
            if test[5] and test[5] > now:
                schedule = f"Starts: {test[5]}"
            else:
                schedule = f"Ends: {test[6]}"

            with st.expander(f"{test[1]} — {status} — {test[7]} questions"):
                st.write(f"Total Marks: {test[2]} | Duration: {test[3]} mins")
                st.write(schedule)
                if test[4]:
                    st.success("This test is published and available for eligible students.")
                else:
                    if test[7] == 0:
                        st.warning("Add questions to this test before it can be published.")
                    else:
                        if st.button("Publish Test", key=f"publish_test_{test[0]}"):
                            db = Database()
                            if db.connect():
                                db.execute_query("UPDATE tests SET is_published = TRUE WHERE test_id = %s", (test[0],))
                                db.disconnect()
                            st.success("✓ Test published successfully")
                            st.rerun()
    else:
        st.info("No tests created yet. Use the Create New Test button above.")


def show_faculty_import_questions():
    """Allow faculty to upload MCQ questions for a subject."""
    st.markdown("#### Import Questions to Test")
    st.info(
        "Upload a CSV with columns: question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level, marks"
    )

    db = Database()
    if db.connect():
        subjects = db.fetch_all("SELECT subject_id, subject_name, dept_id, semester FROM subjects")
        db.disconnect()
    else:
        subjects = []

    subject_options = {f"{s[1]} (Sem {s[3]})": s[0] for s in subjects} if subjects else {}
    
    col1, col2 = st.columns(2)
    with col1:
        subject_name = st.selectbox("Subject *", list(subject_options.keys()) if subject_options else [])
        subject_id = subject_options.get(subject_name)
    
    with col2:
        # Get tests for selected subject
        if subject_id:
            db = Database()
            if db.connect():
                tests = db.fetch_all(
                    """SELECT test_id, test_name FROM tests 
                       WHERE subject_id = %s
                       ORDER BY created_at DESC""",
                    (subject_id,)
                )
                db.disconnect()
                test_options = {f"{t[1]}": t[0] for t in tests} if tests else {}
            else:
                test_options = {}
        else:
            test_options = {}
        
        selected_test_name = st.selectbox("Select Test to Add Questions *", list(test_options.keys()) if test_options else ["No tests available"])
        selected_test_id = test_options.get(selected_test_name)

    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        except Exception as e:
            st.error(f"Unable to read CSV file: {e}")
            return

        if st.button("Import Questions & Add to Test"):
            required_columns = [
                'question_text', 'option_a', 'option_b', 'option_c', 'option_d',
                'correct_answer', 'difficulty_level', 'marks'
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                st.error(f"Missing required columns: {', '.join(missing)}")
                return
            if not subject_id:
                st.error("Select a valid subject before importing questions.")
                return
            if not selected_test_id:
                st.error("Select a test to add questions to.")
                return

            db = Database()
            if not db.connect():
                st.error("Database connection failed.")
                return

            success_count = 0
            error_count = 0
            
            # Get current max question order in test
            max_order = db.fetch_one(
                "SELECT COALESCE(MAX(question_order), 0) FROM test_questions WHERE test_id = %s",
                (selected_test_id,)
            )
            question_order = max_order[0] + 1 if max_order else 1
            
            for _, row in df.iterrows():
                try:
                    # Insert into questions table
                    db.execute_query(
                        """INSERT INTO questions (
                               subject_id, question_text, option_a, option_b, option_c, option_d,
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
                            int(row['marks']),
                            st.session_state.user_id,
                        )
                    )
                    
                    # Get the newly inserted question ID
                    question = db.fetch_one("SELECT LASTVAL();")
                    question_id = question[0] if question else None
                    
                    if question_id:
                        # Add to test_questions table
                        db.execute_query(
                            """INSERT INTO test_questions 
                               (test_id, question_id, question_order, marks, negative_marks)
                               VALUES (%s, %s, %s, %s, %s)""",
                            (
                                selected_test_id,
                                question_id,
                                question_order,
                                int(row['marks']),
                                float(row.get('negative_marks', 0.25))
                            )
                        )
                        question_order += 1
                        success_count += 1
                except Exception:
                    error_count += 1

            db.disconnect()
            st.success(f"✓ Imported and added {success_count} questions to test!")
            st.info(f"📌 Questions are now part of your selected test")
            if error_count:
                st.warning(f"⚠️ {error_count} rows failed to import.")


def show_faculty_dashboard():
    """Faculty dashboard"""
    show_header()
    
    if st.session_state.get('page') == 'create_test':
        show_create_test()
        return

    st.markdown(f"### Welcome, {st.session_state.username}!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 My Tests", "📊 Analytics", "👥 Students", "📤 Import Questions"])
    
    with tab1:
        st.markdown("#### Create/Manage Tests")
        if st.button("+ Create New Test"):
            st.session_state.page = "create_test"
        show_faculty_tests()
    
    with tab2:
        show_faculty_analytics()
    
    with tab3:
        show_faculty_students()
    
    with tab4:
        show_faculty_import_questions()

def show_admin_dashboard():
    """Admin dashboard"""
    show_header()
    
    st.markdown(f"### 👨‍💼 Admin Panel - Welcome, {st.session_state.username}!")
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "🏫 Departments", "📚 Subjects", "⚙️ Settings"])
    
    if st.session_state.get('page') == 'add_user':
        show_add_user()
        return
    elif st.session_state.get('page') == 'edit_user':
        show_edit_user()
        return

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
                            st.session_state.edit_user_id = user[0]
                            st.session_state.page = "edit_user"
    
    with tab2:
        show_admin_departments()
    
    with tab3:
        show_admin_subjects()
    
    with tab4:
        show_admin_settings()

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
