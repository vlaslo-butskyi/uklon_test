from datetime import datetime

from src import db


class GeoRecords(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Float, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    datetime = db.Column(db.TIMESTAMP(), default=datetime.utcnow)
