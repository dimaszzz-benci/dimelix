from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app import db
from app.models.film import Film

# Fungsi helper — cek apakah user adalah admin
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Akses ditolak! Hanya admin yang boleh masuk.', 'danger')
            return redirect(url_for('film.browse'))
        return f(*args, **kwargs)
    return decorated

def show_dashboard():
    if not current_user.is_admin:
        flash('Akses ditolak!', 'danger')
        return redirect(url_for('film.browse'))

    films = Film.query.order_by(Film.created_at.desc()).all()
    return render_template('admin/dashboard.html', films=films)

def show_add_film():
    if not current_user.is_admin:
        return redirect(url_for('film.browse'))
    return render_template('admin/add_film.html')

def do_add_film():
    if not current_user.is_admin:
        return redirect(url_for('film.browse'))

    title       = request.form.get('title')
    description = request.form.get('description')
    genre       = request.form.get('genre')
    year        = request.form.get('year')
    poster_url  = request.form.get('poster_url')
    video_url   = request.form.get('video_url')

    new_film = Film(
        title=title,
        description=description,
        genre=genre,
        year=int(year) if year else None,
        poster_url=poster_url,
        video_url=video_url
    )

    db.session.add(new_film)
    db.session.commit()

    flash(f'Film "{title}" berhasil ditambahkan!', 'success')
    return redirect(url_for('admin.dashboard'))

def show_edit_film(film_id):
    if not current_user.is_admin:
        return redirect(url_for('film.browse'))
    film = Film.query.get_or_404(film_id)
    return render_template('admin/edit_film.html', film=film)

def do_edit_film(film_id):
    if not current_user.is_admin:
        return redirect(url_for('film.browse'))

    film = Film.query.get_or_404(film_id)

    film.title       = request.form.get('title')
    film.description = request.form.get('description')
    film.genre       = request.form.get('genre')
    film.year        = request.form.get('year')
    film.poster_url  = request.form.get('poster_url')
    film.video_url   = request.form.get('video_url')

    db.session.commit()

    flash(f'Film "{film.title}" berhasil diupdate!', 'success')
    return redirect(url_for('admin.dashboard'))

def do_delete_film(film_id):
    if not current_user.is_admin:
        return redirect(url_for('film.browse'))

    film = Film.query.get_or_404(film_id)
    db.session.delete(film)
    db.session.commit()

    flash('Film berhasil dihapus!', 'success')
    return redirect(url_for('admin.dashboard'))
