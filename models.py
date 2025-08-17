import datetime
from database import db
from sqlalchemy import Enum


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)  # hashed password
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    file_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA256 hash
    originality_status = db.Column(
        Enum("Pending", "Original", "Duplicate", "Fake", name="originality_status_enum"),
        default="Pending",
        nullable=False
    )
    uploaded_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("documents", lazy=True))
    
    # New verification fields (optional - add these if you want detailed verification data)
    verification_score = db.Column(db.Float, default=0.0)  # Score out of 100
    verification_details = db.Column(db.Text)  # JSON string with detailed results
    verified_at = db.Column(db.DateTime)