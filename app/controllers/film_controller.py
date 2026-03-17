from flask import render_template, request
from app.models.film import Film

def show_browse():
    # Ambil semua film dari database
    films = Film.query.order_by(Film.created_at.desc()).all()
    return render_template('films/browse.html', films=films)

def show_detail(film_id):
    # Ambil 1 film, kalau tidak ada → 404
    film = Film.query.get_or_404(film_id)
    return render_template('films/detail.html', film=film)

def show_watch(film_id):
    film = Film.query.get_or_404(film_id)
    return render_template('films/watch.html', film=film)

def do_search():
    # Ambil keyword dari URL: /search?q=naruto
    keyword = request.args.get('q', '')

    # SQL LIKE → cari judul yang mengandung keyword
    films = Film.query.filter(
        Film.title.ilike(f'%{keyword}%')
    ).all()

    return render_template('films/browse.html', films=films, keyword=keyword)
