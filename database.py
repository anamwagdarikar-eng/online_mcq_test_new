import psycopg as psycopg2
from psycopg import sql
import os
from config import NEON_CONNECTION_STRING, DEBUG_MODE

class Database:
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or NEON_CONNECTION_STRING
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            if DEBUG_MODE:
                print("✓ Database connected successfully")
            return True
        except Exception as e:
            if DEBUG_MODE:
                print(f"✗ Database connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def table_exists(self, table_name):
        """Check whether a table exists in the database"""
        should_disconnect = False
        if not self.conn or not self.cursor:
            if not self.connect():
                return False
            should_disconnect = True

        try:
            self.cursor.execute(
                """SELECT EXISTS (
                       SELECT 1 FROM information_schema.tables
                       WHERE table_schema = 'public' AND table_name = %s
                   )""",
                (table_name,)
            )
            result = self.cursor.fetchone()
            return bool(result[0]) if result else False
        except Exception as e:
            if DEBUG_MODE:
                print(f"✗ Table exists check failed: {e}")
            return False
        finally:
            if should_disconnect:
                self.disconnect()

    def execute_query(self, query, params=None):
        """Execute a query"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            if DEBUG_MODE:
                print(f"✗ Query execution failed: {e}")
            return False

    def fetch_one(self, query, params=None):
        """Fetch single row"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        except Exception as e:
            if DEBUG_MODE:
                print(f"✗ Fetch one failed: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch all rows"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            if DEBUG_MODE:
                print(f"✗ Fetch all failed: {e}")
            return []

    def init_database(self):
        """Initialize database schema"""
        if not self.connect():
            return False

        queries = [
            # Users Table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'faculty', 'student')),
                department VARCHAR(100),
                semester VARCHAR(10),
                phone VARCHAR(20),
                profile_image VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
            """,
            
            # Departments Table
            """
            CREATE TABLE IF NOT EXISTS departments (
                dept_id SERIAL PRIMARY KEY,
                dept_name VARCHAR(100) NOT NULL UNIQUE,
                dept_code VARCHAR(20) NOT NULL UNIQUE,
                hod_id INTEGER REFERENCES users(user_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Subjects Table
            """
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id SERIAL PRIMARY KEY,
                subject_name VARCHAR(255) NOT NULL,
                subject_code VARCHAR(20) NOT NULL,
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                semester INTEGER NOT NULL,
                faculty_id INTEGER REFERENCES users(user_id),
                credits INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Course Outcomes (CO)
            """
            CREATE TABLE IF NOT EXISTS course_outcomes (
                co_id SERIAL PRIMARY KEY,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),
                co_code VARCHAR(20) NOT NULL,
                co_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Program Outcomes (PO)
            """
            CREATE TABLE IF NOT EXISTS program_outcomes (
                po_id SERIAL PRIMARY KEY,
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                po_code VARCHAR(20) NOT NULL,
                po_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Questions Table
            """
            CREATE TABLE IF NOT EXISTS questions (
                question_id SERIAL PRIMARY KEY,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),
                co_id INTEGER REFERENCES course_outcomes(co_id),
                question_text TEXT NOT NULL,
                question_type VARCHAR(20) DEFAULT 'MCQ' CHECK (question_type IN ('MCQ', 'MSQ', 'NUMERICAL')),
                difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('Easy', 'Medium', 'Hard')),
                marks INTEGER DEFAULT 1,
                negative_marks DECIMAL(5, 2) DEFAULT 0.25,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_answer VARCHAR(10),
                explanation TEXT,
                created_by INTEGER REFERENCES users(user_id),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Tests/Exams Table
            """
            CREATE TABLE IF NOT EXISTS tests (
                test_id SERIAL PRIMARY KEY,
                test_name VARCHAR(255) NOT NULL,
                subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                created_by INTEGER NOT NULL REFERENCES users(user_id),
                test_description TEXT,
                total_marks INTEGER DEFAULT 100,
                duration_minutes INTEGER DEFAULT 60,
                passing_marks INTEGER DEFAULT 40,
                negative_marking_enabled BOOLEAN DEFAULT TRUE,
                enable_fullscreen BOOLEAN DEFAULT TRUE,
                enable_tab_warnings BOOLEAN DEFAULT TRUE,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                is_published BOOLEAN DEFAULT FALSE,
                show_results BOOLEAN DEFAULT FALSE,
                randomize_questions BOOLEAN DEFAULT TRUE,
                randomize_options BOOLEAN DEFAULT TRUE,
                allowed_ips TEXT,
                access_password_hash VARCHAR(255),
                allow_review BOOLEAN DEFAULT TRUE,
                max_attempts INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Test Questions (Junction Table)
            """
            CREATE TABLE IF NOT EXISTS test_questions (
                test_question_id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL REFERENCES tests(test_id),
                question_id INTEGER NOT NULL REFERENCES questions(question_id),
                question_order INTEGER,
                marks INTEGER,
                negative_marks DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Student Test Responses
            """
            CREATE TABLE IF NOT EXISTS student_responses (
                response_id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL REFERENCES tests(test_id),
                student_id INTEGER NOT NULL REFERENCES users(user_id),
                question_id INTEGER NOT NULL REFERENCES questions(question_id),
                selected_answer VARCHAR(100),
                is_correct BOOLEAN,
                marks_obtained DECIMAL(5, 2) DEFAULT 0,
                time_spent_seconds INTEGER DEFAULT 0,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Test Attempts (to track multiple attempts)
            """
            CREATE TABLE IF NOT EXISTS test_attempts (
                attempt_id SERIAL PRIMARY KEY,
                test_id INTEGER NOT NULL REFERENCES tests(test_id),
                student_id INTEGER NOT NULL REFERENCES users(user_id),
                attempt_number INTEGER DEFAULT 1,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                total_marks_obtained DECIMAL(6, 2) DEFAULT 0,
                total_time_spent_seconds INTEGER DEFAULT 0,
                status VARCHAR(20) CHECK (status IN ('in_progress', 'submitted', 'auto_submitted')),
                tab_switch_count INTEGER DEFAULT 0,
                ip_address VARCHAR(50),
                device_id VARCHAR(255),
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Session Management
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id),
                session_token VARCHAR(500) UNIQUE NOT NULL,
                ip_address VARCHAR(50),
                device_id VARCHAR(255),
                user_agent TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Login Attempts (for security)
            """
            CREATE TABLE IF NOT EXISTS login_attempts (
                attempt_id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                ip_address VARCHAR(50),
                successful BOOLEAN,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Audit Log
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                action VARCHAR(255),
                details TEXT,
                ip_address VARCHAR(50),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Test Results Summary
            """
            CREATE TABLE IF NOT EXISTS test_results (
                result_id SERIAL PRIMARY KEY,
                attempt_id INTEGER NOT NULL REFERENCES test_attempts(attempt_id),
                test_id INTEGER NOT NULL REFERENCES tests(test_id),
                student_id INTEGER NOT NULL REFERENCES users(user_id),
                total_questions INTEGER,
                correct_answers INTEGER,
                incorrect_answers INTEGER,
                unanswered INTEGER,
                total_marks DECIMAL(6, 2),
                marks_obtained DECIMAL(6, 2),
                percentage DECIMAL(5, 2),
                grade VARCHAR(5),
                passed BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # CO-PO Mapping
            """
            CREATE TABLE IF NOT EXISTS co_po_mapping (
                mapping_id SERIAL PRIMARY KEY,
                co_id INTEGER NOT NULL REFERENCES course_outcomes(co_id),
                po_id INTEGER NOT NULL REFERENCES program_outcomes(po_id),
                proficiency_level VARCHAR(10) CHECK (proficiency_level IN ('1', '2', '3')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            "ALTER TABLE tests ADD COLUMN IF NOT EXISTS allowed_ips TEXT;",
            "ALTER TABLE tests ADD COLUMN IF NOT EXISTS access_password_hash VARCHAR(255);",
            
            # Student Registry (for bulk enrollment)
            """
            CREATE TABLE IF NOT EXISTS student_registry (
                registry_id SERIAL PRIMARY KEY,
                roll_number VARCHAR(50) UNIQUE NOT NULL,
                student_id INTEGER REFERENCES users(user_id),
                dept_id INTEGER NOT NULL REFERENCES departments(dept_id),
                semester INTEGER,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Create Indexes for Performance
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
            "CREATE INDEX IF NOT EXISTS idx_questions_subject ON questions(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_tests_subject ON tests(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_student_responses_test ON student_responses(test_id);",
            "CREATE INDEX IF NOT EXISTS idx_student_responses_student ON student_responses(student_id);",
            "CREATE INDEX IF NOT EXISTS idx_test_attempts_student ON test_attempts(student_id);",
            "CREATE INDEX IF NOT EXISTS idx_test_results_student ON test_results(student_id);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);",
        ]

        for query in queries:
            try:
                self.cursor.execute(query)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                if DEBUG_MODE:
                    print(f"Warning: {e}")

        self.disconnect()
        print("✓ Database initialized successfully!")
        return True

# Global database instance
db = Database()

def get_db():
    """Get database instance"""
    return db
