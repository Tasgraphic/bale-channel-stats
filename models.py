from database import db
from datetime import datetime


class Channel(db.Model):

    __tablename__ = "channels"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    channel_id = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    platform = db.Column(
        db.String(50),
        default="bale"
    )

    status = db.Column(
        db.String(50),
        default="pending"
    )

    admin_id = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )