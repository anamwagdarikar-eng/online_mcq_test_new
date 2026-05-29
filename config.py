import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/mcq_db")
NEON_CONNECTION_STRING = os.getenv("NEON_CONNECTION_STRING", DATABASE_URL)

# App Configuration
APP_NAME = "Engineering College MCQ Test System"
APP_VERSION = "1.0.0"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Session Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True") == "True"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Security Configuration
ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "True") == "True"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds

# Test Configuration
AUTO_SUBMIT_ON_TIMEOUT = True
ENABLE_NEGATIVE_MARKING = True
NEGATIVE_MARKING_PERCENTAGE = 0.25  # 25% of positive marks

# Anti-Cheating Configuration
ENABLE_FULLSCREEN = True
ENABLE_TAB_SWITCH_WARNING = True
ENABLE_IP_LOGGING = True
ENABLE_WEBCAM_INTEGRATION = False  # Can be enabled
DISABLE_COPY_PASTE = True
SINGLE_DEVICE_LOGIN = True
MAX_TAB_SWITCHES = 5

# Scalability Configuration
MAX_CONCURRENT_STUDENTS = 5000
BATCH_SIZE = 100

# Email Configuration (optional)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

# College Information (Customize as needed)
DEFAULT_COLLEGE_NAME = "Vidya Vikas Institute of Engineering and Technology, Solapur"
COLLEGE_NAME = DEFAULT_COLLEGE_NAME
COLLEGE_LOGO_PATH = "assets/college_logo.png"

def get_academic_year():
    today = datetime.today()
    year = today.year
    if today.month >= 7:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
    return f"{start_year}-{end_year}"

ACADEMIC_YEAR = get_academic_year()

# Debug Mode
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
