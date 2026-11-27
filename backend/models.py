from datetime import datetime, date
from extensions import db

class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    attendances = db.relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("employee_id", "attendance_date", name="uq_employee_day"),)
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    attendance_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    employee = db.relationship("Employee", back_populates="attendances")
