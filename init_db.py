from app import create_app, db
from app.models.user import User
from app.models.film import Film
from app import bcrypt

app = create_app()

with app.app_context():
    # Buat semua tabel berdasarkan model yang ada
    db.create_all()
    print("✅ Tabel berhasil dibuat!")

    # Cek apakah admin sudah ada
    admin = User.query.filter_by(email='admin@dimelix.com').first()

    if not admin:
        # Buat akun admin pertama
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email='admin@dimelix.com',
            password=hashed_pw,
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Akun admin berhasil dibuat!")
        print("   Email    : admin@dimelix.com")
        print("   Password : admin123")
    else:
        print("ℹ️ Admin sudah ada, skip.")

    print("\n🎬 Dimelix siap dijalankan!")
