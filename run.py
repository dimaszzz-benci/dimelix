from app import create_app, db
from app.models.user import User
from app.models.film import Film

app = create_app()

# Inisialisasi database otomatis saat pertama deploy
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
