import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dimelix-secret-key-2024'

    # Railway akan otomatis kasih DATABASE_URL
    # kalau kita tambah MySQL service
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        # Production: pakai MySQL dari Railway
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Development: pakai SQLite lokal
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dimelix.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
