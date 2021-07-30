# models.py

from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    conf = db.Column(db.INT, default=0)
    blocked = db.Column(db.INT, default=0)
    role = db.Column(db.INT, db.ForeignKey('roles.id'), default=0)
    key = db.Column(db.String(64), default='')
    secret = db.Column(db.String(64), default='')


class PasswordRecoveries(UserMixin, db.Model):
    __tablename__ = 'password_recoveries'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    token = db.Column(db.String(64))
    used = db.Column(db.INT, default=0)
    time = db.Column(db.Integer)


class Confirmations(UserMixin, db.Model):
    __tablename__ = 'confirmations'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    token = db.Column(db.String(64))
    time = db.Column(db.Integer)
