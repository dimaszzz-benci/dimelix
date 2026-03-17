import os

class Config:
    # Secret key untuk keamanan session
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dimelix-secret-key-2024'

    # Koneksi database
    # Kita pakai SQLite dulu (cocok untuk HP)
    # Nanti gampang diganti ke MySQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dimelix.db'

    # Matiin fitur tracking perubahan (boros memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
