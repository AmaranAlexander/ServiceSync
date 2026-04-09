# ServiceSync — Setup Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 14+

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env — set your DATABASE_URL and a real SECRET_KEY

# 3. Create database
createdb servicesync_dev

# 4. Run migrations
flask db init
flask db migrate -m "initial schema"
flask db upgrade

# 5. Seed demo data
python seed.py

# 6. Run the app
python run.py
# → http://localhost:5000
```

## Login Credentials (demo)
| Role       | Username | Password  |
|------------|----------|-----------|
| Manager    | admin    | admin123  |
| Front Desk | jmorris  | password  |
| Mechanic   | tdiaz    | password  |
| Mechanic   | lchen    | password  |

## Role Permissions
| Feature                  | Manager | Front Desk | Mechanic |
|--------------------------|---------|------------|----------|
| View dashboard (full)    | ✓       | ✓          | own view |
| Create/edit tickets      | ✓       | ✓          | ✗        |
| Delete tickets           | ✓       | ✗          | ✗        |
| Update status            | ✓       | ✓          | own jobs |
| Add notes                | ✓       | ✓          | own jobs |
| Manage customers/vehicles| ✓       | ✓          | ✗        |
| View mechanic workload   | ✓       | ✓          | own view |
