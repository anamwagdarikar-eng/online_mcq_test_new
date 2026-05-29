import bcrypt
import jwt
import datetime
from config import SECRET_KEY, MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION
from database import Database
import hmac
import hashlib

class Auth:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def register_user(self, username, email, password, full_name, role, department=None, semester=None):
        """Register new user"""
        if not self.db.connect():
            return {"success": False, "message": "Database connection failed"}

        try:
            # Check if user already exists
            existing = self.db.fetch_one(
                "SELECT user_id FROM users WHERE email = %s OR username = %s",
                (email, username)
            )
            if existing:
                return {"success": False, "message": "User already exists"}

            # Hash password
            password_hash = self.hash_password(password)

            # Insert user
            self.db.execute_query(
                """INSERT INTO users (username, email, password_hash, full_name, role, department, semester) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (username, email, password_hash, full_name, role, department, semester)
            )
            
            self.db.disconnect()
            return {"success": True, "message": "User registered successfully"}
        except Exception as e:
            self.db.disconnect()
            return {"success": False, "message": str(e)}

    def login_user(self, username, password, ip_address):
        """Login user"""
        if not self.db.connect():
            return {"success": False, "message": "Database connection failed"}

        try:
            # Check login attempts
            attempts = self.db.fetch_one(
                """SELECT COUNT(*) FROM login_attempts 
                   WHERE username = %s AND attempted_at > NOW() - INTERVAL '15 minutes' AND successful = FALSE""",
                (username,)
            )
            
            if attempts and attempts[0] >= MAX_LOGIN_ATTEMPTS:
                self.db.disconnect()
                return {"success": False, "message": "Too many login attempts. Try again later"}

            # Get user by username or email
            user = self.db.fetch_one(
                """SELECT user_id, username, password_hash, role, is_active 
                   FROM users WHERE username = %s OR email = %s""",
                (username, username)
            )

            if not user:
                self.db.execute_query(
                    "INSERT INTO login_attempts (username, ip_address, successful) VALUES (%s, %s, FALSE)",
                    (username, ip_address)
                )
                self.db.disconnect()
                return {"success": False, "message": "Invalid credentials"}

            user_id, user_name, password_hash, role, is_active = user

            # Check if user is active
            if not is_active:
                self.db.disconnect()
                return {"success": False, "message": "User account is inactive"}

            # Verify password
            if not self.verify_password(password, password_hash):
                self.db.execute_query(
                    "INSERT INTO login_attempts (username, ip_address, successful) VALUES (%s, %s, FALSE)",
                    (username, ip_address)
                )
                self.db.disconnect()
                return {"success": False, "message": "Invalid credentials"}

            # Create session
            session_token = self.create_session(user_id, ip_address)
            
            # Log successful login
            self.db.execute_query(
                "INSERT INTO login_attempts (username, ip_address, successful) VALUES (%s, %s, TRUE)",
                (username, ip_address)
            )

            # Update last login
            self.db.execute_query(
                "UPDATE users SET last_login = NOW() WHERE user_id = %s",
                (user_id,)
            )

            self.db.disconnect()
            return {
                "success": True,
                "message": "Login successful",
                "user_id": user_id,
                "username": user_name,
                "role": role,
                "session_token": session_token
            }
        except Exception as e:
            self.db.disconnect()
            return {"success": False, "message": str(e)}

    def create_session(self, user_id, ip_address, device_id=None):
        """Create user session"""
        try:
            # Generate session token
            payload = {
                'user_id': user_id,
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            session_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

            # Store session in database
            self.db.execute_query(
                """INSERT INTO sessions (user_id, session_token, ip_address, device_id, is_active) 
                   VALUES (%s, %s, %s, %s, TRUE)""",
                (user_id, session_token, ip_address, device_id)
            )

            return session_token
        except Exception as e:
            print(f"Error creating session: {e}")
            return None

    def verify_session(self, session_token):
        """Verify session token"""
        try:
            payload = jwt.decode(session_token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']

            # Check if session exists and is active
            session = self.db.fetch_one(
                "SELECT session_id FROM sessions WHERE session_token = %s AND is_active = TRUE",
                (session_token,)
            )

            if session:
                # Update last activity
                self.db.execute_query(
                    "UPDATE sessions SET last_activity = NOW() WHERE session_token = %s",
                    (session_token,)
                )
                return {"success": True, "user_id": user_id}
            else:
                return {"success": False, "message": "Invalid session"}
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Session expired"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def logout_user(self, session_token):
        """Logout user"""
        if not self.db.connect():
            return {"success": False}

        try:
            self.db.execute_query(
                "UPDATE sessions SET is_active = FALSE WHERE session_token = %s",
                (session_token,)
            )
            self.db.disconnect()
            return {"success": True}
        except Exception as e:
            self.db.disconnect()
            return {"success": False}

    def get_user(self, user_id):
        """Get user details"""
        if not self.db.connect():
            return None

        try:
            user = self.db.fetch_one(
                """SELECT user_id, username, email, full_name, role, department, semester, 
                          phone, profile_image, is_active, last_login FROM users WHERE user_id = %s""",
                (user_id,)
            )
            self.db.disconnect()
            return user
        except Exception as e:
            self.db.disconnect()
            return None

# Global auth instance
auth = Auth()

def get_auth():
    """Get auth instance"""
    return auth
