# Test Access Restrictions & Password Protection

## Overview
This document describes the new security features added to restrict student access to tests based on network IP restrictions and admin-issued 4-digit PIN passwords.

## Features Implemented

### 1. **Network IP Restrictions**
Students can now only access tests from permitted IP addresses configured by administrators.

#### Admin Setup (Faculty/Admin Panel):
- When creating a test, faculty can specify **Allowed IP Addresses**
- Format: Comma-separated IP addresses (e.g., `192.168.1.100, 192.168.1.101, 192.168.1.102`)
- Leave blank to allow access from any IP
- IPs are stored in the `tests.allowed_ips` column

#### Student Experience:
- When viewing **Available Tests**, only tests with matching IP restrictions appear
- If tests are scheduled but student's IP is unauthorized: warning message displays
  > "Tests are scheduled, but your current network IP is not authorized for access. Contact the administrator."
- If student attempts to start a test from unauthorized IP: error message blocks access
  > "Your current network IP is not authorized to access this test. Contact the admin for access."

### 2. **Test Access Password (4-Digit PIN)**
Administrators can require a 4-digit numeric password for accessing each test.

#### Admin Setup (Faculty/Admin Panel):
- When creating a test, faculty can set **Test Password (4 digits)**
- Format: Exactly 4 numeric digits (e.g., `1234`, `5678`)
- Password is **hashed** using bcrypt (not stored in plaintext)
- Stored in `tests.access_password_hash` column
- Leave empty if no password required

#### Student Experience:
- When starting a test with password protection, a password dialog appears:
  > "Enter 4-digit test password"
- Student must enter the PIN provided by administrator
- Validation:
  - If not 4 digits: `"Please enter the 4-digit test password provided by your admin."`
  - If incorrect: `"Incorrect test password. Please check with your administrator."`
- Once validated, test attempt starts immediately

### 3. **Database Schema Changes**

#### New Columns in `tests` Table:
```sql
allowed_ips TEXT
  -- Comma-separated list of permitted IP addresses
  -- NULL or empty = allow all IPs

access_password_hash VARCHAR(255)
  -- Bcrypt hash of 4-digit PIN password
  -- NULL = no password required
```

#### Schema Migration:
The system automatically applies these changes to existing databases:
```python
ALTER TABLE tests ADD COLUMN IF NOT EXISTS allowed_ips TEXT;
ALTER TABLE tests ADD COLUMN IF NOT EXISTS access_password_hash VARCHAR(255);
```

### 4. **Helper Functions**

#### `get_client_ip()` → `str`
Extracts student's IP address from:
- `HTTP_X_FORWARDED_FOR` (load balancer)
- `HTTP_CLIENT_IP` (proxy)
- `HTTP_X_REAL_IP` (reverse proxy)
- Defaults to `127.0.0.1` if not detected

#### `is_ip_allowed(allowed_ips, ip_address)` → `bool`
Checks if a student's IP is in the allowed list:
- Returns `True` if `allowed_ips` is empty/null
- Parses comma-separated IPs
- Returns `True` if student IP matches any allowed IP
- Returns `False` if IP not in allowed list

#### `validate_four_digit_pin(pin)` → `bool`
Validates password format:
- Must be string
- Must contain only digits
- Must be exactly 4 characters long

#### `fetch_available_tests_for_student(department, semester, student_ip)` → `(accessible_tests, all_tests)`
Retrieves tests for a student with IP filtering:
- Filters by department and semester
- Returns two lists:
  - `accessible_tests`: Tests with matching IP restrictions
  - `all_tests`: All tests (for showing warning if blocked)

## Usage Workflow

### Admin/Faculty: Create Test with Restrictions
1. Go to **Faculty Dashboard** → **Create New Test**
2. Fill in test details (name, subject, marks, duration, etc.)
3. **Optional** - Add IP Restrictions:
   - In "Allowed IP Addresses" field, enter: `192.168.1.100, 192.168.1.101`
4. **Optional** - Add 4-Digit Password:
   - In "Test Password (4 digits)" field, enter: `5678`
