# ⚡ Quick Start Guide

Get the MCQ Test System up and running in 5 minutes!

## 🚀 Quick Setup (Development)

### 1. Prerequisites Check
```bash
python --version  # Should be 3.8+
pip --version     # Should be 20.0+
```

### 2. Clone and Setup
```bash
cd d:\online_mcq_test
python -m venv venv
.\venv\Scripts\activate  # Windows only
```

### 3. Install & Configure
```bash
pip install -r requirements.txt
cp .env.example .env
```

### 4. Setup Database
- Create PostgreSQL database named `mcq_db`
- Or use NeonDB (cloud PostgreSQL)
- Update DATABASE_URL in .env

### 5. Initialize
```bash
python init_db.py          # Create tables
python seed_data.py        # Add sample data
streamlit run main.py      # Start app
```

### 6. Login
Open: http://localhost:8501

Default credentials:
- **Admin**: `admin` / `Admin@123`
- **Faculty**: `faculty1` / `Faculty@123`
- **Student**: `student01` / `Student@001`

---

## 🐳 Quick Setup (Docker)

```bash
docker-compose up -d       # Start containers
docker-compose logs -f app # View logs

# Access
# App: http://localhost:8501
# pgAdmin: http://localhost:5050
```

---

## 📋 First Steps

### Admin
1. Login as admin
2. Go to Admin Panel
3. Create departments
4. Create subjects
5. Create users (faculty, students)

### Faculty
1. Login as faculty
2. Go to Faculty Panel
3. Add questions to question bank
4. Create test and add questions
5. Publish test

### Student
1. Login as student
2. See available tests
3. Start test
4. Answer questions
5. Submit test
6. View results

---

## ⚙️ Common Commands

### Database
```bash
# Backup
pg_dump -U mcq_user -d mcq_db > backup.sql

# Restore
psql -U mcq_user -d mcq_db < backup.sql

# Connect
psql -U mcq_user -d mcq_db
```

### Application
```bash
# Development
streamlit run main.py --logger.level=debug

# Production
streamlit run main.py --logger.level=error
```

### Docker
```bash
# Stop
docker-compose down

# Remove data
docker-compose down -v

# View logs
docker-compose logs -f

# Exec command
docker-compose exec app python seed_data.py
```

---

## 🔑 Environment Variables

```env
# Required
DATABASE_URL=postgresql://user:password@localhost/mcq_db

# Security (change in production)
SECRET_KEY=your-secret-key

# Optional
COLLEGE_NAME=Your College
ACADEMIC_YEAR=2024-2025
DEBUG_MODE=False
ENABLE_HTTPS=True
```

---

## 🎯 Features To Try

1. **Create Test**
   - Admin Panel → Create Test
   - Add questions
   - Publish

2. **Take Test**
   - Student Dashboard → Available Tests
   - Start Test
   - Answer questions
   - Submit

3. **View Analytics**
   - Faculty Panel → Analytics
   - Select test
   - View charts and statistics

4. **Question Bank**
   - Faculty Panel → Questions
   - Add questions
   - Bulk import from CSV

---

## 📱 Accessing from Other Devices

On same network:
```bash
streamlit run main.py --server.address 0.0.0.0
# Then access: http://<your-computer-ip>:8501
```

---

## ❓ Troubleshooting

**Database error?**
- Verify DATABASE_URL in .env
- Check PostgreSQL is running
- Test: `psql postgresql://user:password@host/db`

**Port 8501 already in use?**
```bash
streamlit run main.py --server.port 8502
```

**Need help?**
- Check README.md for detailed docs
- Check DEPLOYMENT.md for production setup
- Review logs in debug mode

---

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│        Streamlit Frontend UI            │
│  (Browser - HTTP/HTTPS)                 │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│     Python Backend (main.py)            │
│  - Authentication                       │
│  - Test Management                      │
│  - Security & Anti-Cheating            │
│  - Analytics                            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────┴──────────────────────┐
│   PostgreSQL / NeonDB Database          │
│  - Users & Roles                        │
│  - Tests & Questions                    │
│  - Student Responses                    │
│  - Results & Analytics                  │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist After Setup

- [ ] Login as admin
- [ ] Create test department
- [ ] Create subject
- [ ] Create faculty user
- [ ] Create student user
- [ ] Add sample questions
- [ ] Create and publish test
- [ ] Take test as student
- [ ] View results
- [ ] Check analytics

---

## 📚 Additional Resources

- **README.md** - Comprehensive documentation
- **DEPLOYMENT.md** - Production deployment
- **Database Schema** - See init_db.py
- **Code Comments** - Well-documented code

---

## 🎓 Ready to Use!

Your MCQ Test System is now ready for use. Start creating tests and assessments!

**Need to learn more?**
→ Read [README.md](README.md)

**Ready to deploy?**
→ Read [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Happy Testing! 🎉**
