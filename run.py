from app import create_app

# Buat app dari factory function
app = create_app()

if __name__ == '__main__':
    # Jalankan app di mode debug
    # debug=True → otomatis reload kalau ada perubahan kode
    app.run(debug=True)
