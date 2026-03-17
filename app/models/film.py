from app import db
from datetime import datetime

class Film(db.Model):
    __tablename__ = 'films'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    genre       = db.Column(db.String(100), nullable=True)
    year        = db.Column(db.Integer, nullable=True)
    poster_url  = db.Column(db.String(500), nullable=True)
    video_url   = db.Column(db.String(500), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Film {self.title}>'
