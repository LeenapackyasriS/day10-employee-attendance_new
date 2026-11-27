import os
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Employee, Attendance

load_dotenv()

def employee_json(e):
    return {"id": e.id, "name": e.name, "email": e.email, "department": e.department,
            "created_at": e.created_at.isoformat() if e.created_at else None}

def attendance_json(r):
    hours = None
    if r.check_in and r.check_out:
        seconds = (r.check_out - r.check_in).total_seconds()
        hours = str(Decimal(str(seconds / 3600)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {"id": r.id, "employee_id": r.employee_id, "employee_name": r.employee.name,
            "email": r.employee.email, "attendance_date": r.attendance_date.isoformat(),
            "check_in": r.check_in.strftime("%H:%M:%S") if r.check_in else None,
            "check_out": r.check_out.strftime("%H:%M:%S") if r.check_out else None,
            "working_hours": hours}

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "mysql+pymysql://root:@127.0.0.1:3306/day10_attendance")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")
    CORS(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return jsonify({"message": "Day 10 Employee Attendance API is running"})

    @app.post("/api/employees")
    def add_employee():
        data = request.get_json(silent=True) or {}
        name, email = (data.get("name") or "").strip(), (data.get("email") or "").strip().lower()
        department = (data.get("department") or "").strip()
        if not name or not email:
            return jsonify({"error": "Name and email are required"}), 400
        if "@" not in email or "." not in email.split("@")[-1]:
            return jsonify({"error": "Enter a valid email address"}), 400
        employee = Employee(name=name, email=email, department=department or None)
        db.session.add(employee)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "An employee with this email already exists"}), 409
        return jsonify(employee_json(employee)), 201

    @app.get("/api/employees")
    def list_employees():
        return jsonify([employee_json(e) for e in Employee.query.order_by(Employee.id.desc()).all()])

    @app.post("/api/attendance/check-in")
    def check_in():
        data = request.get_json(silent=True) or {}
        employee_id = data.get("employee_id")
        if not employee_id:
            return jsonify({"error": "employee_id is required"}), 400
        employee = db.session.get(Employee, employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        today = date.today()
        record = Attendance.query.filter_by(employee_id=employee.id, attendance_date=today).first()
        if record and record.check_in:
            return jsonify({"error": "Employee has already checked in today"}), 409
        if record is None:
            record = Attendance(employee_id=employee.id, attendance_date=today)
            db.session.add(record)
        record.check_in = datetime.now()
        db.session.commit()
        return jsonify(attendance_json(record))

    @app.post("/api/attendance/check-out")
    def check_out():
        data = request.get_json(silent=True) or {}
        employee_id = data.get("employee_id")
        if not employee_id:
            return jsonify({"error": "employee_id is required"}), 400
        employee = db.session.get(Employee, employee_id)
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        record = Attendance.query.filter_by(employee_id=employee.id, attendance_date=date.today()).first()
        if not record or not record.check_in:
            return jsonify({"error": "Please check in before checking out"}), 400
        if record.check_out:
            return jsonify({"error": "Employee has already checked out today"}), 409
        record.check_out = datetime.now()
        db.session.commit()
        return jsonify(attendance_json(record))

    @app.get("/api/attendance/today")
    def today_attendance():
        rows = Attendance.query.filter_by(attendance_date=date.today()).order_by(Attendance.id.desc()).all()
        return jsonify([attendance_json(r) for r in rows])

    @app.get("/api/attendance/employee/<int:employee_id>")
    def employee_history(employee_id):
        if not db.session.get(Employee, employee_id):
            return jsonify({"error": "Employee not found"}), 404
        rows = Attendance.query.filter_by(employee_id=employee_id).order_by(Attendance.attendance_date.desc()).all()
        return jsonify([attendance_json(r) for r in rows])

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Route not found"}), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500
    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True, port=5000)