5. Click **Create Test**
6. Communicate password `5678` to students through secure channel (email, messaging, etc.)

### Student: Access Restricted Test
1. Login to system
2. Go to **Available Tests**
   - Only sees tests matching their IP
   - Sees warning if tests exist but are IP-restricted
3. Click **Start Test** on accessible test
4. If test has password:
   - Dialog appears: "Enter 4-digit test password"
   - Enter PIN: `5678`
   - Click **Start Test**
5. Test attempt begins

## Security Considerations

### IP-Based Restrictions:
- **Pros**: Prevents unauthorized network access
- **Cons**: 
  - Does not prevent cheating within allowed network
  - Requires coordination with IT for IP management
  - VPN/Proxy bypass possible if misconfigured

### PIN Password Protection:
- **Pros**: 
  - Simple 4-digit PIN easy for students to remember
  - Bcrypt hashed (secure storage)
  - Cannot be reverse-engineered
- **Cons**:
  - 4-digit PIN only ~10,000 combinations
  - Should be combined with IP restrictions for stronger security
  - Password must be shared securely (not in public announcements)

## Best Practices

1. **Combine Both Restrictions**
   - Use IP restrictions for network-level control
   - Use PIN password as additional layer
   - Example: Allow only lab network IPs + require PIN

2. **PIN Distribution**
   - Share PIN via secure email (LMS or official college email)
   - Do NOT post in public forums or chat groups
   - Change PIN for each test to prevent leakage
   - Consider time-based PIN rotation if needed

3. **IP Management**
   - Get exact IPs from your IT/Network admin
   - Test connectivity before test day
   - Have backup access points with additional IPs
   - Document IP ranges for multiple exam centers

4. **Fallback Plan**
   - Keep admin account with bypass capability
   - Have IT contact available during exam
   - Document steps to add emergency IPs mid-exam

## Examples

### Example 1: Lab Exam with IP Restriction Only
```
Test Name: Data Structures Lab Test
Allowed IPs: 192.168.1.50, 192.168.1.51, 192.168.1.52, 192.168.1.53
Test Password: (leave empty)
```
Students can access only from these 4 lab machines, no password needed.

### Example 2: Online Exam with PIN Protection Only
```
Test Name: DSA Theory Exam
Allowed IPs: (leave empty)
Test Password: 7391
```
Students can access from any IP after entering PIN `7391`.

### Example 3: Hybrid Security
```
Test Name: Final Exam - Computer Networking
Allowed IPs: 203.0.113.0, 203.0.113.1, 203.0.113.2
Test Password: 4521
```
Students must be on one of the 3 exam center networks AND know the PIN.

## Troubleshooting

### Issue: "Your current network IP is not authorized"
- **Solution**: Check if your IP is in the allowed list with your admin
- **Debug**: Try accessing from the allowed network
- **Contact**: Reach out to administrator with your current IP

### Issue: "Incorrect test password"
- **Solution**: Verify the PIN with your instructor
- **Common**: Wrong PIN entered or typo
- **Reset**: Contact administrator for correct PIN

### Issue: "No tests available" but tests are scheduled
- **Possible Causes**:
  1. Your network IP is not authorized
  2. Current time is outside test schedule
  3. You already attempted the test (one attempt per test)
- **Solution**: Check all three conditions with administrator

## Files Modified

- `database.py`: Added schema for `allowed_ips` and `access_password_hash`
- `main.py`:
  - Added `get_client_ip()` function
  - Added `is_ip_allowed()` function
  - Added `validate_four_digit_pin()` function
  - Added `fetch_available_tests_for_student()` function
  - Updated student dashboard to filter by IP
  - Updated test start flow to check IP and validate password
  - Updated faculty test creation form to input IP list and PIN
  - Added schema migration in database initialization

## Database Schema

```sql
-- Added to existing tests table:
ALTER TABLE tests ADD COLUMN allowed_ips TEXT;
ALTER TABLE tests ADD COLUMN access_password_hash VARCHAR(255);
```

## Version
- **Version**: 2.1.0
- **Date**: June 3, 2026
- **Features**: Network IP restrictions + 4-digit PIN password protection
