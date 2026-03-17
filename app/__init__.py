from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import Config

# Buat objek database, login manager, dan bcrypt
# Dibuat di luar create_app agar bisa dipakai di file lain
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    # Buat Flask app
    app = Flask(__name__)

    # Masukkan konfigurasi dari config.py
    app.config.from_object(Config)

    # Hubungkan db, login_manager, bcrypt ke app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Arahkan user ke halaman login kalau belum login
    login_manager.login_view = 'auth.login'

    # Daftarkan routes (nanti kita isi)
    from app.routes.auth_routes import auth_bp
from app.routes.film_routes import film_bp
from app.routes.admin_routes import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(film_bp)
app.register_blueprint(admin_bp)
    return app
