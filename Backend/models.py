from extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Organization(db.Model):
    __tablename__ = 'organization'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    users = db.relationship('User', backref='organization', lazy=True)

    def __repr__(self):
        return f"<Organization {self.name}>"


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending') 
    requested_at = db.Column(db.DateTime, server_default=db.func.now())
    approved_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='loans')


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    status = db.Column(db.String(20), default='pending') 

    user = db.relationship('User', backref='contributions')
    organization = db.relationship('Organization', backref='contributions')


class ContributionSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



