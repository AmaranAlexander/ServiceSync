# ServiceSync

**Internal service management for automotive shops, lube centers, and service centers.**

ServiceSync is a full-stack web application built for front desk staff, service advisors, mechanics, and managers to coordinate daily shop operations — from vehicle intake to job completion and customer pickup.

---

## Features

- **Service Ticket Management** — Create, assign, update, and close tickets with full status history and audit trail
- **Customer & Vehicle Records** — Store contact info, vehicle details (VIN, plate, mileage), and full service history per vehicle
- **Technician Assignment** — Assign jobs to mechanics, track workload per technician in real time
- **Priority & Urgency Flags** — Mark tickets as High or Critical; urgent jobs surface at the top of every view
- **Service Notes** — Add timestamped internal notes to any ticket; track who wrote what and when
- **Role-Based Access** — Three roles with enforced permissions: Manager, Front Desk, and Mechanic
- **Live Dashboard** — KPI cards for open tickets, by-status counts, urgent jobs, mechanic workload, and completed-today count
- **Search & Filter** — Search by customer name, license plate, or ticket number; filter by status, urgency, or assigned mechanic
- **Multi-Shop Support** — Any team can sign up, create a shop, and share a join code with staff; data is fully isolated per shop

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, Flask 3 |
| ORM | Flask-SQLAlchemy 3, Flask-Migrate (Alembic) |
| Auth | Flask-Login, Werkzeug password hashing |
| Forms | Flask-WTF, WTForms |
| Database | PostgreSQL (production) / SQLite (development) |
| Frontend | Jinja2 templates, Bootstrap 5, Bootstrap Icons |

---

## Project Structure

```
webapp/
├── app/
│   ├── __init__.py          # App factory
│   ├── models/
│   │   ├── shop.py          # Shop / multi-tenant model
│   │   ├── user.py          # User + Role constants
│   │   ├── customer.py      # Customer records
│   │   ├── vehicle.py       # Vehicle records
│   │   ├── ticket.py        # ServiceTicket, StatusHistory, enums
│   │   └── note.py          # ServiceNote
│   ├── routes/
│   │   ├── auth.py          # Login, register
│   │   ├── dashboard.py     # Dashboard views (manager & mechanic)
│   │   ├── tickets.py       # Full ticket CRUD + status/notes
│   │   ├── customers.py     # Customer & vehicle CRUD
│   │   ├── mechanics.py     # Mechanic workload views
│   │   └── shop.py          # Shop settings, team management
│   ├── forms/
│   │   ├── auth.py
│   │   ├── register.py
│   │   ├── ticket.py
│   │   └── customer.py
│   ├── services/
│   │   └── dashboard.py     # Dashboard metric queries
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── tickets/
│   │   ├── customers/
│   │   ├── mechanics/
│   │   └── shop/
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── config/
│   └── config.py            # Dev / prod / test configs
├── migrations/              # Alembic migrations
├── run.py                   # Entry point
├── seed.py                  # Demo data seeder
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or SQLite for local development)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/AmaranAlexander/ServiceSync.git
cd ServiceSync

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY
```

### Database (PostgreSQL)

```bash
createdb servicesync_dev

flask db upgrade

python seed.py
```

### Database (SQLite — no setup needed)

The app defaults to SQLite if `DATABASE_URL` is not set. Just run:

```bash
python seed.py
```

### Run

```bash
python run.py
# → http://localhost:5000
```

---

## Demo Credentials

The seed script creates a demo shop called **Riverside Auto Service** with these accounts:

| Role | Username | Password |
|------|----------|----------|
| Manager | `admin` | `admin123` |
| Front Desk | `jmorris` | `password` |
| Mechanic | `tdiaz` | `password` |
| Mechanic | `lchen` | `password` |

**Demo shop join code:** `DEMO1234`

To test the registration flow, visit `/auth/register` and either create a new shop or join the demo shop with the code above.

---

## Role Permissions

| Action | Manager | Front Desk | Mechanic |
|--------|---------|------------|---------|
| Full dashboard | Yes | Yes | Own jobs only |
| Create / edit tickets | Yes | Yes | No |
| Delete tickets | Yes | No | No |
| Update ticket status | Yes | Yes | Own jobs only |
| Add notes | Yes | Yes | Own jobs only |
| Manage customers & vehicles | Yes | Yes | No |
| View mechanic workload | Yes | Yes | Own view |
| Shop settings & role management | Yes | No | No |

---

## Multi-Tenant / Multi-Shop

ServiceSync supports multiple independent shops on the same deployment.

- **Create a shop** — Register and choose "Create a new shop." You become the manager and receive a unique join code.
- **Join a shop** — Register and choose "Join an existing shop," then enter the join code from your manager.
- All data (tickets, customers, vehicles, staff) is fully isolated per shop.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | `dev-secret-change-in-production` |
| `DATABASE_URL` | SQLAlchemy DB URI | SQLite (local file) |
| `FLASK_ENV` | `development` or `production` | `development` |

---

## Future Improvements

- SMS/email notifications when a vehicle is ready for pickup
- Parts inventory tracking linked to service tickets
- Customer-facing ticket status portal
- PDF invoice / work order generation
- Reporting: revenue, avg turnaround time, technician throughput
