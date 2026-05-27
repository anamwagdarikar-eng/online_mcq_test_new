import random
from database import Database
from datetime import datetime, timedelta
from config import AUTO_SUBMIT_ON_TIMEOUT, ENABLE_NEGATIVE_MARKING, NEGATIVE_MARKING_PERCENTAGE

class TestManagement:
    def __init__(self):
        self.db = Database()

    def create_test(self, test_data):
        """Create new test"""
        if not self.db.connect():
            return {"success": False, "message": "Database connection failed"}

        try:
            self.db.execute_query(
                """INSERT INTO tests (test_name, subject_id, dept_id, created_by, test_description,
                   total_marks, duration_minutes, passing_marks, negative_marking_enabled,
                   enable_fullscreen, enable_tab_warnings, start_time, end_time,
                   randomize_questions, randomize_options) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (test_data['test_name'], test_data['subject_id'], test_data['dept_id'],
                 test_data['created_by'], test_data.get('description', ''),
                 test_data.get('total_marks', 100), test_data.get('duration', 60),
                 test_data.get('passing_marks', 40), test_data.get('negative_marking', True),
                 test_data.get('fullscreen', True), test_data.get('tab_warnings', True),
                 test_data['start_time'], test_data['end_time'],
                 test_data.get('randomize_questions', True),
                 test_data.get('randomize_options', True))
            )

            test = self.db.fetch_one("SELECT LASTVAL();")
            test_id = test[0] if test else None

            self.db.disconnect()
            return {"success": True, "test_id": test_id, "message": "Test created successfully"}
        except Exception as e:
            self.db.disconnect()
            return {"success": False, "message": str(e)}

    def add_question_to_test(self, test_id, question_id, order):
        """Add question to test"""
        if not self.db.connect():
            return False

        try:
            # Get question details
            question = self.db.fetch_one(
                "SELECT marks, negative_marks FROM questions WHERE question_id = %s",
                (question_id,)
            )

            if question:
                self.db.execute_query(
                    """INSERT INTO test_questions (test_id, question_id, question_order, marks, negative_marks)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (test_id, question_id, order, question[0], question[1])
                )

            self.db.disconnect()
            return True
        except Exception as e:
            self.db.disconnect()
            return False

    def get_test_questions(self, test_id, randomize=False):
        """Get test questions"""
        if not self.db.connect():
            return []

        try:
            # Get test settings
            test = self.db.fetch_one(
                "SELECT randomize_questions, randomize_options FROM tests WHERE test_id = %s",
                (test_id,)
            )

            questions = self.db.fetch_all(
                """SELECT q.question_id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                          q.difficulty_level, q.marks, tq.marks, tq.question_order
                   FROM test_questions tq
                   JOIN questions q ON tq.question_id = q.question_id
                   WHERE tq.test_id = %s
                   ORDER BY tq.question_order""",
                (test_id,)
            )

            questions_list = []
            for q in questions:
                question_dict = {
                    'question_id': q[0],
                    'question_text': q[1],
                    'options': {
                        'A': q[2],
                        'B': q[3],
                        'C': q[4],
                        'D': q[5]
                    },
                    'difficulty': q[6],
                    'marks': q[8],
                    'order': q[9]
                }

                # Randomize options if enabled
                if test and test[1]:  # randomize_options
                    options_list = list(question_dict['options'].items())
                    random.shuffle(options_list)
                    question_dict['options'] = dict(options_list)

                questions_list.append(question_dict)

            # Randomize questions if enabled
            if test and test[0]:  # randomize_questions
                random.shuffle(questions_list)

            self.db.disconnect()
            return questions_list
        except Exception as e:
            self.db.disconnect()
            return []

    def submit_response(self, test_id, student_id, question_id, selected_answer):
        """Submit student response"""
        if not self.db.connect():
            return {"success": False}

        try:
            # Get correct answer
            question = self.db.fetch_one(
                "SELECT correct_answer, marks FROM questions WHERE question_id = %s",
                (question_id,)
            )

            if not question:
                self.db.disconnect()
                return {"success": False}

            correct_answer = question[0]
            marks = question[1]
            is_correct = selected_answer == correct_answer

            # Get current attempt
            attempt = self.db.fetch_one(
                """SELECT attempt_id FROM test_attempts 
                   WHERE test_id = %s AND student_id = %s AND status = 'in_progress'
                   ORDER BY attempt_id DESC LIMIT 1""",
                (test_id, student_id)
            )

            if not attempt:
                self.db.disconnect()
                return {"success": False}

            attempt_id = attempt[0]

            # Calculate marks
            marks_obtained = marks if is_correct else 0
            if not is_correct and ENABLE_NEGATIVE_MARKING:
                marks_obtained = -marks * NEGATIVE_MARKING_PERCENTAGE

            # Insert response
            self.db.execute_query(
                """INSERT INTO student_responses (test_id, student_id, question_id, selected_answer, is_correct, marks_obtained)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (test_id, student_id, question_id, selected_answer, is_correct, marks_obtained)
            )

            self.db.disconnect()
            return {"success": True, "is_correct": is_correct, "marks": marks_obtained}
        except Exception as e:
            self.db.disconnect()
            return {"success": False, "message": str(e)}

    def submit_test(self, test_id, student_id):
        """Submit test and calculate results"""
        if not self.db.connect():
            return {"success": False}

        try:
            # Get attempt
            attempt = self.db.fetch_one(
                """SELECT attempt_id FROM test_attempts 
                   WHERE test_id = %s AND student_id = %s AND status = 'in_progress'
                   ORDER BY attempt_id DESC LIMIT 1""",
                (test_id, student_id)
            )

            if not attempt:
                self.db.disconnect()
                return {"success": False}

            attempt_id = attempt[0]

            # Update attempt status
            self.db.execute_query(
                """UPDATE test_attempts SET status = 'submitted', end_time = NOW(), completed = TRUE
                   WHERE attempt_id = %s""",
                (attempt_id,)
            )

            # Calculate results
            results = self.calculate_results(test_id, student_id, attempt_id)

            self.db.disconnect()
            return {"success": True, "results": results}
        except Exception as e:
            self.db.disconnect()
            return {"success": False, "message": str(e)}

    def calculate_results(self, test_id, student_id, attempt_id):
        """Calculate test results"""
        if not self.db.connect():
            return None

        try:
            # Get all responses
            responses = self.db.fetch_all(
                """SELECT COUNT(*), SUM(CASE WHEN is_correct = TRUE THEN 1 ELSE 0 END),
                          SUM(CASE WHEN is_correct = FALSE THEN 1 ELSE 0 END),
                          COALESCE(SUM(marks_obtained), 0)
                   FROM student_responses
                   WHERE test_id = %s AND student_id = %s""",
                (test_id, student_id)
            )

            if not responses or not responses[0]:
                self.db.disconnect()
                return None

            response = responses[0]
            total_questions = response[0]
            correct_answers = response[1] or 0
            incorrect_answers = response[2] or 0
            total_marks_obtained = float(response[3]) or 0

            # Get test details
            test = self.db.fetch_one(
                "SELECT total_marks, passing_marks FROM tests WHERE test_id = %s",
                (test_id,)
            )

            total_marks = test[0]
            passing_marks = test[1]
            unanswered = total_questions - correct_answers - incorrect_answers

            percentage = (total_marks_obtained / total_marks * 100) if total_marks > 0 else 0
            passed = total_marks_obtained >= passing_marks

            # Determine grade
            grade = self.calculate_grade(percentage)

            # Insert test results
            self.db.execute_query(
                """INSERT INTO test_results (attempt_id, test_id, student_id, total_questions,
                   correct_answers, incorrect_answers, unanswered, total_marks,
                   marks_obtained, percentage, grade, passed)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (attempt_id, test_id, student_id, total_questions, correct_answers,
                 incorrect_answers, unanswered, total_marks, total_marks_obtained,
                 percentage, grade, passed)
            )

            # Update attempt with results
            self.db.execute_query(
                """UPDATE test_attempts SET total_marks_obtained = %s WHERE attempt_id = %s""",
                (total_marks_obtained, attempt_id)
            )

            self.db.disconnect()

            return {
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'incorrect_answers': incorrect_answers,
                'unanswered': unanswered,
                'total_marks': total_marks,
                'marks_obtained': total_marks_obtained,
                'percentage': round(percentage, 2),
                'grade': grade,
                'passed': passed
            }
        except Exception as e:
            self.db.disconnect()
            return None

    def calculate_grade(self, percentage):
        """Calculate grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'

    def start_test_attempt(self, test_id, student_id, ip_address, device_id):
        """Start test attempt"""
        if not self.db.connect():
            return None

        try:
            # Get test details
            test = self.db.fetch_one(
                "SELECT duration_minutes FROM tests WHERE test_id = %s",
                (test_id,)
            )

            if not test:
                self.db.disconnect()
                return None

            duration = test[0]

            # Create attempt
            self.db.execute_query(
                """INSERT INTO test_attempts (test_id, student_id, start_time, status, ip_address, device_id)
                   VALUES (%s, %s, NOW(), 'in_progress', %s, %s)""",
                (test_id, student_id, ip_address, device_id)
            )

            attempt = self.db.fetch_one("SELECT LASTVAL();")
            attempt_id = attempt[0] if attempt else None

            self.db.disconnect()
            return {
                'attempt_id': attempt_id,
                'duration_minutes': duration,
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(minutes=duration)
            }
        except Exception as e:
            self.db.disconnect()
            return None

# Global test management instance
test_management = TestManagement()

def get_test_management():
    """Get test management instance"""
    return test_management
