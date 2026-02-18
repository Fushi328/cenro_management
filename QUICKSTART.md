# Quick Start Guide

## Step 1: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues installing `mysqlclient` on Windows, you can skip it for now since the project defaults to SQLite for development.

## Step 3: Run Migrations

```bash
python manage.py migrate
```

## Step 4: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

When prompted:
- Enter a username (e.g., `admin`)
- Enter an email (optional)
- Enter a password
- Confirm the password

**Important:** After creating the superuser, you need to set their role to ADMIN. You can do this via:
1. Django admin panel at `/admin/` after logging in
2. Or via Python shell: `python manage.py shell` then:
   ```python
   from accounts.models import User
   admin = User.objects.get(username='admin')
   admin.role = User.Role.ADMIN
   admin.is_approved = True
   admin.save()
   ```

## Step 5: Run the Server

```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Step 6: Access the Application

1. Go to **http://127.0.0.1:8000/**
2. You'll be redirected to the login page
3. Login with your superuser credentials
4. Navigate to Django admin (`/admin/`) to set your role to ADMIN if needed

## Default User Roles

- **Admin** - Full system access
- **Staff** - View assigned schedules, complete requests
- **Consumer** - Submit requests, view history

## First Steps After Setup

1. **Set Admin Role**: Make sure your superuser has `role=ADMIN` and `is_approved=True`
2. **Create Staff Accounts**: Use "Staff Management" → "Register Staff" (admin only)
3. **Approve Staff**: Go to "Staff Management" → "Staff Approvals" to approve staff accounts
4. **Test User Account Registration**: Register a consumer account at `/accounts/register/consumer/`
5. **Submit Test Request**: Login as consumer and create a service request

## Troubleshooting

### Issue: `mysqlclient` installation fails
**Solution**: The project uses SQLite by default. You don't need MySQL for development. If you see import errors, comment out `mysqlclient` in `requirements.txt` temporarily.

### Issue: Template not found errors
**Solution**: Make sure you've created the `templates/` and `static/` directories in the project root.

### Issue: Static files not loading
**Solution**: Run `python manage.py collectstatic` (optional for development, Django serves static files automatically in DEBUG mode).

### Issue: Permission denied errors
**Solution**: Make sure your user account has the correct role set (ADMIN, STAFF, or CONSUMER) and `is_approved=True` (except for ADMIN).
