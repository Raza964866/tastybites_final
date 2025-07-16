# TastyBites Deployment Guide - PythonAnywhere

## What You Have Ready:
✅ **Backup**: Your original project is safely backed up to `D:\tastybites_backup`
✅ **Database Export**: Your MySQL database exported to `database_export.sql`
✅ **Project Files**: All your Flask application files
✅ **Configuration**: Production config file created

## Step-by-Step Deployment:

### 1. Create PythonAnywhere Account
- Go to https://www.pythonanywhere.com/
- Sign up for a **Free account**
- Choose a username (this will be part of your website URL)

### 2. Upload Your Project
- In PythonAnywhere dashboard, go to **Files**
- Create a new folder: `tastybites_final`
- Upload your entire `tastybites` folder
- Upload `wsgi.py` and `config_production.py`

### 3. Set Up MySQL Database
- Go to **Databases** tab
- Click **Create database**
- Database name: `tastybites_db` (will become `yourusername$tastybites_db`)
- Note down the connection details

### 4. Import Your Database
- Go to **Database** tab
- Click on your database
- Use **Import** feature to upload your `database_export.sql`

### 5. Configure Your App
- Go to **Web** tab
- Click **Add a new web app**
- Choose **Flask**
- Set the source code path to: `/home/yourusername/tastybites_final/tastybites`
- Set the WSGI file path to: `/home/yourusername/tastybites_final/wsgi.py`

### 6. Update Configuration
- Edit `config_production.py` with your actual PythonAnywhere details
- Update the database URL with your username and password

### 7. Install Dependencies
- Go to **Consoles** tab
- Start a **Bash console**
- Navigate to your project: `cd tastybites_final/tastybites`
- Install requirements: `pip3.10 install --user -r requirements.txt`

### 8. Test Your App
- Go to **Web** tab
- Click **Reload** your web app
- Visit your website: `https://yourusername.pythonanywhere.com`

## Your Files Are Safe!
- Original project: `D:\tastybites_final` (unchanged)
- Backup: `D:\tastybites_backup`
- Database export: `D:\tastybites_final\database_export.sql`

## Need Help?
- PythonAnywhere has excellent documentation
- Your local project remains untouched
- You can always restore from backup if needed

## What We've Done:
1. ✅ Created a complete backup
2. ✅ Exported your MySQL database
3. ✅ Created production configuration
4. ✅ Created WSGI file for deployment
5. ✅ Prepared deployment guide
