from flask import Blueprint, request, redirect, session, make_response
from werkzeug.utils import secure_filename
from helpers import admin_base, flash_msg
from database import get_db, save_db, fmt_rp, CINEMAS, SEAT_PRICE
import os, json

admin_bp    = Blueprint('admin', __name__, url_prefix='/admin')
QR_FOLDER   = 'static/qr'
POSTER_DIR  = 'static/posters'
ALLOWED_EXT = {'png','jpg','jpeg','webp','gif'}
ADMIN_USER  = 'admin'
ADMIN_PASS  = 'cinemax2024'

for d in [QR_FOLDER, POSTER_DIR]:
    os.makedirs(d, exist_ok=True)

def allowed(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def w(*a, **k):
        if not session.get('admin_ok'):
            return redirect('/admin/login')
        return f(*a, **k)
    return w

@admin_bp.route('/login', methods=['GET','POST'])
def login():
    err = ''
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['admin_ok'] = True
            return redirect('/admin')
        err = 'Username atau password salah.'
    return make_response(f'''<!DOCTYPE html><html lang="id"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Login Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#090912;color:#f0f0f8;font-family:Outfit,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem}}.btn{{display:inline-flex;align-items:center;padding:.6rem 1.4rem;border-radius:10px;border:none;font-family:Outfit,sans-serif;font-size:.9rem;font-weight:600;cursor:pointer;text-decoration:none}}.btn-red{{background:linear-gradient(135deg,#e8173a,#ff6b35);color:#fff}}input{{width:100%;background:#11111e;border:1px solid rgba(255,255,255,.1);color:#f0f0f8;border-radius:10px;padding:.75rem 1rem;font-family:Outfit,sans-serif;font-size:.95rem;outline:none;transition:border-color .2s}}input:focus{{border-color:#e8173a}}label{{display:block;font-size:.8rem;color:#8888aa;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:.5rem}}.fg{{margin-bottom:1.25rem}}</style></head><body>
<div style="width:100%;max-width:400px;">
  <div style="text-align:center;margin-bottom:2rem;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;background:linear-gradient(135deg,#e8173a,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:3px;">🎬 CineMax</div>
    <div style="color:#8888aa;font-size:.9rem;margin-top:.25rem;">Admin Panel</div>
  </div>
  <div style="background:#181828;border:1px solid rgba(255,255,255,.07);border-radius:20px;padding:2rem;">
    <h2 style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:2px;margin-bottom:1.5rem;text-align:center;">LOGIN ADMIN</h2>
    {"" if not err else f'<div style="padding:.75rem 1rem;background:rgba(232,23,58,.12);border:1px solid rgba(232,23,58,.3);border-radius:10px;color:#f87171;font-size:.85rem;margin-bottom:1rem;">' + err + '</div>'}
    <form method="POST">
      <div class="fg"><label>Username</label><input type="text" name="username" placeholder="admin" required autofocus></div>
      <div class="fg"><label>Password</label><input type="password" name="password" placeholder="••••••••" required></div>
      <button type="submit" class="btn btn-red" style="width:100%;justify-content:center;padding:.75rem;">Masuk →</button>
    </form>
  </div>
  <div style="text-align:center;margin-top:1.5rem;"><a href="/" style="color:#8888aa;font-size:.85rem;">← Ke Website</a></div>
</div>
</body></html>''')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_ok', None)
    return redirect('/admin/login')

@admin_bp.route('/')
@admin_required
def dashboard():
    db = get_db()
    movies   = db['movies']
    bookings = db['bookings']
    users    = db['users']
    revenue  = sum(b.get('total',0) for b in bookings if b.get('status')=='confirmed')
    stats = f'''<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:1rem;margin-bottom:2rem;">
      <div class="card" style="text-align:center;padding:1.25rem;"><div style="font-size:2rem;margin-bottom:.4rem;">🎬</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;background:linear-gradient(135deg,#e8173a,#ff6b35);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(movies)}</div><div style="color:#8888aa;font-size:.8rem;">Film</div></div>
      <div class="card" style="text-align:center;padding:1.25rem;"><div style="font-size:2rem;margin-bottom:.4rem;">🎟️</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;background:linear-gradient(135deg,#059669,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(bookings)}</div><div style="color:#8888aa;font-size:.8rem;">Booking</div></div>
      <div class="card" style="text-align:center;padding:1.25rem;"><div style="font-size:2rem;margin-bottom:.4rem;">👥</div><div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;background:linear-gradient(135deg,#7c3aed,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{len(users)}</div><div style="color:#8888aa;font-size:.8rem;">User</div></div>
      <div class="card" style="text-align:center;padding:1.25rem;"><div style="font-size:2rem;margin-bottom:.4rem;">💰</div><div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;background:linear-gradient(135deg,#d97706,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{fmt_rp(revenue)}</div><div style="color:#8888aa;font-size:.8rem;">Pendapatan</div></div>
    </div>'''
    rows = ''
    for m in movies:
        poster = m.get('poster','')
        thumb = f'<img src="{poster}" style="width:40px;height:56px;object-fit:cover;border-radius:6px;" onerror="this.style.display=\'none\'">' if poster else '<div style="width:40px;height:56px;background:#2a2a3e;border-radius:6px;display:flex;align-items:center;justify-content:center;">🎬</div>'
        rows += f'<tr><td>{thumb}</td><td style="font-weight:600;">{m.get("title","")}</td><td><span style="background:rgba(232,23,58,.15);color:#f87171;padding:.2rem .6rem;border-radius:6px;font-size:.8rem;">{m.get("genre","")}</span></td><td style="color:#fbbf24;">{fmt_rp(m.get("price",45000))}</td><td><a href="/admin/edit/{m["id"]}" class="btn btn-yellow btn-sm">✏️ Edit</a> <a href="/admin/delete/{m["id"]}" class="btn btn-danger btn-sm" onclick="return confirm(\'Hapus?\')">🗑️</a></td></tr>'
    qr = db.get('qr_image','')
    qr_src = f'/static/qr/{qr}' if qr and not qr.startswith('http') else qr
    qr_html = f'<div style="text-align:center;"><div style="display:inline-block;background:#fff;padding:10px;border-radius:12px;margin-bottom:.75rem;"><img src="{qr_src}" style="width:180px;height:180px;object-fit:contain;"></div><div style="color:#34d399;font-size:.85rem;font-weight:600;">✅ QR aktif</div><a href="/admin/upload-qr" class="btn btn-ghost btn-sm" style="margin-top:.75rem;display:inline-flex;">🔄 Ganti</a></div>' if qr else '<div style="text-align:center;padding:1.5rem;color:#8888aa;"><div style="font-size:2.5rem;margin-bottom:.75rem;">📷</div><div style="margin-bottom:1rem;">QR belum diupload</div><a href="/admin/upload-qr" class="btn btn-red">⬆️ Upload QR</a></div>'
    content = f'''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.75rem;"><div><h1 style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:2px;">Dashboard</h1><div style="color:#8888aa;font-size:.85rem;">Selamat datang, Admin!</div></div></div>
    {stats}
    <div style="display:grid;grid-template-columns:1fr 300px;gap:1.5rem;align-items:start;">
      <div class="card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem;"><h2 style="font-size:1.1rem;font-weight:700;">🎬 Daftar Film</h2><a href="/admin/films/add" class="btn btn-red btn-sm">+ Tambah Film</a></div><div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;"><thead><tr><th>Poster</th><th>Judul</th><th>Genre</th><th>Harga</th><th>Aksi</th></tr></thead><tbody>{rows or "<tr><td colspan=5 style=text-align:center;padding:2rem;color:#8888aa;>Belum ada film</td></tr>"}</tbody></table></div></div>
      <div class="card"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.25rem;"><h2 style="font-size:1.1rem;font-weight:700;">💳 QR Pembayaran</h2></div>{qr_html}</div>
    </div>'''
    return make_response(admin_base(content, 'dashboard'))

@admin_bp.route('/films')
@admin_required
def films():
    return redirect('/admin')

@admin_bp.route('/films/add', methods=['GET','POST'])
@admin_required
def add_film():
    db = get_db()
    if request.method == 'POST':
        poster_val = ''
        f = request.files.get('poster_file')
        if f and f.filename and allowed(f.filename):
            fname = f"p{len(db['movies'])+1}_{secure_filename(f.filename)}"
            f.save(os.path.join(POSTER_DIR, fname))
            poster_val = f'/static/posters/{fname}'
        if not poster_val:
            poster_val = request.form.get('poster_url','').strip()
        times = [t.strip() for t in request.form.get('showtimes','').split(',') if t.strip()]
        new_id = max((m['id'] for m in db['movies']), default=0) + 1
        db['movies'].append({"id":new_id,"title":request.form.get('title',''),"genre":request.form.get('genre',''),"price":int(request.form.get('price',45000)),"description":request.form.get('description',''),"poster":poster_val,"duration":request.form.get('duration',''),"rating":request.form.get('rating','SU'),"score":float(request.form.get('score',0) or 0),"director":request.form.get('director',''),"cast":request.form.get('cast',''),"showtimes":times})
        save_db(db)
        flash_msg('Film berhasil ditambahkan!', 'success')
        return redirect('/admin')
    return make_response(admin_base(_film_form(), 'films'))

@admin_bp.route('/edit/<int:mid>', methods=['GET','POST'])
@admin_required
def edit_film(mid):
    db = get_db()
    movie = next((m for m in db['movies'] if m['id']==mid), None)
    if not movie:
        flash_msg('Film tidak ditemukan','danger')
        return redirect('/admin')
    if request.method == 'POST':
        poster_val = movie.get('poster','')
        f = request.files.get('poster_file')
        if f and f.filename and allowed(f.filename):
            fname = f"p{mid}_{secure_filename(f.filename)}"
            f.save(os.path.join(POSTER_DIR, fname))
            poster_val = f'/static/posters/{fname}'
        nu = request.form.get('poster_url','').strip()
        if nu: poster_val = nu
        times = [t.strip() for t in request.form.get('showtimes','').split(',') if t.strip()]
        movie.update({"title":request.form.get('title',''),"genre":request.form.get('genre',''),"price":int(request.form.get('price',45000)),"description":request.form.get('description',''),"poster":poster_val,"duration":request.form.get('duration',''),"rating":request.form.get('rating','SU'),"score":float(request.form.get('score',0) or 0),"director":request.form.get('director',''),"cast":request.form.get('cast',''),"showtimes":times})
        save_db(db)
        flash_msg('Film berhasil diperbarui!','success')
        return redirect('/admin')
    return make_response(admin_base(_film_form(movie),'films'))

@admin_bp.route('/delete/<int:mid>')
@admin_required
def delete_film(mid):
    db = get_db()
    title = next((m['title'] for m in db['movies'] if m['id']==mid),'Film')
    db['movies'] = [m for m in db['movies'] if m['id']!=mid]
    save_db(db)
    flash_msg(f'Film "{title}" dihapus.','warning')
    return redirect('/admin')

def _film_form(m=None):
    edit = m is not None
    val  = lambda k,d='': m.get(k,d) if edit else d
    ropts = ''.join(f'<option value="{r}" {"selected" if val("rating","SU")==r else ""}>{r}</option>' for r in ['SU','13+','17+','21+'])
    pnow = f'<div style="margin-bottom:1rem;text-align:center;"><div style="color:#8888aa;font-size:.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:.5rem;">Poster saat ini</div><img src="{val("poster")}" style="max-height:160px;border-radius:10px;border:1px solid rgba(255,255,255,.1);" onerror="this.style.display=\'none\'"></div>' if edit and val('poster') else ''
    action = f'/admin/edit/{m["id"]}' if edit else '/admin/films/add'
    return f'''<div style="max-width:720px;">
      <div style="display:flex;align-items:center;gap:1rem;margin-bottom:2rem;"><a href="/admin" class="btn btn-ghost btn-sm">← Kembali</a><h1 style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:2px;">{"Edit Film" if edit else "Tambah Film Baru"}</h1></div>
      <form method="POST" action="{action}" enctype="multipart/form-data">
        <div class="card" style="margin-bottom:1.25rem;">
          <h3 style="font-size:1rem;font-weight:700;margin-bottom:1.25rem;color:#e8173a;">📝 Info Film</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
            <div class="form-group" style="grid-column:1/-1;"><label>Judul *</label><input type="text" name="title" value="{val('title')}" required></div>
            <div class="form-group"><label>Genre</label><input type="text" name="genre" value="{val('genre')}" placeholder="Action, Drama"></div>
            <div class="form-group"><label>Durasi</label><input type="text" name="duration" value="{val('duration')}" placeholder="2j 15m"></div>
            <div class="form-group"><label>Harga (Rp) *</label><input type="number" name="price" value="{val('price',45000)}" required></div>
            <div class="form-group"><label>Rating</label><select name="rating">{ropts}</select></div>
            <div class="form-group"><label>Skor</label><input type="text" name="score" value="{val('score','0.0')}" placeholder="8.5"></div>
            <div class="form-group"><label>Sutradara</label><input type="text" name="director" value="{val('director')}"></div>
            <div class="form-group"><label>Pemeran</label><input type="text" name="cast" value="{val('cast')}"></div>
            <div class="form-group" style="grid-column:1/-1;"><label>Jam Tayang (pisah koma)</label><input type="text" name="showtimes" value="{', '.join(val('showtimes',[]))}" placeholder="10:00, 13:30, 19:00"></div>
            <div class="form-group" style="grid-column:1/-1;"><label>Deskripsi</label><textarea name="description">{val('description')}</textarea></div>
          </div>
        </div>
        <div class="card" style="margin-bottom:1.5rem;">
          <h3 style="font-size:1rem;font-weight:700;margin-bottom:1.25rem;color:#e8173a;">🖼️ Poster Film</h3>
          {pnow}
          <div style="background:#11111e;border:2px dashed rgba(255,255,255,.1);border-radius:12px;padding:1.5rem;text-align:center;margin-bottom:1rem;">
            <div style="font-size:2.5rem;margin-bottom:.5rem;">📤</div>
            <div style="font-weight:600;margin-bottom:.25rem;">Upload dari Penyimpanan</div>
            <div style="color:#8888aa;font-size:.8rem;margin-bottom:1rem;">JPG · PNG · WEBP</div>
            <label for="pfile" class="btn btn-ghost" style="cursor:pointer;">📂 Pilih File</label>
            <input type="file" id="pfile" name="poster_file" accept="image/*" style="display:none" onchange="prevP(this)">
          </div>
          <div id="prev" style="display:none;text-align:center;margin-bottom:1rem;"><img id="prevImg" style="max-height:180px;border-radius:10px;border:1px solid rgba(255,255,255,.1);"><div style="color:#34d399;font-size:.85rem;margin-top:.5rem;">✅ File dipilih</div></div>
          <div style="text-align:center;color:#8888aa;font-size:.85rem;margin-bottom:.75rem;">— atau URL —</div>
          <div class="form-group" style="margin:0;"><label>URL Poster</label><input type="text" name="poster_url" id="purl" placeholder="https://..."></div>
        </div>
        <div style="display:flex;gap:1rem;">
          <button type="submit" class="btn {"btn-green" if edit else "btn-red"}" style="flex:1;justify-content:center;padding:.8rem;">{"💾 Simpan" if edit else "🎬 Tambah Film"}</button>
          <a href="/admin" class="btn btn-ghost">Batal</a>
        </div>
      </form>
    </div>
    <script>function prevP(i){{if(i.files&&i.files[0]){{const r=new FileReader();r.onload=e=>{{document.getElementById('prevImg').src=e.target.result;document.getElementById('prev').style.display='block';document.getElementById('purl').value='';}}; r.readAsDataURL(i.files[0]);}}}}</script>'''

@admin_bp.route('/bookings')
@admin_required
def bookings():
    db  = get_db()
    bks = list(reversed(db['bookings']))
    rows = ''
    for b in bks:
        st = b.get('status','pending')
        sc = '#34d399' if st=='confirmed' else '#fbbf24'
        rows += f'<tr><td style="font-family:monospace;font-size:.8rem;">{b["id"]}</td><td style="font-weight:600;">{b.get("movie","")}</td><td>{b.get("user","")}</td><td>{b.get("date","")} {b.get("time","")}</td><td>{", ".join(b.get("seats",[]))}</td><td style="color:#fbbf24;font-weight:600;">{fmt_rp(b.get("total",0))}</td><td><span style="color:{sc};font-weight:700;font-size:.8rem;">{st.upper()}</span></td></tr>'
    content = f'''<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.75rem;"><h1 style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:2px;">🎟️ Data Booking</h1></div>
    <div class="card"><div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;"><thead><tr><th>ID</th><th>Film</th><th>User</th><th>Jadwal</th><th>Kursi</th><th>Total</th><th>Status</th></tr></thead><tbody>{rows or "<tr><td colspan=7 style=text-align:center;padding:2rem;color:#8888aa;>Belum ada booking</td></tr>"}</tbody></table></div></div>'''
    return make_response(admin_base(content,'bookings'))

@admin_bp.route('/upload-qr', methods=['GET','POST'])
@admin_required
def upload_qr():
    db = get_db()
    if request.method == 'POST':
        f = request.files.get('qr_image')
        if not f or not f.filename:
            flash_msg('Pilih file QR terlebih dahulu','danger')
            return redirect(request.url)
        if not allowed(f.filename):
            flash_msg('Format tidak didukung. Gunakan JPG/PNG/WEBP','danger')
            return redirect(request.url)
        fname = secure_filename(f.filename)
        f.save(os.path.join(QR_FOLDER, fname))
        db['qr_image'] = fname
        save_db(db)
        flash_msg('QR berhasil diupload!','success')
        return redirect('/admin')
    qr = db.get('qr_image','')
    qr_src = f'/static/qr/{qr}' if qr and not qr.startswith('http') else qr
    cur = f'<div class="card" style="margin-bottom:1.5rem;text-align:center;"><div style="color:#8888aa;font-size:.75rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem;">QR Aktif</div><div style="display:inline-block;background:#fff;padding:10px;border-radius:12px;margin-bottom:.75rem;"><img src="{qr_src}" style="width:200px;height:200px;object-fit:contain;"></div><div style="color:#34d399;font-size:.9rem;font-weight:600;">✅ {qr}</div></div>' if qr else ''
    content = f'''<div style="max-width:480px;">
      <div style="display:flex;align-items:center;gap:1rem;margin-bottom:2rem;"><a href="/admin" class="btn btn-ghost btn-sm">← Kembali</a><div><h1 style="font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:2px;">QR Pembayaran</h1><div style="color:#8888aa;font-size:.85rem;">QR QRIS untuk halaman pembayaran</div></div></div>
      {cur}
      <div class="card">
        <h3 style="font-size:1rem;font-weight:700;margin-bottom:1.25rem;color:#e8173a;">📷 {"Ganti" if qr else "Upload"} QR Code</h3>
        <form method="POST" enctype="multipart/form-data">
          <div style="background:#11111e;border:2px dashed rgba(255,255,255,.12);border-radius:14px;padding:2rem;text-align:center;margin-bottom:1.25rem;">
            <div style="font-size:3rem;margin-bottom:.75rem;">🖼️</div>
            <div style="font-weight:600;margin-bottom:.25rem;">Pilih file QR dari penyimpanan</div>
            <div style="color:#8888aa;font-size:.85rem;margin-bottom:1.25rem;">JPG · PNG · WEBP</div>
            <label for="qrfile" class="btn btn-red" style="cursor:pointer;">📂 Buka Penyimpanan</label>
            <input type="file" id="qrfile" name="qr_image" accept="image/*" style="display:none" onchange="prevQR(this)">
          </div>
          <div id="qrprev" style="display:none;text-align:center;margin-bottom:1.25rem;"><div style="display:inline-block;background:#fff;padding:10px;border-radius:12px;"><img id="qrimg" style="width:180px;height:180px;object-fit:contain;"></div><div style="color:#34d399;font-size:.9rem;font-weight:600;margin-top:.75rem;" id="qrname">✅ Siap diupload</div></div>
          <button type="submit" class="btn btn-red" style="width:100%;justify-content:center;padding:.8rem;">⬆️ Upload QR</button>
        </form>
      </div>
    </div>
    <script>function prevQR(i){{if(i.files&&i.files[0]){{const r=new FileReader();r.onload=e=>{{document.getElementById('qrimg').src=e.target.result;document.getElementById('qrprev').style.display='block';document.getElementById('qrname').textContent='✅ '+i.files[0].name;}};r.readAsDataURL(i.files[0]);}}}}</script>'''
    return make_response(admin_base(content,'qr'))
