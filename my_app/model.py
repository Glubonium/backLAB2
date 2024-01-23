from my_app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=False)
    password = db.Column(db.String(length=255), nullable=False)
    records = db.relationship("Record", back_populates="user", lazy="dynamic")
    income_accounting = db.relationship("IncomeAccounting", back_populates="user", uselist=False, primaryjoin="User.id == IncomeAccounting.user_id")

class IncomeAccounting(db.Model):
    __tablename__ = "income_accounting"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    balance = db.Column(db.Float(precision=2), default=0.0, nullable=False)
    user = db.relationship("User", back_populates="income_accounting", uselist=False, primaryjoin="User.id == IncomeAccounting.user_id")

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=False)
    record = db.relationship("Record", back_populates="category", lazy="dynamic")
class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float(precision=2), unique=False, nullable=False)
    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="record")
