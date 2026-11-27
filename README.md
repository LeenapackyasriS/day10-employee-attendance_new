# Day 10 Employee Attendance – Flask + MySQL

## Features
- Add/list employees; validate required fields and duplicate emails
- Check in and check out once per employee per day
- Today's attendance dashboard
- Employee attendance history
- Calculate elapsed hours between check-in and check-out
- Responsive HTML/CSS/JavaScript frontend

## Requirements
Python 3.10+ (Python 3.12 recommended), MySQL or XAMPP MariaDB.

## 1. Create database
Start MySQL in XAMPP. Import `backend/create_database.sql` in phpMyAdmin.

## 2. Start backend (PowerShell)
Open PowerShell in the `backend` folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` if your MySQL username/password differs. Default assumes XAMPP root with no password:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/day10_attendance
SECRET_KEY=replace-this-with-a-long-random-secret
```

Run:

```powershell
python app.py
```

Backend: http://127.0.0.1:5000

## 3. Start frontend
Open a second PowerShell window in `frontend`:

```powershell
py -3.12 -m http.server 5500
```

Open http://127.0.0.1:5500

## API routes

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| POST | `/api/employees` | Add employee |
| GET | `/api/employees` | List employees |
| POST | `/api/attendance/check-in` | Check in |
| POST | `/api/attendance/check-out` | Check out |
| GET | `/api/attendance/today` | Today's attendance |
| GET | `/api/attendance/employee/<employee_id>` | Attendance history |

### Add employee JSON
```json
{"name":"Anitha Kumar","email":"anitha@example.com","department":"Development"}
```

### Check-in/check-out JSON
```json
{"employee_id":1}
```

## Learning-project limitations
This is a Day 10 teaching version, not production-ready. The frontend supplies employee_id; a production app must authenticate the user and derive identity from a verified session/token. Hours are elapsed time only; no break deductions, shift rules, late marks, overtime or overnight shift handling. The server's local date/time is used. `db.create_all()` creates missing tables but does not migrate existing schemas. For production, disable debug mode, use strong secrets, authentication/authorization, HTTPS, validation, logging and backups.
