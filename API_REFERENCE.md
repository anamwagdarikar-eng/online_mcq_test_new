# 🔌 API Reference (Future Enhancement)

This document outlines the planned REST API endpoints for the MCQ Test System.
Currently, the system uses Streamlit's session-based architecture. REST API endpoints are planned for version 2.0.

## Base URL

```
http://localhost:8501/api
https://your-domain.com/api (Production)
```

## Authentication

All API requests (except login/register) require JWT token in header:

```
Authorization: Bearer <jwt_token>
```

---

## User Management

### Register New User
```
POST /auth/register
Content-Type: application/json

{
  "username": "student01",
  "email": "student@college.edu",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "student",
  "department": "Computer Science"
}

Response: 201 Created
{
  "success": true,
  "user_id": 1,
  "message": "User registered successfully"
}
```

### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "student01",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "success": true,
  "user_id": 1,
  "role": "student",
  "session_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### Logout
```
POST /auth/logout
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Get User Profile
```
GET /users/me
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "user_id": 1,
  "username": "student01",
  "email": "student@college.edu",
  "full_name": "John Doe",
  "role": "student",
  "department": "Computer Science",
  "last_login": "2024-01-15T10:30:00Z"
}
```

### Update User Profile
```
PUT /users/me
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "full_name": "John Doe Updated",
  "phone": "+91-9876543210"
}

Response: 200 OK
{
  "success": true,
  "message": "Profile updated successfully"
}
```

---

## Test Management

### List Available Tests
```
GET /tests
Authorization: Bearer <jwt_token>

Query Parameters:
  - department: filter by department
  - subject: filter by subject
  - status: published/draft
  - limit: 10
  - offset: 0

Response: 200 OK
{
  "tests": [
    {
      "test_id": 1,
      "test_name": "Data Structures Mid Term",
      "subject_name": "Data Structures",
      "duration_minutes": 120,
      "total_marks": 100,
      "start_time": "2024-01-20T10:00:00Z",
      "end_time": "2024-01-20T12:00:00Z"
    }
  ],
  "total": 25
}
```

### Get Test Details
```
GET /tests/{test_id}
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "test_id": 1,
  "test_name": "Data Structures Mid Term",
  "subject_id": 1,
  "duration_minutes": 120,
  "total_marks": 100,
  "passing_marks": 40,
  "negative_marking_enabled": true,
  "randomize_questions": true,
  "randomize_options": true,
  "allow_review": true,
  "show_results": false,
  "instructions": "Read each question carefully..."
}
```

### Create Test (Faculty/Admin)
```
POST /tests
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "test_name": "Data Structures Final",
  "subject_id": 1,
  "total_marks": 100,
  "duration_minutes": 120,
  "passing_marks": 40,
  "negative_marking_enabled": true,
  "start_time": "2024-01-25T10:00:00Z",
  "end_time": "2024-01-25T14:00:00Z"
}

Response: 201 Created
{
  "test_id": 5,
  "test_name": "Data Structures Final",
  "status": "draft"
}
```

### Publish Test
```
PUT /tests/{test_id}/publish
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "success": true,
  "test_id": 5,
  "status": "published"
}
```

### Add Question to Test
```
POST /tests/{test_id}/questions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "question_id": 10,
  "question_order": 1,
  "marks": 2
}

Response: 201 Created
{
  "success": true,
  "test_question_id": 25
}
```

---

## Test Attempts

### Start Test Attempt
```
POST /tests/{test_id}/attempts/start
Authorization: Bearer <jwt_token>

Response: 201 Created
{
  "attempt_id": 100,
  "test_id": 1,
  "start_time": "2024-01-20T10:00:00Z",
  "duration_minutes": 120,
  "total_questions": 50,
  "questions": [
    {
      "question_id": 1,
      "question_text": "What is...",
      "options": {
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      },
      "marks": 1,
      "difficulty": "Easy"
    }
  ]
}
```

### Get Current Attempt
```
GET /tests/{test_id}/attempts/current
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "attempt_id": 100,
  "test_id": 1,
  "status": "in_progress",
  "time_remaining": 6000,
  "questions_answered": 15,
  "questions_total": 50
}
```

### Submit Answer
```
POST /tests/{test_id}/attempts/{attempt_id}/responses
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "question_id": 1,
  "selected_answer": "B",
  "time_spent": 45
}

Response: 200 OK
{
  "success": true,
  "response_id": 500,
  "is_correct": true,
  "marks": 1
}
```

### Submit Test
```
POST /tests/{test_id}/attempts/{attempt_id}/submit
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "success": true,
  "attempt_id": 100,
  "test_id": 1,
  "results": {
    "total_questions": 50,
    "correct_answers": 40,
    "incorrect_answers": 8,
    "unanswered": 2,
    "marks_obtained": 78,
    "percentage": 78.0,
    "grade": "A",
    "passed": true
  }
}
```

### Auto-Submit on Timeout
```
POST /tests/{test_id}/attempts/{attempt_id}/auto-submit
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "success": true,
  "auto_submitted": true,
  "results": { ... }
}
```

---

## Results

### Get Test Results
```
GET /tests/{test_id}/results
Authorization: Bearer <jwt_token>

