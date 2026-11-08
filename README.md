# Eve — Smart Scheduling & Team Coordination Platform

Eve is a team coordination and shift-scheduling web platform developed for **IM2 (Information Management 2)**. It showcases relational database design, Django vertical-slice architecture, and practical SQL operations (such as `INNER JOIN` and `LEFT JOIN` queries).

---

## Application Workflow

```text
Register / log in
       ↓
Open the home dashboard
       ↓
Create or join a company
       ↓
Get a company role: Owner, Manager, or Staff
       ↓
Create an event under the company
       ↓
Assign company members to the event
       ↓
Set each assignment’s role, location, time, and status
       ↓
Track event and assignment progress
```

---

## Implemented Features

1. **Authentication & Onboarding**:
   - Secure registration creating Django `User`, `Profile`, `UserSettings`, and company ownership records atomically.
   - Login with email or username, password verification, flash alerts, and logout.
2. **Home Dashboard**:
   - High-level metrics: user's companies, upcoming events count, personal assigned shifts, and shift confirmation percentage.
   - Quick preview of user's personal upcoming shift assignments with direct status confirmation.
   - Company and role directory preview.
3. **Company & Role Management (`/events/companies/`)**:
   - **Create a Company**: Creator automatically becomes `OWNER`.
   - **Join a Company**: Browse available companies and join as `STAFF`.
   - **Role Administration**: Owners and Managers can promote or demote members across roles (`OWNER`, `MANAGER`, `STAFF`) and remove members with safeguards for the sole owner.
4. **Event Scheduling (`/events/`)**:
   - Create events linked to specific companies with title, description, date, start time, end time, location, and status (`DRAFT`, `UPCOMING`, `COMPLETED`, `CANCELLED`).
   - Filter events by company and lifecycle status.
5. **Shift Assignment & Coordination (`/events/<event_id>/`)**:
   - Owners and Managers can assign unassigned company members to shifts.
   - Specify `assigned_role` (e.g. Usher, Technician, Security, Cashier), `assigned_location`, `start_time`, `end_time`, and status.
   - Staff members can view their personal assignment and click **"Confirm Attendance"** or **"Mark Shift Completed"**.
6. **Progress Tracking**:
   - Live visual progress bars and metrics on both the Event detail page and Home Dashboard calculating confirmation and completion rates.
7. **SQL JOIN Demonstration (`/events/joins/`)**:
   - Live interactive database view and CLI command demonstrating `INNER JOIN` vs `LEFT JOIN` on `events_event` and `events_eventassignment`.

---

## Relational Database Schema

```text
+------------------+         1 : N         +----------------------+
|     Company      | --------------------> |    CompanyMember     |
+------------------+                       +----------------------+
        | 1                                           | 1
        |                                             |
        | N                                           | N
        v                                             v
+------------------+         1 : N         +----------------------+
|      Event       | --------------------> |   EventAssignment    |
+------------------+                       +----------------------+
```

---

## Architecture & Directory Structure

```text
eve_project/
├── apps/
│   ├── events/          # Companies, Roles, Events, Assignments & SQL JOIN Demo
│   │   ├── management/commands/
│   │   │   ├── join_demo.py       # Terminal SQL JOIN demo command
│   │   │   └── seed_join_demo.py  # Relational test data seeder
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests.py
│   ├── home/            # Dashboard landing page & workflow metrics
│   ├── login/           # Authentication and logout views
│   ├── register/        # Registration flow and initial setup
│   ├── userprofile/     # Profile model and editing interface
│   └── usersettings/    # Preference toggles (Dark Mode, Email Notifications)
├── eve_project/         # Django project settings and root routing
├── static/              # CSS stylesheet and UI branding
├── templates/           # Django HTML templates
├── manage.py
└── requirements.txt     # Python dependencies
```

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup Virtual Environment

```bash
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Relational Data

```bash
python manage.py migrate
python manage.py seed_join_demo
```

### 5. Run Terminal SQL Demo

```bash
python manage.py join_demo
```

### 6. Run the Test Suite

```bash
python manage.py test
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## License

This project is licensed under the MIT License for educational and demonstration purposes.
