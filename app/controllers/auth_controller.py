from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app import db, bcrypt
from app.models.user import User

def show_login():
    return render_template('auth/login.html')

def show_register():
    return render_template('auth/register.html')

def do_login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        # Cari user berdasarkan email
        user = User.query.filter_by(email=email).first()

        # Cek apakah user ada & password cocok
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('film.browse'))
        else:
            flash('Email atau password salah!', 'danger')

    return render_template('auth/login.html')

def do_register():
    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')

        # Hash password sebelum disimpan
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        # Buat user baru
        new_user = User(
            username=username,
            email=email,
            password=hashed_pw
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

def do_logout():
    logout_user()
    return redirect(url_for('auth.login'))
