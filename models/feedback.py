from . import db
from datetime import datetime


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    email = db.Column(db.String(255), nullable=False)

    rating = db.Column(db.Integer, nullable=False)

    message = db.Column(db.Text, nullable=False)
    
    feedback_category = db.Column(
    db.String(100),
    nullable=True
)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )