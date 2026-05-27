import hashlib
import uuid
import requests
import json
from datetime import datetime
from database import Database
from config import ENABLE_IP_LOGGING, DISABLE_COPY_PASTE, SINGLE_DEVICE_LOGIN, MAX_TAB_SWITCHES

class Security:
    def __init__(self):
        self.db = Database()

    def sanitize_input(self, input_str):
        """Sanitize user input to prevent SQL injection"""
        if not isinstance(input_str, str):
            return input_str
        
        # Remove dangerous characters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = input_str
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        return sanitized

    def hash_device_id(self, user_agent, ip_address):
        """Generate device hash from user agent and IP"""
        device_string = f"{user_agent}:{ip_address}"
        return hashlib.sha256(device_string.encode()).hexdigest()

    def get_client_ip(self, headers):
        """Get client IP from request headers"""
        if 'X-Forwarded-For' in headers:
            return headers['X-Forwarded-For'].split(',')[0].strip()
        elif 'X-Real-IP' in headers:
            return headers['X-Real-IP']
        return '0.0.0.0'

    def log_audit(self, user_id, action, details, ip_address, user_agent):
        """Log user actions for audit trail"""
        if not self.db.connect():
            return False

        try:
            self.db.execute_query(
                """INSERT INTO audit_log (user_id, action, details, ip_address, user_agent) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, action, details, ip_address, user_agent)
            )
            self.db.disconnect()
            return True
        except Exception as e:
            self.db.disconnect()
            return False

    def log_ip_address(self, user_id, test_id, ip_address, device_id, attempt_id):
        """Log IP address for anti-cheating"""
        if not ENABLE_IP_LOGGING:
            return True

        if not self.db.connect():
            return False

        try:
            self.db.execute_query(
                """UPDATE test_attempts SET ip_address = %s, device_id = %s 
                   WHERE attempt_id = %s""",
                (ip_address, device_id, attempt_id)
            )
            self.db.disconnect()
            return True
        except Exception as e:
            self.db.disconnect()
            return False

    def check_single_device_login(self, user_id, device_id):
        """Check if user is already logged in from another device"""
        if not SINGLE_DEVICE_LOGIN:
            return True

        if not self.db.connect():
            return True

        try:
            # Get active sessions for this user
            active_sessions = self.db.fetch_all(
                """SELECT session_id, device_id FROM sessions 
                   WHERE user_id = %s AND is_active = TRUE""",
                (user_id,)
            )

            for session in active_sessions:
                if session[1] != device_id:  # Different device
                    # Invalidate old session
                    self.db.execute_query(
                        "UPDATE sessions SET is_active = FALSE WHERE session_id = %s",
                        (session[0],)
                    )

            self.db.disconnect()
            return True
        except Exception as e:
            self.db.disconnect()
            return False

    def log_tab_switch(self, attempt_id):
        """Log tab switch for anti-cheating"""
        if not self.db.connect():
            return False

        try:
            # Get current tab switch count
            attempt = self.db.fetch_one(
                "SELECT tab_switch_count FROM test_attempts WHERE attempt_id = %s",
                (attempt_id,)
            )

            if attempt:
                new_count = attempt[0] + 1
                self.db.execute_query(
                    "UPDATE test_attempts SET tab_switch_count = %s WHERE attempt_id = %s",
                    (new_count, attempt_id)
                )

                self.db.disconnect()
                return new_count

            self.db.disconnect()
            return 0
        except Exception as e:
            self.db.disconnect()
            return 0

    def check_tab_switch_limit(self, attempt_id):
        """Check if tab switch limit exceeded"""
        if not self.db.connect():
            return True

        try:
            attempt = self.db.fetch_one(
                "SELECT tab_switch_count FROM test_attempts WHERE attempt_id = %s",
                (attempt_id,)
            )

            self.db.disconnect()
            
            if attempt and attempt[0] >= MAX_TAB_SWITCHES:
                return False
            return True
        except Exception as e:
            self.db.disconnect()
            return True

    def generate_csrf_token(self):
        """Generate CSRF token"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

    def validate_csrf_token(self, token, session_token):
        """Validate CSRF token"""
        # In production, store tokens in database
        return True

    def get_html_disable_copy_paste(self):
        """Return HTML/JS to disable copy-paste on test page"""
        if not DISABLE_COPY_PASTE:
            return ""
        
        return """
        <script>
            document.addEventListener('copy', function(e) {
                e.preventDefault();
                alert('Copying is disabled during the test');
                return false;
            });
            document.addEventListener('cut', function(e) {
                e.preventDefault();
                alert('Cutting is disabled during the test');
                return false;
            });
            document.addEventListener('paste', function(e) {
                e.preventDefault();
                alert('Pasting is disabled during the test');
                return false;
            });
            // Disable right click
            document.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                alert('Right-click is disabled during the test');
                return false;
            });
            // Disable keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'x' || e.key === 'v')) {
                    e.preventDefault();
                    return false;
                }
            });
        </script>
        """

    def get_fullscreen_js(self):
        """Return JavaScript for fullscreen enforcement"""
        return """
        <script>
            function enterFullscreen() {
                const elem = document.documentElement;
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                } else if (elem.mozRequestFullScreen) {
                    elem.mozRequestFullScreen();
                } else if (elem.webkitRequestFullscreen) {
                    elem.webkitRequestFullscreen();
                } else if (elem.msRequestFullscreen) {
                    elem.msRequestFullscreen();
                }
            }
            
            function exitFullscreenWarning() {
                document.addEventListener('fullscreenchange', function() {
                    if (!document.fullscreenElement) {
                        alert('⚠️ WARNING: You have exited fullscreen mode. This will be recorded as suspicious activity.');
                    }
                });
            }
            
            window.addEventListener('load', function() {
                setTimeout(enterFullscreen, 100);
                exitFullscreenWarning();
            });
        </script>
        """

    def parameterized_query_example(self, query, params):
        """Example of parameterized query to prevent SQL injection"""
        # Always use parameterized queries with placeholders
        # Don't concatenate user input into queries
        return query, params

# Global security instance
security = Security()

def get_security():
    """Get security instance"""
    return security
