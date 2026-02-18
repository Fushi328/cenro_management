Management System for the City Environmental and Natural Resources Office (CENRO) of Bayawan
===========================================================================================

This is a web-based management system built with **Python** and **Django** for the CENRO office of Bayawan.
It manages **septage declogging** and **grass cutting services**, including:

- User registration and admin approvals
- Service request submission and tracking
- Multi-year service history with 4-year declogging cycle validation
- Fee computation and payment confirmation
- Scheduling and notifications

## Tech Stack

- **Backend**: Python, Django
- **Database (production)**: MySQL
- **Database (development/offline)**: SQLite
- **Frontend**: HTML5, modern CSS (eco-friendly theme), JavaScript

## Project Structure

- `cenro_mgmt/` – Django project settings and configuration
- `accounts/` – Custom user model, authentication, and role-based access (Consumer, Admin, Staff)
- `services/` – Service requests, payment handling, cycle validation, history
- `scheduling/` – Scheduling by barangay/date and staff assignment
- `dashboard/` – Dashboard overview, summary cards, and calendar
- `templates/` – Shared and app-specific templates
- `static/` – CSS, JS, and images for the eco-themed UI

## Getting Started

### 1. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Database configuration

By default, the project uses **SQLite** for local development.

To use **MySQL** (recommended for production), set the following environment variables:

- `USE_MYSQL=1`
- `MYSQL_NAME`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_PORT` (default: `3306`)

### 4. Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

### Default Roles

- **Admin** – Full access, approves accounts, validates requests, computes fees, schedules services, and manages staff.
- **Staff** – Admin-approved accounts, can view assigned schedules and update completion status.
- **Consumer** – Can register, submit service requests, upload receipts, and view history.

Role-based access control is enforced in views and templates.

## Notes

- The UI uses a **desktop-first**, eco-friendly, government-ready design with a fixed left sidebar and card-based layout.
- Map/GPS support is scaffolded via latitude/longitude fields on client addresses; you can plug in a mapping provider (e.g., Leaflet, Google Maps) as needed.
- A placeholder is included for future online payments integration.

