import os
import sys

# CRITICAL: Add project root to Python path FIRST, before any other imports
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now safe to import other modules
import streamlit as st
import time
from datetime import datetime, timedelta

from utils.test_management import get_test_management
from utils.security import get_security
from database import Database
from config import ENABLE_FULLSCREEN, ENABLE_TAB_SWITCH_WARNING, AUTO_SUBMIT_ON_TIMEOUT, ENABLE_WEBCAM_INTEGRATION

# MCQ Question imports and Webcam support
try:
    import cv2
    WEBCAM_AVAILABLE = True
except ImportError:
    WEBCAM_AVAILABLE = False

st.set_page_config(page_title="MCQ Test", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .test-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .timer-warning {
        background-color: #ff6b6b;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .timer-normal {
        background-color: #51cf66;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .question-palette {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 5px;
        margin-bottom: 20px;
    }
    .question-btn {
        padding: 10px;
        border: 2px solid #ddd;
        border-radius: 5px;
        cursor: pointer;
    }
    .question-btn.answered {
        background-color: #51cf66;
        color: white;
        border-color: #51cf66;
    }
    .question-btn.visited {
        background-color: #e7f5ff;
        border-color: #667eea;
    }
    .question-btn.current {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    .option-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.3s;
    }
    .option-container:hover {
        border-color: #667eea;
        background-color: #f0f4ff;
    }
    .option-container.selected {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    .exam-instructions {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Anti-cheating features - Fullscreen
if ENABLE_FULLSCREEN:
    st.markdown("""
    <script>
        function enterFullscreen() {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen().catch(err => console.log('Fullscreen error:', err));
            }
        }
        
        window.addEventListener('load', function() {
            setTimeout(enterFullscreen, 500);
            
            // Warn on exit
            document.addEventListener('fullscreenchange', function() {
                if (!document.fullscreenElement) {
                    alert('⚠️ WARNING: You have exited fullscreen mode. This is recorded as suspicious activity.');
                }
            });
        });
    </script>
    """, unsafe_allow_html=True)

# Session management
if 'test_data' not in st.session_state:
    st.session_state.test_data = None
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'duration_minutes' not in st.session_state:
    st.session_state.duration_minutes = 60
if 'tab_switch_count' not in st.session_state:
    st.session_state.tab_switch_count = 0
if 'warned_tab_switches' not in st.session_state:
    st.session_state.warned_tab_switches = False

def get_time_remaining():
    """Calculate remaining time"""
    if st.session_state.start_time is None:
        return st.session_state.duration_minutes * 60
    
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    remaining = (st.session_state.duration_minutes * 60) - elapsed
    return max(0, remaining)

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def render_timer():
    """Render test timer with auto-submission"""
    remaining = get_time_remaining()
    
    if remaining <= 0:
        st.error("⏱️ Time's up! Test auto-submitted.")
        submit_test()
        st.stop()
    
    # Warning if less than 5 minutes
    if remaining < 300:
        st.markdown(f'<div class="timer-warning">⏰ Time Remaining: {format_time(remaining)}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="timer-normal">⏱️ Time Remaining: {format_time(remaining)}</div>', 
                   unsafe_allow_html=True)
    
    return remaining

def show_exam_instructions():
    """Display exam instructions"""
    st.markdown("""
    <div class="exam-instructions">
    <h4>📋 Exam Instructions</h4>
    <ul>
    <li>Read each question carefully before answering</li>
    <li>You can navigate between questions using the question palette</li>
    <li>Click on an option to select your answer</li>
    <li>Review your answers before submitting</li>
    <li>The test will auto-submit when time expires</li>
    <li>Negative marking is enabled for incorrect answers</li>
    <li>Do not refresh the page or exit fullscreen mode</li>
    <li>Tab switching may result in automatic test submission</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def show_question_palette(questions):
    """Show question navigation palette"""
    cols = st.columns(10)
    for i, col in enumerate(cols):
        if i < len(questions):
            q_id = i + 1
            # Determine button style
            if q_id - 1 in st.session_state.responses:
                btn_class = "question-btn answered"
                label = f"✓{q_id}"
            elif q_id - 1 == st.session_state.current_question_idx:
                btn_class = "question-btn current"
                label = f"●{q_id}"
            else:
                btn_class = "question-btn visited"
                label = str(q_id)
            
            with col:
                if st.button(label, key=f"q_palette_{i}", use_container_width=True):
                    st.session_state.current_question_idx = i

def show_question(question, question_number):
    """Display a single question"""
    st.markdown("---")
    st.markdown(f"### Question {question_number + 1}")
    st.markdown(f"**Marks:** {question['marks']} | **Difficulty:** {question['difficulty']}")
    
    st.markdown(f"#### {question['question_text']}")
    
    # Display options
    selected_option = st.session_state.responses.get(question_number)
    
    options = question.get('options', {})
    for option_key, option_text in options.items():
        if st.button(
            f"**({option_key})** {option_text}",
            key=f"option_{question_number}_{option_key}",
            use_container_width=True
        ):
            st.session_state.responses[question_number] = option_key
            
            # Log response
            test_mgmt = get_test_management()
            test_mgmt.submit_response(
                st.session_state.test_id,
                st.session_state.user_id,
                question['question_id'],
                option_key
            )
            st.rerun()

def init_webcam():
    """Initialize and display webcam feed for proctoring using Streamlit camera input"""
    if not ENABLE_WEBCAM_INTEGRATION:
        return False
    
    if not WEBCAM_AVAILABLE:
        st.warning("⚠️ OpenCV not available. Webcam monitoring disabled.")
        return False
    
    try:
        # Use Streamlit's native camera input
        picture = st.camera_input("📹 Webcam Proctoring - Smile for the camera!")
        
        if picture is not None:
            # Display the captured image
            st.image(picture, caption="Webcam Feed Captured", use_column_width=True)
            st.info("✓ Webcam feed captured and monitored for proctoring")
            return True
    except Exception as e:
        st.warning(f"⚠️ Webcam initialization failed: {str(e)}")
        return False
    
    return False

def enable_webcam_monitoring():
    """Enable webcam monitoring during test"""
    if ENABLE_WEBCAM_INTEGRATION:
        with st.sidebar:
            if st.checkbox("Enable Webcam Proctoring", value=False):
                st.markdown("### 📹 Webcam Proctoring")
                init_webcam()

def import_mcq_questions(test_id):
    """Import MCQ questions for the test"""
    try:
        test_mgmt = get_test_management()
        questions = test_mgmt.get_test_questions(test_id, randomize=True)
        
        if not questions:
            st.error("❌ No questions available for this test")
            return None
        
        st.success(f"✓ Successfully loaded {len(questions)} questions")
        return questions
    except Exception as e:
        st.error(f"❌ Error importing questions: {str(e)}")
        return None

def submit_test():
    """Submit test and calculate results"""
    test_mgmt = get_test_management()
    result = test_mgmt.submit_test(st.session_state.test_id, st.session_state.user_id)
    
    if result['success']:
        results = result['results']
        st.success("✓ Test submitted successfully!")
        
        # Display results
        st.markdown("---")
        st.markdown("### 📊 Test Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Questions", results['total_questions'])
        with col2:
            st.metric("Correct Answers", results['correct_answers'])
        with col3:
            st.metric("Marks Obtained", f"{results['marks_obtained']:.2f}")
        with col4:
            st.metric("Grade", results['grade'])
        
        st.markdown(f"### Score: {results['percentage']:.2f}%")
        
        if results['passed']:
            st.success(f"✓ PASSED - Grade: {results['grade']}")
        else:
            st.error(f"✗ FAILED - Grade: {results['grade']}")
        
        st.session_state.test_completed = True
    else:
        st.error("Error submitting test")

def main():
    """Main test interface"""
    # Check if user is logged in
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.error("Please login first")
        st.stop()
    
    # Get test ID from URL
    if 'test_id' not in st.session_state:
        test_id = st.query_params.get('test_id', None)
        if test_id:
            st.session_state.test_id = int(test_id)
        else:
            st.error("No test selected")
            st.stop()
    
    # Load test data
    test_id = st.session_state.test_id
    
    if st.session_state.test_data is None:
        db = Database()
        if db.connect():
            test = db.fetch_one(
                """SELECT test_name, duration_minutes, total_marks, negative_marking_enabled 
                   FROM tests WHERE test_id = %s""",
                (test_id,)
            )
            db.disconnect()
            
            if test:
                st.session_state.test_data = test
                st.session_state.duration_minutes = test[1]
                st.session_state.start_time = datetime.now()
            else:
                st.error("Test not found")
                st.stop()
    
    # Test header
    st.markdown(f"""
    <div class="test-header">
    <h2>{st.session_state.test_data[0]}</h2>
    <p>Total Marks: {st.session_state.test_data[2]} | Duration: {st.session_state.test_data[1]} minutes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show instructions if first question
    if st.session_state.current_question_idx == 0 and len(st.session_state.responses) == 0:
        show_exam_instructions()
    
    # Enable webcam monitoring if configured
    enable_webcam_monitoring()
    
    # Render timer
    remaining_time = render_timer()
    
    # Load questions using MCQ import function
    questions = import_mcq_questions(test_id)
    
    if not questions:
        st.stop()
    
    # Show question palette
    show_question_palette(questions)
    
    # Show current question
    if 0 <= st.session_state.current_question_idx < len(questions):
        current_q = questions[st.session_state.current_question_idx]
        show_question(current_q, st.session_state.current_question_idx)
    
    # Navigation and submit buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.current_question_idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col2:
        if st.session_state.current_question_idx < len(questions) - 1:
            if st.button("Next ➡️"):
                st.session_state.current_question_idx += 1
                st.rerun()
    
    with col3:
        st.write(f"{st.session_state.current_question_idx + 1}/{len(questions)}")
    
    with col4:
        if st.button("✅ Submit Test", use_container_width=True):
            with st.spinner("Submitting..."):
                submit_test()

if __name__ == "__main__":
    main()
