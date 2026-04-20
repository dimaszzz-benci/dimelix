from flask import Blueprint, request, redirect, session, make_response
from datetime import datetime, timedelta
from helpers import flash_msg, base
from database import get_db, save_db, get_movies, fmt_rp, CINEMAS, SEAT_PRICE

booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/booking/<int:movie_id>', methods=['GET', 'POST'])
def booking(movie_id):
    if 'user' not in session:
        flash_msg('Silakan login terlebih dahulu', 'warning')
        return redirect('/login')

    movies = get_movies()
    m = next((x for x in movies if x['id'] == movie_id), None)
    if not m: return redirect('/')

    if request.method == 'POST':
        seats = request.form.getlist('seats')
        if len(seats) < 1:
            flash_msg('Pilih minimal 1 kursi!', 'danger')
            return redirect(f'/booking/{movie_id}')
        if len(seats) > 8:
            flash_msg('Maksimal 8 kursi per transaksi!', 'danger')
            return redirect(f'/booking/{movie_id}')

        seat_type = request.form.get('seat_type', 'Reguler')
        price_per = SEAT_PRICE.get(seat_type, 45000)
        total     = len(seats) * price_per

        bk = {
            "id":        f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user":      session['user'],
            "movie":     m['title'],
            "movie_id":  m['id'],
            "cinema":    request.form.get('cinema', CINEMAS[0]),
            "date":      request.form.get('date', ''),
            "time":      request.form.get('showtime', ''),
            "seats":     seats,
            "seat_type": seat_type,
            "total":     total,
            "status":    "pending",
            "booked_at": datetime.now().isoformat()
        }
        db = get_db()
        db['bookings'].append(bk)
        save_db(db)
        session['last_booking'] = bk
        return redirect(f'/payment/{bk["id"]}')

    # ── Bangun opsi dropdown ──────────────────────────────────────────────────
    cinema_opts = ''.join(f'<option value="{c}">{c}</option>' for c in CINEMAS)

    # Tanggal: 7 hari ke depan
    today = datetime.now()
    date_opts = ''
    for i in range(7):
        d    = today + timedelta(days=i)
        val  = d.strftime('%Y-%m-%d')
        lbl  = d.strftime('%A, %d %B %Y')
        sel  = 'selected' if i == 0 else ''
        date_opts += f'<option value="{val}" {sel}>{lbl}</option>'

    # Jam tayang
    time_opts = ''.join(f'<option value="{t}">{t}</option>' for t in m.get('showtimes', []))

    # Tipe kursi
    type_cards = ''
    for name, price in SEAT_PRICE.items():
        type_cards += f'''
        <label style="cursor:pointer;">
          <input type="radio" name="seat_type" value="{name}" {"checked" if name=="Reguler" else ""}
            style="display:none;" onchange="updateType(this)">
          <div class="type-card" data-name="{name}" data-price="{price}"
            style="padding:.9rem 1rem;border:2px solid {"rgba(232,23,58,.5)" if name=="Reguler" else "rgba(255,255,255,.1)"};
              border-radius:12px;background:{"rgba(232,23,58,.08)" if name=="Reguler" else "transparent"};transition:all .2s;">
            <div style="font-weight:700;font-size:.9rem;">{name}</div>
            <div style="color:#e8173a;font-size:.85rem;font-weight:600;margin-top:.2rem;">{fmt_rp(price)}</div>
          </div>
        </label>'''

    content = f'''
    <div style="max-width:1000px;margin:0 auto;padding:2rem 1.5rem;">
      <h1 style="font-family:'Bebas Neue',sans-serif;font-size:2rem;margin-bottom:.5rem;">🎟️ Pesan Tiket — {m['title']}</h1>
      <p style="color:#8888aa;margin-bottom:2rem;">Lengkapi detail pemesananmu</p>

      <form method="POST" id="bookForm">
        <input type="hidden" name="showtime" id="timeHidden">
        <div style="display:grid;grid-template-columns:1fr 320px;gap:1.5rem;">

          <!-- KIRI -->
          <div>
            <!-- Jadwal -->
            <div class="card" style="margin-bottom:1.25rem;">
              <h3 style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;margin-bottom:1.25rem;">📅 Pilih Jadwal</h3>
              <div class="form-group">
                <label>Bioskop</label>
                <select name="cinema" onchange="updateSummary()">
                  {cinema_opts}
                </select>
              </div>
              <div class="form-group">
                <label>Tanggal</label>
                <select name="date" id="dateSelect" onchange="updateSummary()">
                  {date_opts}
                </select>
              </div>
              <div class="form-group">
                <label>Jam Tayang</label>
                <div style="display:flex;gap:.6rem;flex-wrap:wrap;" id="timeBtns">
                  {"".join(f'<button type="button" onclick="selTime(this,\\"{t}\\")" style="padding:.45rem 1rem;border:1px solid rgba(255,255,255,.1);border-radius:8px;background:transparent;color:#f0f0f8;font-family:Outfit,sans-serif;font-size:.85rem;font-weight:600;cursor:pointer;transition:all .2s;">{t}</button>' for t in m.get("showtimes",[]))}
                </div>
              </div>
            </div>

            <!-- Tipe Kursi -->
            <div class="card" style="margin-bottom:1.25rem;">
              <h3 style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;margin-bottom:1.25rem;">💺 Tipe Kursi</h3>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;">
                {type_cards}
              </div>
            </div>

            <!-- Peta Kursi -->
            <div class="card">
              <h3 style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;margin-bottom:1rem;">🪑 Pilih Kursi</h3>
              <div style="background:linear-gradient(90deg,transparent,rgba(232,23,58,.3),transparent);height:3px;border-radius:3px;margin:0 2rem .5rem;"></div>
              <p style="text-align:center;color:#8888aa;font-size:.75rem;letter-spacing:3px;margin-bottom:1.5rem;">▲ LAYAR ▲</p>
              <div id="seatGrid" style="display:grid;grid-template-columns:repeat(10,1fr);gap:.35rem;margin-bottom:1rem;"></div>
              <div style="display:flex;gap:1.5rem;justify-content:center;margin-bottom:1rem;">
                <div style="display:flex;align-items:center;gap:.4rem;font-size:.8rem;color:#8888aa;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);"></div>Tersedia</div>
                <div style="display:flex;align-items:center;gap:.4rem;font-size:.8rem;color:#8888aa;"><div style="width:14px;height:14px;border-radius:3px;background:#e8173a;"></div>Dipilih</div>
                <div style="display:flex;align-items:center;gap:.4rem;font-size:.8rem;color:#8888aa;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(255,255,255,.15);"></div>Terisi</div>
              </div>
              <p style="text-align:center;color:#8888aa;font-size:.85rem;">Dipilih: <span id="selDisplay" style="color:#e8173a;font-weight:700;">—</span></p>
            </div>
          </div>

          <!-- KANAN: Ringkasan -->
          <div class="card" style="position:sticky;top:80px;height:fit-content;border-radius:20px;padding:1.75rem;">
            <h3 style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;margin-bottom:1.25rem;">🧾 Ringkasan</h3>
            <div style="font-weight:700;font-size:1rem;margin-bottom:.25rem;">{m['title']}</div>
            <div style="color:#8888aa;font-size:.85rem;margin-bottom:1.25rem;padding-bottom:1.25rem;border-bottom:1px solid rgba(255,255,255,.07);">
              {m['genre']} • ⭐ {m['score']}
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.9rem;">
              <span style="color:#8888aa;">Bioskop</span><span id="s-cinema" style="font-weight:600;text-align:right;max-width:180px;">{CINEMAS[0]}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.9rem;">
              <span style="color:#8888aa;">Tanggal</span><span id="s-date" style="font-weight:600;">{today.strftime('%d %b %Y')}</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.9rem;">
              <span style="color:#8888aa;">Jam</span><span id="s-time" style="font-weight:600;">—</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.9rem;">
              <span style="color:#8888aa;">Tipe</span><span id="s-type" style="font-weight:600;">Reguler</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:.75rem;font-size:.9rem;">
              <span style="color:#8888aa;">Kursi</span><span id="s-seats" style="font-weight:600;">—</span>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,.07);padding-top:1rem;margin-top:.5rem;">
              <div style="color:#8888aa;font-size:.85rem;">Total</div>
              <div id="s-total" style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#e8173a;">Rp 0</div>
            </div>
            <button type="submit" class="btn btn-red" style="width:100%;justify-content:center;margin-top:1.25rem;">
              Lanjut ke Pembayaran →
            </button>
          </div>

        </div>
      </form>
    </div>

    <script>
    const PRICES = {str(SEAT_PRICE).replace("'",'"')};
    let selSeats=[], curType='Reguler', curPrice=45000;
    const TAKEN = ["A3","A7","B5","C2","C8","D4","D6","E1","E9","F3","F7","G5","H2","H8"];
    const ROWS  = ["A","B","C","D","E","F","G","H"];

    // Build seat grid
    const grid = document.getElementById('seatGrid');
    ROWS.forEach(r => {{
      for(let c=1;c<=10;c++) {{
        const id = r+c, taken = TAKEN.includes(id);
        const d  = document.createElement('div');
        d.style.cssText = `aspect-ratio:1;border-radius:5px;border:1px solid ${{taken?'transparent':'rgba(255,255,255,.12)'}};
          cursor:${{taken?'not-allowed':'pointer'}};display:flex;align-items:center;justify-content:center;
          font-size:.55rem;font-weight:700;transition:all .15s;
          background:${{taken?'rgba(255,255,255,.08)':'rgba(255,255,255,.03)'}};
          color:${{taken?'rgba(255,255,255,.15)':'#8888aa'}};`;
        d.textContent = id;
        if(!taken) d.onclick = () => toggleSeat(d, id);
        grid.appendChild(d);
      }}
    }});

    function toggleSeat(d, id) {{
      if(d.dataset.sel==='1') {{
        d.dataset.sel=''; d.style.background='rgba(255,255,255,.03)';
        d.style.borderColor='rgba(255,255,255,.12)'; d.style.color='#8888aa';
        selSeats = selSeats.filter(s=>s!==id);
      }} else {{
        if(selSeats.length>=8) {{ alert('Maksimal 8 kursi'); return; }}
        d.dataset.sel='1'; d.style.background='#e8173a';
        d.style.borderColor='#e8173a'; d.style.color='#fff';
        selSeats.push(id);
      }}
      syncSeats();
    }}

    function syncSeats() {{
      document.querySelectorAll('.si').forEach(e=>e.remove());
      selSeats.forEach(s=>{{
        const i=document.createElement('input');
        i.type='hidden'; i.name='seats'; i.value=s; i.className='si';
        document.getElementById('bookForm').appendChild(i);
      }});
      const label = selSeats.length ? selSeats.join(', ') : '—';
      document.getElementById('selDisplay').textContent = label;
      document.getElementById('s-seats').textContent    = label;
      document.getElementById('s-total').textContent    = 'Rp ' + new Intl.NumberFormat('id-ID').format(selSeats.length * curPrice);
    }}

    function selTime(btn, t) {{
      document.querySelectorAll('#timeBtns button').forEach(b=>{{
        b.style.background='transparent'; b.style.borderColor='rgba(255,255,255,.1)'; b.style.color='#f0f0f8';
      }});
      btn.style.background='#e8173a'; btn.style.borderColor='#e8173a'; btn.style.color='#fff';
      document.getElementById('timeHidden').value = t;
      document.getElementById('s-time').textContent = t;
    }}

    function updateType(radio) {{
      curType  = radio.value;
      curPrice = PRICES[curType];
      document.querySelectorAll('.type-card').forEach(c=>{{
        const active = c.dataset.name === curType;
        c.style.borderColor = active ? 'rgba(232,23,58,.5)' : 'rgba(255,255,255,.1)';
        c.style.background  = active ? 'rgba(232,23,58,.08)' : 'transparent';
      }});
      document.getElementById('s-type').textContent = curType;
      document.getElementById('s-total').textContent = 'Rp ' + new Intl.NumberFormat('id-ID').format(selSeats.length * curPrice);
    }}

    function updateSummary() {{
      const cinema = document.querySelector('select[name=cinema]').value;
      const dateEl = document.getElementById('dateSelect');
      const dateText = dateEl.options[dateEl.selectedIndex].text;
      document.getElementById('s-cinema').textContent = cinema;
      document.getElementById('s-date').textContent   = dateText;
    }}

    // set hidden showtime ke value pertama jika ada
    const firstTimeBtn = document.querySelector('#timeBtns button');
    if(firstTimeBtn) firstTimeBtn.click();
    </script>'''

    return make_response(base(content, f'Pesan — {m["title"]}'))
