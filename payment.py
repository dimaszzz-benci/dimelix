import json as _json, base64, urllib.request
from flask import Blueprint, request, redirect, session, make_response
from helpers import flash_msg, base
from database import get_db, save_db, fmt_rp

payment_bp = Blueprint('payment', __name__)

MIDTRANS_SERVER_KEY = 'Mid-server-UWdwnCZyJi4yuj1jUvHaCKjq'
MIDTRANS_CLIENT_KEY = 'Mid-client-CnZrBGXckbxkkT3-'
MIDTRANS_BASE_URL   = 'https://app.sandbox.midtrans.com/snap/v1/transactions'


@payment_bp.route('/payment/<booking_id>')
@payment_bp.route('/payment/<booking_id>/<method>')
def payment(booking_id, method=''):
    bk = session.get('last_booking')
    if not bk or bk['id'] != booking_id:
        return redirect('/')

    db       = get_db()
    qr_image = db.get('qr_image', '')   # diisi admin lewat upload QR

    seat_tags = ''.join(
        f'<span style="background:rgba(232,23,58,.15);border:1px solid rgba(232,23,58,.3);'
        f'color:#e8173a;padding:.3rem .65rem;border-radius:6px;font-size:.85rem;font-weight:700;">{s}</span>'
        for s in bk['seats']
    )

    # ── Helper aktif/border ──────────────────────────────────────────────────
    def active(m): return 'block' if method == m else 'none'
    def border(m, rgb): return f'rgba({rgb},.5)' if method == m else 'rgba(255,255,255,.1)'

    def confirm_btn(mid, label='✅ Konfirmasi Pembayaran Selesai'):
        return f'''
        <form method="POST" action="/confirm-payment/{bk["id"]}/{mid}" style="margin-top:1.25rem;">
          <button type="submit" class="btn btn-green" style="width:100%;justify-content:center;">
            {label}
          </button>
        </form>
        <div id="suc-{mid}" style="display:none;margin-top:1rem;background:rgba(16,185,129,.12);
          border:1px solid rgba(16,185,129,.35);border-radius:14px;padding:1.5rem;text-align:center;">
          <div style="font-size:3rem;margin-bottom:.75rem;">🎉</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#34d399;margin-bottom:.5rem;">Pembayaran Berhasil!</div>
          <p style="color:#c0fce8;font-size:.9rem;margin-bottom:1rem;">Tiket kamu sudah aktif.</p>
          <a href="/my-tickets" class="btn btn-green">🎟️ Lihat Tiket</a>
        </div>'''

    # ── QR BLOCK ─────────────────────────────────────────────────────────────
    if qr_image:
        # Kalau path lokal (diupload admin), prefix /static/qr/
        src = qr_image if qr_image.startswith('http') else f'/static/qr/{qr_image}'
        qr_block = f'''
        <div style="text-align:center;margin-bottom:1.25rem;">
          <p style="color:#8888aa;font-size:.85rem;margin-bottom:1rem;">
            Scan QR di bawah dengan aplikasi dompet digital
          </p>
          <div style="display:inline-block;background:#fff;padding:14px;border-radius:16px;box-shadow:0 4px 30px rgba(0,0,0,.5);">
            <img src="{src}" alt="QR QRIS" style="display:block;width:220px;height:220px;object-fit:contain;"
              onerror="this.parentElement.innerHTML='<p style=color:#f87171;padding:1rem;>Gambar QR gagal dimuat</p>'"/>
          </div>
          <p style="color:#ffd700;font-size:.8rem;margin-top:.75rem;">⏱ QR berlaku 15 menit</p>
        </div>'''
    else:
        qr_block = '''
        <div style="text-align:center;padding:1.5rem;background:#11111e;border-radius:12px;margin-bottom:1rem;">
          <div style="font-size:3rem;margin-bottom:.5rem;">⚠️</div>
          <p style="color:#fbbf24;font-size:.9rem;font-weight:600;">QR Code belum diatur admin.</p>
          <p style="color:#8888aa;font-size:.8rem;margin-top:.25rem;">Hubungi customer service untuk pembayaran QRIS.</p>
        </div>'''

    # ── DANA block ───────────────────────────────────────────────────────────
    dana_block = f'''
    <div style="background:#11111e;border-radius:10px;padding:1.25rem;margin-bottom:.75rem;">
      <div style="font-size:.75rem;color:#8888aa;margin-bottom:.25rem;text-transform:uppercase;letter-spacing:1px;">Nomor DANA Tujuan</div>
      <div style="font-size:1.6rem;font-weight:700;letter-spacing:3px;color:#00aed6;" id="danaNum">0812-3456-7890</div>
    </div>
    <div style="background:#11111e;border-radius:10px;padding:1rem;margin-bottom:1rem;">
      <div style="font-size:.75rem;color:#8888aa;margin-bottom:.25rem;">Nama Penerima</div>
      <div style="font-weight:700;">CineMax Official</div>
    </div>
    <div style="background:rgba(0,174,214,.08);border:1px solid rgba(0,174,214,.2);border-radius:10px;padding:1rem;font-size:.85rem;color:#8888aa;">
      <strong style="color:#00aed6;">Cara bayar:</strong> Buka DANA → Transfer → masukkan nomor di atas →
      masukkan nominal tepat <strong style="color:#f0f0f8;">{fmt_rp(bk['total'])}</strong>
    </div>'''

    # ── BCA block ────────────────────────────────────────────────────────────
    va_number = f"8808{bk['id'][-8:]}"
    bca_block = f'''
    <div style="background:#11111e;border-radius:10px;padding:1.25rem;margin-bottom:.75rem;cursor:pointer;"
      onclick="copyText('{va_number}','copied-bca')">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:.75rem;color:#8888aa;margin-bottom:.25rem;text-transform:uppercase;letter-spacing:1px;">BCA Virtual Account</div>
          <div style="font-size:1.5rem;font-weight:700;letter-spacing:3px;" id="bcaNum">{va_number}</div>
        </div>
        <span style="font-size:1.5rem;color:#3b82f6;">📋</span>
      </div>
      <div id="copied-bca" style="display:none;color:#34d399;font-size:.8rem;margin-top:.5rem;">✅ Nomor disalin!</div>
    </div>
    <div style="background:#11111e;border-radius:10px;padding:1rem;margin-bottom:1rem;">
      <div style="font-size:.75rem;color:#8888aa;margin-bottom:.25rem;">Nama Rekening</div>
      <div style="font-weight:700;">CineMax Indonesia</div>
    </div>
    <div style="background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:10px;padding:1rem;font-size:.85rem;color:#8888aa;">
      <strong style="color:#3b82f6;">Cara bayar:</strong> m-BCA / KlikBCA / ATM BCA → Transfer → Virtual Account →
      masukkan nomor di atas → bayar tepat <strong style="color:#f0f0f8;">{fmt_rp(bk['total'])}</strong>
    </div>'''

    content = f'''
    <div style="max-width:720px;margin:0 auto;padding:2.5rem 1.5rem;">

      <!-- Banner konfirmasi -->
      <div style="text-align:center;padding:1rem;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);
        border-radius:12px;color:#34d399;font-size:.95rem;margin-bottom:2rem;">
        🎉 Pemesanan dikonfirmasi! Selesaikan pembayaran untuk <strong>{bk['movie']}</strong>
      </div>

      <!-- Detail tiket -->
      <div style="background:#181828;border:1px solid rgba(255,255,255,.07);border-radius:20px;overflow:hidden;margin-bottom:2rem;">
        <div style="background:linear-gradient(135deg,#1a0520,#2d0a14);padding:2rem;display:flex;gap:1.5rem;align-items:center;">
          <span style="font-size:3rem;">🎬</span>
          <div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;">{bk['movie']}</div>
            <div style="color:#8888aa;font-size:.85rem;font-family:monospace;">ID: {bk['id']}</div>
          </div>
        </div>
        <div style="padding:1.5rem 2rem;">
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem;">
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Bioskop</div><div style="font-weight:700;font-size:.9rem;">{bk['cinema']}</div></div>
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Tanggal</div><div style="font-weight:700;font-size:.9rem;">{bk['date']}</div></div>
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Jam</div><div style="font-weight:700;font-size:.9rem;">{bk['time']}</div></div>
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Tipe Kursi</div><div style="font-weight:700;font-size:.9rem;">{bk['seat_type']}</div></div>
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Jumlah</div><div style="font-weight:700;font-size:.9rem;">{len(bk['seats'])} kursi</div></div>
            <div><div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.3rem;">Status</div><div style="font-weight:700;font-size:.9rem;color:#fbbf24;">⏳ Menunggu Bayar</div></div>
          </div>
        </div>
        <div style="padding:1.25rem 2rem;border-top:1px solid rgba(255,255,255,.07);">
          <div style="font-size:.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:.75rem;">Nomor Kursi</div>
          <div style="display:flex;gap:.5rem;flex-wrap:wrap;">{seat_tags}</div>
        </div>
        <div style="padding:1rem 2rem 1.5rem;border-top:1px solid rgba(255,255,255,.07);text-align:center;">
          <div style="font-size:1.5rem;letter-spacing:.25rem;color:#8888aa;font-family:monospace;">▌▌█▌▌▌█▌▌█▌▌▌▌█▌▌</div>
          <div style="font-family:monospace;color:#8888aa;font-size:.75rem;margin-top:.25rem;">{bk['id']}</div>
        </div>
      </div>

      <!-- Total -->
      <div style="background:linear-gradient(135deg,rgba(232,23,58,.1),rgba(255,107,53,.1));
        border:1px solid rgba(232,23,58,.3);border-radius:16px;padding:1.25rem 1.5rem;
        display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;">
        <div>
          <div style="color:#8888aa;font-size:.85rem;">Total Pembayaran</div>
          <div style="color:#8888aa;font-size:.8rem;">{len(bk['seats'])} kursi × {bk['seat_type']}</div>
        </div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#e8173a;">{fmt_rp(bk['total'])}</div>
      </div>

      <!-- Pilih Metode -->
      <h2 style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;margin-bottom:1.25rem;">💳 Pilih Metode Pembayaran</h2>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:1.75rem;">
        <a href="/payment/{bk['id']}/qris" style="padding:1.1rem;border:2px solid {border('qris','255,215,0')};border-radius:14px;
          text-align:center;text-decoration:none;color:#f0f0f8;display:block;transition:all .2s;
          background:{'rgba(255,215,0,.06)' if method=='qris' else 'transparent'};">
          <div style="font-size:1.8rem;margin-bottom:.35rem;">💰</div>
          <div style="font-size:.85rem;font-weight:700;">QRIS</div>
          <div style="font-size:.7rem;color:#8888aa;margin-top:.2rem;">Semua E-Wallet</div>
        </a>
        <a href="/payment/{bk['id']}/dana" style="padding:1.1rem;border:2px solid {border('dana','0,174,214')};border-radius:14px;
          text-align:center;text-decoration:none;color:#f0f0f8;display:block;transition:all .2s;
          background:{'rgba(0,174,214,.06)' if method=='dana' else 'transparent'};">
          <div style="font-size:1.8rem;margin-bottom:.35rem;">📱</div>
          <div style="font-size:.85rem;font-weight:700;">DANA</div>
          <div style="font-size:.7rem;color:#8888aa;margin-top:.2rem;">Transfer DANA</div>
        </a>
        <a href="/payment/{bk['id']}/bca" style="padding:1.1rem;border:2px solid {border('bca','59,130,246')};border-radius:14px;
          text-align:center;text-decoration:none;color:#f0f0f8;display:block;transition:all .2s;
          background:{'rgba(59,130,246,.06)' if method=='bca' else 'transparent'};">
          <div style="font-size:1.8rem;margin-bottom:.35rem;">🏦</div>
          <div style="font-size:.85rem;font-weight:700;">BCA</div>
          <div style="font-size:.7rem;color:#8888aa;margin-top:.2rem;">Virtual Account</div>
        </a>
      </div>

      <!-- === QRIS Panel === -->
      <div style="display:{active('qris')};background:#181828;border:2px solid rgba(255,215,0,.25);border-radius:18px;padding:1.75rem;margin-bottom:1.5rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;margin-bottom:1.25rem;color:#ffd700;">💰 Bayar via QRIS</div>
        {qr_block}
        {confirm_btn('qris', '✅ Saya Sudah Scan & Bayar via QRIS')}
      </div>

      <!-- === DANA Panel === -->
      <div style="display:{active('dana')};background:#181828;border:2px solid rgba(0,174,214,.25);border-radius:18px;padding:1.75rem;margin-bottom:1.5rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;margin-bottom:1.25rem;color:#00aed6;">📱 Bayar via DANA</div>
        {dana_block}
        {confirm_btn('dana', '✅ Saya Sudah Transfer via DANA')}
      </div>

      <!-- === BCA Panel === -->
      <div style="display:{active('bca')};background:#181828;border:2px solid rgba(59,130,246,.25);border-radius:18px;padding:1.75rem;margin-bottom:1.5rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;margin-bottom:1.25rem;color:#3b82f6;">🏦 Bayar via BCA Virtual Account</div>
        {bca_block}
        {confirm_btn('bca', '✅ Saya Sudah Transfer via BCA')}
      </div>

      {"" if method else '<div style="text-align:center;padding:2rem;color:#8888aa;"><div style=\'font-size:3rem;margin-bottom:1rem;\'>👆</div><p>Pilih metode pembayaran di atas untuk melanjutkan</p></div>'}

      <div style="text-align:center;margin-top:1.5rem;">
        <a href="/my-tickets" style="color:#8888aa;font-size:.9rem;">Lihat semua tiket saya →</a>
      </div>
    </div>

    <script>
    function copyText(txt, elId) {{
      navigator.clipboard.writeText(txt)
        .then(() => {{ document.getElementById(elId).style.display='block'; }})
        .catch(() => {{ alert('Nomor: ' + txt); }});
    }}
    </script>'''

    return make_response(base(content, f'Pembayaran — {bk["movie"]}'))


@payment_bp.route('/confirm-payment/<booking_id>/<method>', methods=['POST'])
def confirm_payment(booking_id, method):
    db  = get_db()
    bk  = next((b for b in db['bookings'] if b['id'] == booking_id), None)
    if bk:
        bk['status']    = 'confirmed'
        bk['paid_via']  = method
        save_db(db)
        # Update session juga
        if session.get('last_booking', {}).get('id') == booking_id:
            session['last_booking']['status'] = 'confirmed'
    flash_msg('🎉 Pembayaran berhasil! Tiket kamu sudah aktif.', 'success')
    return redirect('/my-tickets')
