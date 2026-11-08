# Eve — Smart Scheduling & Team Coordination Platform

Eve is a team coordination and shift-scheduling web platform developed for **IM2 (Information Management 2)**. It showcases relational database design, Django vertical-slice architecture, and practical SQL operations (such as `INNER JOIN` and `LEFT JOIN` queries).

---

## Features

- **Authentication & Onboarding**:
  - Secure registration creating Django `User`, `Profile`, `UserSettings`, and company ownership records in an atomic transaction.
  - Credential authentication with user session management and flash alerts.
  - Graceful logout.
- **Relational Domain Models & SQL Demonstrations**:
  - Domain structure covering **Companies**, **Company Members** (Owner, Manager, Staff), **Events**, and **Event Assignments**.
  - Interactive SQL demonstration (`/events/joins/`) showcasing the behavioral difference between **`INNER JOIN`** and **`LEFT JOIN`**.
  - Management commands for seeding demo relational data and inspecting query outputs in the terminal.
- **User Profile & Preferences**:
  - Profile management for personal information, bio, and associated company memberships.
  - User settings for interface preferences (e.g. Dark Mode) and notification toggles.
- **Modern Minimalist UI**:
  - Responsive design powered by Bootstrap 5.3, Bootstrap Icons, and custom CSS.

---

## Architecture & Directory Structure

Eve employs a modular vertical-slice application layout:

```text
eve_project/
├── apps/
│   ├── events/          # Company, Member, Event, & Assignment models + SQL JOIN demo
│   │   └── management/commands/
│   │       ├── join_demo.py       # Terminal SQL JOIN demo command
│   │       └── seed_join_demo.py  # Relational test data seeder
│   ├── home/            # Dashboard landing page
│   ├── login/           # Authentication and logout views
│   ├── register/        # Registration flow and initial setup
│   ├── userprofile/     # Profile model and editing interface
│   └── usersettings/    # Preference toggles
├── eve_project/         # Django project settings and root routing
├── static/              # CSS stylesheet and assets
├── templates/           # Django HTML templates
├── manage.py
└── requirements.txt     # Python dependencies
```

---

## Database Design & SQL Joins

### Relational Schema

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

### SQL JOIN Operations

- **INNER JOIN**: Returns only events that have at least one assigned company member. Events without assignments (e.g. *Charity Gala*) are excluded.
- **LEFT JOIN**: Returns all events regardless of assignment status. Events with no assignments display `NULL` for assignment attributes.

---

## Getting Started

### 1. Prerequisites
- Python 3.11 or higher
- Git

### 2. Clone Repository & Setup Virtual Environment

```bash
git clone https://github.com/Leandrozxc/eve_project.git
cd eve_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create or inspect `.env` in the project root:

```ini
# Local SQLite database (default)
DATABASE_URL=sqlite:///db.sqlite3

# Or PostgreSQL (e.g., Supabase / Neon / Local Postgres):
# DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Seed Demo Data for SQL Joins

```bash
python manage.py seed_join_demo
```

### 7. Run Terminal SQL Demo

```bash
python manage.py join_demo
```

### 8. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## Running Automated Tests

Run the test suite across all apps:

```bash
python manage.py test
```

---

## License

This project is licensed under the MIT License for educational and demonstration purposes.
