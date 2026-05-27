# ✅ QUICK DEPLOYMENT CHECKLIST

## 🔴 STEP 1: Get NeonDB Connection String (DO THIS FIRST!)

### 1.1 Log into NeonDB
- Go to: https://console.neon.tech
- You should already be logged in with anamwagdarikar@gmail.com

### 1.2 Copy Connection String
1. Click your **Project** name
2. Go to **Connection** tab
3. Copy the **Connection String** (PostgreSQL)
4. It will look like:
   ```
   postgresql://neon_user:xxxxx@ep-cool-xxxx.neon.tech/dbname?sslmode=require
   ```

### 1.3 Update secrets.toml
1. Open: `d:\online_mcq_test\.streamlit\secrets.toml`
2. Replace this line:
   ```toml
   DATABASE_URL = "postgresql://your_username:your_password@ep-xxxxxxx.neon.tech/your_dbname?sslmode=require"
   ```
   With your actual connection string from Step 1.2

3. **Save the file** (Ctrl+S)

---

## 🟡 STEP 2: Initialize Git & Push to GitHub (10 minutes)

### 2.1 Open PowerShell Terminal
- Open your `d:\online_mcq_test` folder in VS Code
- Open Terminal (Ctrl + `)
- Make sure you're in `d:\online_mcq_test`

### 2.2 Initialize Git
Copy and paste each command one by one:

```powershell
git init
git config user.name "Your Name"
git config user.email "anamwagdarikar@gmail.com"
git add .
git commit -m "Initial commit: MCQ Test System"
```

### 2.3 Create GitHub Repository
1. Go to: https://github.com/new
2. Fill in:
   - **Repository name**: `online_mcq_test`
   - **Description**: `Engineering College MCQ Test System`
   - **Visibility**: Public (important!)
3. **Create repository** button

### 2.4 Connect Local Repo to GitHub
After creating repo, GitHub shows you commands. Run these in PowerShell:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/online_mcq_test.git
git push -u origin main
```

**⚠️ Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username!**

---

## 🟢 STEP 3: Deploy on Streamlit Cloud (15 minutes)

### 3.1 Log into Streamlit Cloud
1. Go to: https://streamlit.io/cloud
2. Click **Sign up** or **Log in**
3. Select **Continue with GitHub**
4. Authorize Streamlit

### 3.2 Deploy Your App
1. Click **Create app**
2. Fill in:
   - **Repository**: `YOUR_USERNAME/online_mcq_test`
   - **Branch**: `main`
   - **Main file path**: `main.py`
3. Click **Deploy**

⏳ **Wait 5-10 minutes** for deployment to complete...

### 3.3 Add Secrets to Streamlit Cloud
1. Go to your deployed app on Streamlit Cloud
2. Click **Settings** (⚙️ gear icon) at top-right
3. Click **Secrets** section
4. Click **Edit secrets**
5. Paste this (replace DATABASE_URL with your NeonDB connection):
   ```toml
   DATABASE_URL = "postgresql://user:pass@ep-xxxx.neon.tech/db?sslmode=require"
   SECRET_KEY = "your-secret-key-12345"
   COLLEGE_NAME = "Your College Name"
   ACADEMIC_YEAR = "2024-2025"
   ENABLE_HTTPS = "True"
   SESSION_TIMEOUT = "3600"
   ```
6. Click **Save** ✅

### 3.4 Wait for Restart
App will automatically restart with new secrets. Wait 2-3 minutes.

---

## 🧪 STEP 4: Test Your Deployed App

### 4.1 Visit Your App
Your app is live at:
```
https://YOUR_USERNAME-online-mcq-test.streamlit.app
```

### 4.2 Test Login
Try logging in with:
- **Admin**: admin / Admin@123
- **Faculty**: faculty1 / Faculty@123
- **Student**: student01 / Student@001

### 4.3 Verify Database
1. Create a test as admin
2. Create a question as faculty
3. Take the test as student
4. Check if everything works

✅ **If all works, you're deployed!**

---

## ❌ TROUBLESHOOTING

### Problem: "git command not found"
**Solution**: Install Git from https://git-scm.com

### Problem: "Database connection error"
**Solution**: 
- Check DATABASE_URL in secrets.toml (local) and Streamlit Cloud Secrets
- Verify NeonDB is running
- Check connection string is correct

### Problem: App not updating after git push
**Solution**:
- Go to Streamlit Cloud dashboard
- Click **Rerun** or **Restart** button
- Wait 2-3 minutes

### Problem: "ModuleNotFoundError"
**Solution**: Wait 3-5 minutes, Streamlit Cloud is installing dependencies

### Problem: Can't login
**Solution**: Database may not be initialized yet. Check Streamlit Cloud logs.

---

## 📋 SUMMARY

| Step | Status | Time |
|------|--------|------|
| Get NeonDB Connection String | ⬜ TODO | 2 min |
| Update secrets.toml | ⬜ TODO | 1 min |
| Initialize Git | ⬜ TODO | 2 min |
| Push to GitHub | ⬜ TODO | 5 min |
| Deploy on Streamlit Cloud | ⬜ TODO | 10 min |
| Add Secrets to Streamlit | ⬜ TODO | 3 min |
| Test Deployed App | ⬜ TODO | 5 min |
| **TOTAL** | | **30 min** |

---

## 🎉 YOU'RE DONE!

Once all steps are complete:
✅ Code is on GitHub
✅ App is deployed on Streamlit Cloud
✅ Database is on NeonDB
✅ Everything is live and accessible from anywhere!

### Your App URL:
```
https://YOUR_USERNAME-online-mcq-test.streamlit.app
```

### GitHub Repo:
```
https://github.com/YOUR_USERNAME/online_mcq_test
```

---

## 📞 NEED HELP?

- **Streamlit Docs**: https://docs.streamlit.io/deploy
- **NeonDB Docs**: https://neon.tech/docs
- **GitHub Help**: https://docs.github.com

**Happy Deploying! 🚀**
