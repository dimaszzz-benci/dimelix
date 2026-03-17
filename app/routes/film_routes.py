from flask import Blueprint
from app.controllers.film_controller import (
    show_browse,
    show_detail,
    show_watch,
    do_search
)

film_bp = Blueprint('film', __name__)

# Halaman utama / browse semua film
@film_bp.route('/')
@film_bp.route('/browse')
def browse():
    return show_browse()

# Halaman detail film berdasarkan id
@film_bp.route('/film/<int:film_id>')
def detail(film_id):
    return show_detail(film_id)

# Halaman watch/streaming
@film_bp.route('/watch/<int:film_id>')
def watch(film_id):
    return show_watch(film_id)

# Search film
@film_bp.route('/search')
def search():
    return do_search()
