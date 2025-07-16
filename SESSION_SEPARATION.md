# Session Separation Between Main Website and Admin Panel

## Overview
The TastyBites application has been designed with **separate session management** for the main website and admin panel to ensure that admin logins do not interfere with regular user sessions.

## How It Works

### 1. Separate Session Cookies
- **Main Website**: Uses session cookie named `main_session`
- **Admin Panel**: Uses session cookie named `admin_session`

### 2. Different Applications
- **Main Website**: Runs on port 5000 (`http://127.0.0.1:5000`)
- **Admin Panel**: Runs on port 5001 (`http://127.0.0.1:5001`)

### 3. Independent Authentication
- Admin login/logout does **NOT** affect main website users
- Main website login/logout does **NOT** affect admin panel
- Each application maintains its own user session state

## Benefits

### ✅ What This Fixes
- **No Cross-Interference**: Admin login won't log out main website users
- **Secure Separation**: Admin panel is completely isolated from main website
- **Independent Sessions**: Each application manages its own user authentication
- **Concurrent Usage**: Admin can be logged into admin panel while users are logged into main website

### ✅ User Experience
- **Regular Users**: Can stay logged into main website regardless of admin activity
- **Admin Users**: Can access admin panel without affecting main website users
- **Easy Navigation**: Admin can visit main website via "View Site" link without logging out

## Implementation Details

### Session Cookie Configuration
```python
# Main Website (app.py)
app.config['SESSION_COOKIE_NAME'] = 'main_session'

# Admin Panel (admin_app.py)
app.config['SESSION_COOKIE_NAME'] = 'admin_session'
```

### Flask-Login Configuration
Each application has its own Flask-Login manager:
- Separate user loaders
- Separate login views
- Separate session management

## Running Both Applications

### Method 1: Using the Script
```bash
python run_both.py
```

### Method 2: Manual (Two Terminals)
```bash
# Terminal 1 - Main Website
python -m tastybites.backend.app

# Terminal 2 - Admin Panel
python -m tastybites.admin_panel.admin_app
```

## Testing Session Separation

### Test Scenario 1: Admin Login
1. Go to main website: `http://127.0.0.1:5000`
2. Login as a regular user
3. Go to admin panel: `http://127.0.0.1:5001`
4. Login as admin
5. **Result**: Main website user remains logged in

### Test Scenario 2: Admin Logout
1. Have both admin and regular user logged in (from Test 1)
2. Logout from admin panel
3. Check main website
4. **Result**: Main website user remains logged in

### Test Scenario 3: Cross-Navigation
1. Login to admin panel
2. Click "View Site" link
3. **Result**: Opens main website in new tab, admin remains logged in admin panel

## Security Considerations

### ✅ What's Secure
- **Isolated Sessions**: Admin and user sessions are completely separate
- **Role-Based Access**: Admin panel only accessible to users with admin role
- **Separate Cookies**: Different session cookies prevent cross-contamination

### ✅ Additional Security
- CSRF Protection enabled on both applications
- Password hashing using secure methods
- Email verification for new users
- Admin role verification for admin access

## Troubleshooting

### Issue: Admin login affects main website
**Solution**: Ensure both applications are running on different ports with different session cookie names.

### Issue: Sessions not separating
**Solution**: Clear browser cookies and restart both applications.

### Issue: Admin can't access main website
**Solution**: Admin should use "View Site" link or manually navigate to `http://127.0.0.1:5000`.

## Files Modified
- `tastybites/backend/app.py` - Added `main_session` cookie name
- `tastybites/admin_panel/admin_app.py` - Added `admin_session` cookie name
- `run_both.py` - Script to run both applications

## Conclusion
This implementation ensures that the admin panel and main website operate independently, providing a better user experience and preventing authentication conflicts.
