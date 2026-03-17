from flask import Blueprint
from flask_login import login_required
from app.controllers.admin_controller import (
    show_dashboard,
    show_add_film,
    do_add_film,
    show_edit_film,
    do_edit_film,
    do_delete_film
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    return show_dashboard()

@admin_bp.route('/film/add', methods=['GET', 'POST'])
@login_required
def add_film():
    return show_add_film() if request.method == 'GET' else do_add_film()

@admin_bp.route('/film/edit/<int:film_id>', methods=['GET', 'POST'])
@login_required
def edit_film(film_id):
    return show_edit_film(film_id) if request.method == 'GET' else do_edit_film(film_id)

@admin_bp.route('/film/delete/<int:film_id>')
@login_required
def delete_film(film_id):
    return do_delete_film(film_id)