Query Parameters:
  - department: filter by department
  - limit: 20
  - offset: 0

Response: 200 OK
{
  "test_id": 1,
  "test_name": "Data Structures Mid Term",
  "total_students": 150,
  "results": [
    {
      "rank": 1,
      "student_name": "Alice Smith",
      "marks": 98,
      "percentage": 98.0,
      "grade": "A+",
      "passed": true
    }
  ]
}
```

### Get Student Results
```
GET /students/me/results
Authorization: Bearer <jwt_token>

Query Parameters:
  - limit: 20
  - offset: 0

Response: 200 OK
{
  "results": [
    {
      "test_id": 1,
      "test_name": "Data Structures Mid Term",
      "marks": 78,
      "percentage": 78.0,
      "grade": "A",
      "passed": true,
      "submitted_at": "2024-01-20T11:45:00Z"
    }
  ]
}
```

### Get Detailed Result
```
GET /results/{attempt_id}
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "attempt_id": 100,
  "test_id": 1,
  "student_id": 1,
  "total_questions": 50,
  "correct_answers": 40,
  "incorrect_answers": 8,
  "unanswered": 2,
  "marks_obtained": 78,
  "percentage": 78.0,
  "grade": "A",
  "passed": true,
  "duration": 90,
  "submitted_at": "2024-01-20T11:45:00Z",
  "responses": [
    {
      "question_id": 1,
      "selected_answer": "B",
      "correct_answer": "B",
      "is_correct": true,
      "marks": 1
    }
  ]
}
```

---

## Analytics

### Test Analytics
```
GET /analytics/tests/{test_id}
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "test_id": 1,
  "test_name": "Data Structures Mid Term",
  "total_students": 150,
  "average_marks": 72.5,
  "highest_marks": 98,
  "lowest_marks": 25,
  "pass_percentage": 85.3,
  "grade_distribution": {
    "A+": 10,
    "A": 35,
    "B": 50,
    "C": 40,
    "D": 15
  },
  "question_analysis": [
    {
      "question_id": 1,
      "success_rate": 92.3,
      "difficulty": "Easy"
    }
  ]
}
```

### Subject Analytics
```
GET /analytics/subjects/{subject_id}
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "subject_id": 1,
  "subject_name": "Data Structures",
  "tests": 5,
  "total_students": 300,
  "average_performance": 71.2,
  "departments": [
    {
      "dept_name": "Computer Science",
      "average": 75.5,
      "students": 150
    }
  ],
  "co_po_attainment": [
    {
      "co_code": "CO1",
      "attainment": 78.5
    }
  ]
}
```

### Department Analytics
```
GET /analytics/departments/{dept_id}
Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "dept_id": 1,
  "dept_name": "Computer Science",
  "total_students": 500,
  "average_performance": 72.3,
  "subjects": [
    {
      "subject_id": 1,
      "subject_name": "Data Structures",
      "average": 75.5
    }
  ]
}
```

---

## Questions

### Create Question
```
POST /questions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "subject_id": 1,
  "question_text": "What is the time complexity of binary search?",
  "question_type": "MCQ",
  "difficulty_level": "Medium",
  "marks": 1,
  "negative_marks": 0.25,
  "option_a": "O(n)",
  "option_b": "O(n log n)",
  "option_c": "O(log n)",
  "option_d": "O(1)",
  "correct_answer": "C",
  "explanation": "Binary search divides the search space in half each time..."
}

Response: 201 Created
{
  "question_id": 100,
  "message": "Question created successfully"
}
```

### Bulk Import Questions
```
POST /questions/bulk-import
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

File: questions.csv

Response: 200 OK
{
  "success": true,
  "imported": 50,
  "failed": 2,
  "errors": [
    {
      "row": 5,
      "error": "Missing required field: correct_answer"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request",
  "message": "Missing required field: email"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Test with ID 999 not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Burst**: 20 requests per 10 seconds
- **Headers**: 
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1642334400

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## Pagination

Endpoints supporting pagination use:

```
?limit=20&offset=0
```

Response includes:

```json
{
  "data": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

---

## Filtering

Endpoints support filtering:

```
GET /tests?department=CS&status=published&semester=4
```

---

## Sorting

```
GET /tests?sort_by=created_at&order=desc
```

---

## Implementation Notes

This API specification is for **Version 2.0** (planned).

Current implementation uses **Streamlit's session-based architecture**. To implement REST API:

1. Add FastAPI or Flask backend
2. Create API route handlers
3. Implement authentication middleware
4. Add rate limiting
5. Create API documentation (Swagger/OpenAPI)

---

## Webhook Events

Future webhooks:
- `test.created`
- `test.published`
- `attempt.started`
- `attempt.submitted`
- `result.calculated`

---

**Version**: 2.0 (Planned)  
**Status**: Specification Ready  
**Implementation**: Future Enhancement
