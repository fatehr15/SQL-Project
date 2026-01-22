# Demo Database

This directory contains the SQLite demo database for testing the application without PostgreSQL setup.

## Quick Start

**Run the application in demo mode:**

```powershell
# From project root
python "Part2\Python App\run_demo.py"
```

Or:

```powershell
python "Part2\Python App\App.py" --demo
```

## What is Demo Mode?

- **No PostgreSQL required** - Uses SQLite (file-based database)
- **No setup needed** - Database is created automatically
- **Sample data included** - Pre-populated with test data
- **Full functionality** - All 6 modules work the same way

## Database Location

The demo database is stored at:
```
demo/university_demo.db
```

## Features

The demo database includes:
- ✅ All required tables (Department, Student, Instructor, Course, etc.)
- ✅ Sample data for testing
- ✅ All CRUD operations work
- ✅ Reservations, Marks, Attendance modules functional
- ✅ Reporting queries work
- ✅ Audit logging works

## Reset Demo Database

To reset the demo database, simply delete the file:
```powershell
Remove-Item "demo\university_demo.db"
```

Then run the app in demo mode again - it will recreate everything.

## Switching Between Demo and PostgreSQL

- **Demo mode**: `python "Part2\Python App\run_demo.py"`
- **PostgreSQL mode**: `python "Part2\Python App\App.py"`

If PostgreSQL connection fails, the app will offer to switch to demo mode automatically.

