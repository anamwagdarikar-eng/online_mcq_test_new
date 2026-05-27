# 🚀 GitHub + NeonDB + Streamlit Cloud Deployment Guide

## STEP 1: Get NeonDB Connection String (5 minutes)

Since you're already logged into NeonDB:

### 1.1 Get Connection String
1. Go to: https://console.neon.tech
2. Click on your **Project** name
3. Go to **Connection String** tab
4. Copy the **PostgreSQL** connection string (starts with `postgresql://`)
5. It looks like:
   ```
   postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require
   ```
6. **Save this somewhere safe** - you'll need it for Streamlit Cloud

### 1.2 Test the Connection (Optional but recommended)
```bash
# Test the connection
psql "your_connection_string_here"
```

---

## STEP 2: Initialize Git & Push to GitHub (10 minutes)

### 2.1 Initialize Local Git Repository
```powershell
cd d:\online_mcq_test
git init
git config user.name "Your Name"
git config user.email "anamwagdarikar@gmail.com"
git add .
git commit -m "Initial commit: MCQ Test System"
```

### 2.2 Create GitHub Repository
1. Go to: https://github.com/new
2. **Repository name**: `online_mcq_test` (or your choice)
3. **Description**: `Engineering College MCQ Test System`
4. Choose **Public** (needed for Streamlit Cloud free tier)
5. Click **Create repository**

### 2.3 Push to GitHub
Copy and run the commands shown on GitHub after creating repo:

```powershell
cd d:\online_mcq_test
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/online_mcq_test.git
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

---

## STEP 3: Create `.streamlit/secrets.toml` (5 minutes)

This file stores sensitive data for Streamlit Cloud.

### 3.1 Create the File Locally
Create file: `d:\online_mcq_test\.streamlit\secrets.toml`

Add this content:
```toml
DATABASE_URL = "postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require"
SECRET_KEY = "your-secret-key-change-this-12345"
COLLEGE_NAME = "Engineering College"
ACADEMIC_YEAR = "2023-2024"
```

Replace `DATABASE_URL` with your NeonDB connection string!

### 3.2 Update `.gitignore` to Keep Secrets Safe
Make sure `.streamlit/secrets.toml` is NOT pushed to GitHub:

Check your `.gitignore` contains:
```
.streamlit/secrets.toml
```

It should already be there. Verify:
```powershell
cd d:\online_mcq_test
type .gitignore | findstr "secrets"
```

---

## STEP 4: Update `.env.example` for Reference

Edit file: `d:\online_mcq_test\.env.example`

Add this content (for documentation only, actual secrets go in secrets.toml):
```
# NeonDB Connection String (get from https://console.neon.tech)
DATABASE_URL=postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require

SECRET_KEY=your-secret-key-here

COLLEGE_NAME=Engineering College
ACADEMIC_YEAR=2023-2024

ENABLE_HTTPS=True
SESSION_TIMEOUT=3600
ENABLE_FULLSCREEN=True
ENABLE_NEGATIVE_MARKING=True
ENABLE_TAB_WARNINGS=True
ENABLE_IP_LOGGING=True
DISABLE_COPY_PASTE=True
```

---

## STEP 5: Deploy on Streamlit Cloud (15 minutes)

### 5.1 Sign Up for Streamlit Cloud
1. Go to: https://streamlit.io/cloud
2. Click **Sign up**
3. Select **Continue with GitHub**
4. Authorize Streamlit to access your GitHub repositories
5. Log in with your GitHub account

### 5.2 Create New App
1. Click **Create app** button
2. Fill in:
   - **Repository**: `YOUR_USERNAME/online_mcq_test`
   - **Branch**: `main`
   - **Main file path**: `main.py`
3. Click **Deploy**

⏳ Wait 5-10 minutes for deployment...

### 5.3 Add Secrets to Streamlit Cloud
Once app is deployed:

1. Click **Settings** (gear icon) in app
2. Go to **Secrets** section
3. Click **Edit secrets** button
4. Add this:
```toml
DATABASE_URL = "postgresql://user:password@ep-xxxxx.neon.tech/dbname?sslmode=require"
SECRET_KEY = "your-secret-key-here"
COLLEGE_NAME = "Engineering College"
ACADEMIC_YEAR = "2023-2024"
ENABLE_HTTPS = "True"
SESSION_TIMEOUT = "3600"
```

5. Click **Save** - app will auto-restart

### 5.4 Initialize Database on Streamlit Cloud
The app will initialize the database on first run automatically.

---

## STEP 6: Verify Deployment

### 6.1 Test Your App
1. Your app is now live at: `https://your-username-online-mcq-test.streamlit.app`
2. Test login with credentials:
   - **Admin**: admin / Admin@123
   - **Faculty**: faculty1 / Faculty@123
   - **Student**: student01 / Student@001

### 6.2 Check Logs
In Streamlit Cloud dashboard, you can see logs for debugging.

---

## TROUBLESHOOTING

### ❌ "ModuleNotFoundError"
**Solution**: Streamlit Cloud should install from `requirements.txt` automatically. Wait 2-3 minutes.

### ❌ "Connection refused" / Database error
**Solution**: 
1. Verify DATABASE_URL in Streamlit Cloud secrets
2. Check NeonDB connection string is correct
3. Ensure database is initialized (first run auto-initializes)

### ❌ "Git push rejected"
**Solution**:
```powershell
git pull origin main
git push -u origin main
```

### ❌ App not updating after git push
**Solution**: 
1. Go to Streamlit Cloud dashboard
2. Click **Rerun** or **Restart** button
3. Wait 1-2 minutes

---

## QUICK REFERENCE LINKS

| Task | Link |
|------|------|
| NeonDB Dashboard | https://console.neon.tech |
| GitHub Repo | https://github.com/new |
| Streamlit Cloud | https://streamlit.io/cloud |
| Your Deployed App | https://your-username-online-mcq-test.streamlit.app |

---

## COMPLETE WORKFLOW CHECKLIST

- [ ] **Step 1**: Get NeonDB connection string
- [ ] **Step 2**: Initialize git & push to GitHub
- [ ] **Step 3**: Create `.streamlit/secrets.toml`
- [ ] **Step 4**: Update `.env.example`
- [ ] **Step 5**: Deploy on Streamlit Cloud
- [ ] **Step 6**: Add secrets to Streamlit Cloud
- [ ] **Step 7**: Test your deployed app

---

## IMPORTANT SECURITY NOTES

⚠️ **NEVER commit `secrets.toml` to GitHub!**
⚠️ **NEVER put real secrets in `.env.example`**
⚠️ **Always use Streamlit Cloud's Secrets tab for sensitive data**
⚠️ **Keep your NeonDB password secure**

---

## NEXT STEPS

1. **Immediate** (Next 30 minutes):
   - Complete steps 1-6 above
   - Test your deployed app

2. **Optional** (After deployment works):
   - Add custom domain (Streamlit Cloud pro feature)
   - Setup email notifications
   - Configure automatic backups for NeonDB

3. **Production Ready**:
   - Change default admin passwords
   - Enable HTTPS (Streamlit Cloud does this by default)
   - Setup database backups

---

## SUPPORT

- **Streamlit Docs**: https://docs.streamlit.io
- **NeonDB Docs**: https://neon.tech/docs
- **GitHub Pages**: https://pages.github.com

Your deployment is complete! 🎉
