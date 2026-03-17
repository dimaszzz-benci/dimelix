from flask import Blueprint
from app.controllers.auth_controller import (
    show_login,
    show_register,
    do_login,
    do_register,
    do_logout
)

# Buat blueprint dengan prefix '/auth'
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# GET  /auth/login    → tampilkan form login
# POST /auth/login    → proses login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return do_login()

# GET  /auth/register → tampilkan form register
# POST /auth/register → proses register
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return do_register()

# GET  /auth/logout   → proses logout
@auth_bp.route('/logout')
def logout():
    return do_logout()
