import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ..database import Database
from datetime import datetime, timedelta

class Analytics:
    def __init__(self):
        self.db = Database()

    def get_subject_toppers(self, test_id, limit=10):
        """Get top performers in a test"""
        if not self.db.connect():
            return []

        try:
            toppers = self.db.fetch_all(
                """SELECT u.full_name, u.user_id, tr.marks_obtained, tr.percentage, tr.grade
                   FROM test_results tr
                   JOIN users u ON tr.student_id = u.user_id
                   WHERE tr.test_id = %s
                   ORDER BY tr.marks_obtained DESC
                   LIMIT %s""",
                (test_id, limit)
            )

            self.db.disconnect()
            return toppers
        except Exception as e:
            self.db.disconnect()
            return []

    def get_average_marks(self, test_id):
        """Get average marks for a test"""
        if not self.db.connect():
            return None

        try:
            stats = self.db.fetch_one(
                """SELECT 
                   AVG(marks_obtained) as avg_marks,
                   MIN(marks_obtained) as min_marks,
                   MAX(marks_obtained) as max_marks,
                   STDDEV(marks_obtained) as stddev_marks,
                   COUNT(*) as total_students
                   FROM test_results WHERE test_id = %s""",
                (test_id,)
            )

            self.db.disconnect()

            if stats:
                return {
                    'average': round(float(stats[0]) if stats[0] else 0, 2),
                    'minimum': round(float(stats[1]) if stats[1] else 0, 2),
                    'maximum': round(float(stats[2]) if stats[2] else 0, 2),
                    'stddev': round(float(stats[3]) if stats[3] else 0, 2),
                    'total_students': stats[4]
                }
            return None
        except Exception as e:
            self.db.disconnect()
            return None

    def get_question_difficulty_analysis(self, test_id):
        """Analyze question difficulty based on performance"""
        if not self.db.connect():
            return []

        try:
            analysis = self.db.fetch_all(
                """SELECT 
                   q.question_id,
                   q.question_text,
                   q.difficulty_level,
                   COUNT(sr.response_id) as total_attempts,
                   SUM(CASE WHEN sr.is_correct = TRUE THEN 1 ELSE 0 END) as correct_count,
                   ROUND(100.0 * SUM(CASE WHEN sr.is_correct = TRUE THEN 1 ELSE 0 END) / COUNT(sr.response_id), 2) as success_rate
                   FROM test_questions tq
                   JOIN questions q ON tq.question_id = q.question_id
                   LEFT JOIN student_responses sr ON tq.test_id = sr.test_id AND q.question_id = sr.question_id
                   WHERE tq.test_id = %s
                   GROUP BY q.question_id, q.question_text, q.difficulty_level
                   ORDER BY success_rate ASC""",
                (test_id,)
            )

            result = []
            for row in analysis:
                result.append({
                    'question_id': row[0],
                    'question_text': row[1][:50] + '...' if len(row[1]) > 50 else row[1],
                    'difficulty': row[2],
                    'attempts': row[3],
                    'correct': row[4],
                    'success_rate': float(row[5]) if row[5] else 0
                })

            self.db.disconnect()
            return result
        except Exception as e:
            self.db.disconnect()
            return []

    def get_co_po_attainment(self, test_id):
        """Calculate CO-PO attainment"""
        if not self.db.connect():
            return []

        try:
            attainment = self.db.fetch_all(
                """SELECT 
                   co.co_code,
                   COUNT(DISTINCT sr.student_id) as students_attempted,
                   COUNT(CASE WHEN sr.is_correct = TRUE THEN 1 END) as correct_responses,
                   ROUND(100.0 * COUNT(CASE WHEN sr.is_correct = TRUE THEN 1 END) / 
                          NULLIF(COUNT(DISTINCT sr.student_id * sr.response_id), 0), 2) as attainment_percentage
                   FROM test_questions tq
                   JOIN questions q ON tq.question_id = q.question_id
                   LEFT JOIN course_outcomes co ON q.co_id = co.co_id
                   LEFT JOIN student_responses sr ON tq.test_id = sr.test_id AND q.question_id = sr.question_id
                   WHERE tq.test_id = %s AND co.co_id IS NOT NULL
                   GROUP BY co.co_code
                   ORDER BY attainment_percentage DESC""",
                (test_id,)
            )

            result = []
            for row in attainment:
                result.append({
                    'co_code': row[0],
                    'students': row[1],
                    'correct': row[2],
                    'attainment': float(row[3]) if row[3] else 0
                })

            self.db.disconnect()
            return result
        except Exception as e:
            self.db.disconnect()
            return []

    def get_department_comparison(self, subject_id):
        """Compare performance across departments"""
        if not self.db.connect():
            return []

        try:
            comparison = self.db.fetch_all(
                """SELECT 
                   d.dept_name,
                   COUNT(DISTINCT tr.student_id) as students,
                   AVG(tr.marks_obtained) as avg_marks,
                   AVG(tr.percentage) as avg_percentage
                   FROM test_results tr
                   JOIN users u ON tr.student_id = u.user_id
                   JOIN departments d ON u.department = d.dept_name
                   JOIN tests t ON tr.test_id = t.test_id
                   WHERE t.subject_id = %s
                   GROUP BY d.dept_name
                   ORDER BY avg_percentage DESC""",
                (subject_id,)
            )

            self.db.disconnect()
            return comparison
        except Exception as e:
            self.db.disconnect()
            return []

    def generate_marks_distribution_chart(self, test_id):
        """Generate marks distribution histogram"""
        if not self.db.connect():
            return None

        try:
            marks_data = self.db.fetch_all(
                """SELECT marks_obtained FROM test_results WHERE test_id = %s""",
                (test_id,)
            )

            if not marks_data:
                self.db.disconnect()
                return None

            marks = [row[0] for row in marks_data]
            
            fig = go.Figure(data=[go.Histogram(x=marks, nbinsx=20)])
            fig.update_layout(
                title='Marks Distribution',
                xaxis_title='Marks',
                yaxis_title='Number of Students',
                template='plotly_white'
            )

            self.db.disconnect()
            return fig
        except Exception as e:
            self.db.disconnect()
            return None

    def generate_performance_by_difficulty_chart(self, test_id):
        """Generate performance by difficulty level chart"""
        if not self.db.connect():
            return None

        try:
            difficulty_data = self.db.fetch_all(
                """SELECT 
                   q.difficulty_level,
                   COUNT(sr.response_id) as total,
                   SUM(CASE WHEN sr.is_correct = TRUE THEN 1 ELSE 0 END) as correct
                   FROM test_questions tq
                   JOIN questions q ON tq.question_id = q.question_id
                   LEFT JOIN student_responses sr ON tq.test_id = sr.test_id AND q.question_id = sr.question_id
                   WHERE tq.test_id = %s
                   GROUP BY q.difficulty_level""",
                (test_id,)
            )

            if not difficulty_data:
                self.db.disconnect()
                return None

            difficulties = []
            success_rates = []
            for row in difficulty_data:
                difficulties.append(row[0])
                success_rates.append(round(100 * row[2] / row[1], 2) if row[1] > 0 else 0)

            fig = go.Figure(data=[
                go.Bar(x=difficulties, y=success_rates)
            ])
            fig.update_layout(
                title='Success Rate by Difficulty',
                xaxis_title='Difficulty Level',
                yaxis_title='Success Rate (%)',
                template='plotly_white'
            )

            self.db.disconnect()
            return fig
        except Exception as e:
            self.db.disconnect()
            return None

    def generate_grade_distribution_chart(self, test_id):
        """Generate grade distribution pie chart"""
        if not self.db.connect():
            return None

        try:
            grade_data = self.db.fetch_all(
                """SELECT grade, COUNT(*) as count FROM test_results 
                   WHERE test_id = %s GROUP BY grade""",
                (test_id,)
            )

            if not grade_data:
                self.db.disconnect()
                return None

            grades = [row[0] for row in grade_data]
            counts = [row[1] for row in grade_data]

            fig = go.Figure(data=[go.Pie(labels=grades, values=counts)])
            fig.update_layout(title='Grade Distribution')

            self.db.disconnect()
            return fig
        except Exception as e:
            self.db.disconnect()
            return None

    def generate_report_pdf(self, test_id):
        """Generate PDF report (requires reportlab)"""
        # This is a placeholder - implement with reportlab for actual PDF generation
        pass

    def export_results_to_excel(self, test_id):
        """Export test results to Excel"""
        if not self.db.connect():
            return None

        try:
            results = self.db.fetch_all(
                """SELECT 
                   u.full_name,
                   u.username,
                   u.department,
                   tr.total_questions,
                   tr.correct_answers,
                   tr.incorrect_answers,
                   tr.marks_obtained,
                   tr.percentage,
                   tr.grade,
                   tr.passed
                   FROM test_results tr
                   JOIN users u ON tr.student_id = u.user_id
                   WHERE tr.test_id = %s
                   ORDER BY tr.marks_obtained DESC""",
                (test_id,)
            )

            if not results:
                self.db.disconnect()
                return None

            df = pd.DataFrame(results, columns=[
                'Name', 'Username', 'Department', 'Total Questions',
                'Correct', 'Incorrect', 'Marks', 'Percentage', 'Grade', 'Passed'
            ])

            self.db.disconnect()
            return df
        except Exception as e:
            self.db.disconnect()
            return None

# Global analytics instance
analytics = Analytics()

def get_analytics():
    """Get analytics instance"""
    return analytics
