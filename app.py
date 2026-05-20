import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "opravdu-bezpecny-klic"
DATABASE = "ptaci.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ptaci (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazev TEXT NOT NULL,
                vedecky_nazev TEXT,
                rad TEXT,
                celed TEXT,
                delka_cm INTEGER,
                rozpeti_cm INTEGER,
                hmotnost_g INTEGER,
                status_ohrozeni TEXT,
                typ_potravy TEXT,
                migrace INTEGER,
                vyskyt_kontinent TEXT,
                snuska_ks REAL
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("admin", generate_password_hash("admin123")),
            )
        conn.commit()

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view

def parse_int(value, default=None):
    try: return int(value)
    except (TypeError, ValueError): return default

def parse_float(value, default=None):
    try: return float(value)
    except (TypeError, ValueError): return default

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    rad_filter = [v for v in request.args.getlist("rad") if v]
    status_filter = [v for v in request.args.getlist("status_ohrozeni") if v]
    typ_potravy_filter = [v for v in request.args.getlist("typ_potravy") if v]
    kontinent_filter = [v for v in request.args.getlist("vyskyt_kontinent") if v]
    migrace_filter = [v for v in request.args.getlist("migrace") if v]
    hmotnost_od = request.args.get("hmotnost_od")
    hmotnost_do = request.args.get("hmotnost_do")

    conditions = ["1=1"]
    params = []

    if rad_filter:
        conditions.append(f"rad IN ({','.join(['?']*len(rad_filter))})")
        params.extend(rad_filter)
    if status_filter:
        conditions.append(f"status_ohrozeni IN ({','.join(['?']*len(status_filter))})")
        params.extend(status_filter)
    if typ_potravy_filter:
        conditions.append(f"typ_potravy IN ({','.join(['?']*len(typ_potravy_filter))})")
        params.extend(typ_potravy_filter)
    if kontinent_filter:
        conditions.append(f"vyskyt_kontinent IN ({','.join(['?']*len(kontinent_filter))})")
        params.extend(kontinent_filter)
    if migrace_filter:
        conditions.append(f"migrace IN ({','.join(['?']*len(migrace_filter))})")
        params.extend([int(m) for m in migrace_filter])
    if hmotnost_od:
        conditions.append("hmotnost_g >= ?")
        params.append(hmotnost_od)
    if hmotnost_do:
        conditions.append("hmotnost_g <= ?")
        params.append(hmotnost_do)

    where_clause = " WHERE " + " AND ".join(conditions)

    cursor.execute(f"SELECT * FROM ptaci {where_clause} ORDER BY nazev ASC", params)
    ptaci = cursor.fetchall()

    cursor.execute(f"SELECT COUNT(*), AVG(delka_cm), AVG(hmotnost_g), MAX(hmotnost_g) FROM ptaci {where_clause}", params)
    count, avg_delka, avg_hmotnost, max_hmotnost = cursor.fetchone()

    cursor.execute(f"SELECT rad, COUNT(*) as cnt FROM ptaci {where_clause} GROUP BY rad ORDER BY cnt DESC LIMIT 5", params)
    rad_data = cursor.fetchall()
    
    cursor.execute(f"SELECT SUM(CASE WHEN migrace=1 THEN 1 ELSE 0 END), SUM(CASE WHEN migrace=0 THEN 1 ELSE 0 END) FROM ptaci {where_clause}", params)
    tazni_netazni = cursor.fetchone()

    cursor.execute(f"SELECT typ_potravy, AVG(hmotnost_g) FROM ptaci {where_clause} GROUP BY typ_potravy", params)
    weight_data = cursor.fetchall()

    cursor.execute(f"SELECT vyskyt_kontinent, COUNT(*) FROM ptaci {where_clause} GROUP BY vyskyt_kontinent", params)
    continent_data = cursor.fetchall()

    rady = [r['rad'] for r in conn.execute("SELECT DISTINCT rad FROM ptaci WHERE rad IS NOT NULL").fetchall()]
    typy = [t['typ_potravy'] for t in conn.execute("SELECT DISTINCT typ_potravy FROM ptaci WHERE typ_potravy IS NOT NULL").fetchall()]
    kontinenty = [k['vyskyt_kontinent'] for k in conn.execute("SELECT DISTINCT vyskyt_kontinent FROM ptaci WHERE vyskyt_kontinent IS NOT NULL").fetchall()]
    statuses = [s['status_ohrozeni'] for s in conn.execute("SELECT DISTINCT status_ohrozeni FROM ptaci WHERE status_ohrozeni IS NOT NULL").fetchall()]

    conn.close()

    return render_template(
        "dashboard.html",
        ptaci=ptaci, rady=rady, typy_potravy=typy, kontinenty=kontinenty, statuses=statuses,
        selected_rad=rad_filter, selected_typ=typ_potravy_filter, selected_kontinent=kontinent_filter,
        selected_status=status_filter, selected_migrace=migrace_filter,
        selected_hmotnost_od=hmotnost_od, selected_hmotnost_do=hmotnost_do,
        celkem=count, prumerna_delka=round(avg_delka or 0, 1),
        prumerna_hmotnost=round(avg_hmotnost or 0, 1), max_hmotnost=max_hmotnost or 0,
        rad_labels=[r[0] for r in rad_data], rad_counts=[r[1] for r in rad_data],
        tazni_count=tazni_netazni[0] or 0, netazni_count=tazni_netazni[1] or 0,
        weight_labels=[w[0] for w in weight_data], weight_avgs=[round(w[1] or 0, 1) for w in weight_data],
        continent_labels=[c[0] for c in continent_data], continent_counts=[c[1] for c in continent_data]
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"): return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.update({"user_id": user["id"], "username": user["username"]})
                return redirect(url_for("dashboard"))
        error = "Nesprávné údaje."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/birds")
@login_required
def bird_list():
    with get_db() as conn:
        birds = conn.execute("SELECT * FROM ptaci ORDER BY nazev ASC").fetchall()
    return render_template("birds.html", birds=birds, username=session.get("username"))

@app.route("/birds/new", methods=["GET", "POST"])
@login_required
def create_bird():
    if request.method == "POST":
        form = request.form
        data = (
            form.get("nazev", "").strip(),
            form.get("vedecky_nazev", "").strip(),
            form.get("rad", "").strip(),
            form.get("celed", "").strip(),
            parse_int(form.get("delka_cm")),
            parse_int(form.get("rozpeti_cm")),
            parse_int(form.get("hmotnost_g")),
            form.get("status_ohrozeni", "").strip(),
            form.get("typ_potravy", "").strip(),
            1 if form.get("migrace") == "1" else 0,
            form.get("vyskyt_kontinent", "").strip(),
            parse_float(form.get("snuska_ks")),
        )
        with get_db() as conn:
            conn.execute("INSERT INTO ptaci (nazev, vedecky_nazev, rad, celed, delka_cm, rozpeti_cm, hmotnost_g, status_ohrozeni, typ_potravy, migrace, vyskyt_kontinent, snuska_ks) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", data)
        flash("Pták přidán.", "success")
        return redirect(url_for("bird_list"))
    return render_template("bird_form.html", bird=None, form_action=url_for("create_bird"), title="Přidat ptáka")

@app.route("/birds/<int:bird_id>/edit", methods=["GET", "POST"])
@login_required
def edit_bird(bird_id):
    with get_db() as conn:
        bird = conn.execute("SELECT * FROM ptaci WHERE id = ?", (bird_id,)).fetchone()
        if request.method == "POST":
            form = request.form
            data = (form.get("nazev", "").strip(), form.get("vedecky_nazev", "").strip(), form.get("rad", "").strip(), form.get("celed", "").strip(), parse_int(form.get("delka_cm")), parse_int(form.get("rozpeti_cm")), parse_int(form.get("hmotnost_g")), form.get("status_ohrozeni", "").strip(), form.get("typ_potravy", "").strip(), 1 if form.get("migrace") == "1" else 0, form.get("vyskyt_kontinent", "").strip(), parse_float(form.get("snuska_ks")), bird_id)
            conn.execute("UPDATE ptaci SET nazev=?, vedecky_nazev=?, rad=?, celed=?, delka_cm=?, rozpeti_cm=?, hmotnost_g=?, status_ohrozeni=?, typ_potravy=?, migrace=?, vyskyt_kontinent=?, snuska_ks=? WHERE id=?", data)
            flash("Upraveno.", "success")
            return redirect(url_for("bird_list"))
    return render_template("bird_form.html", bird=bird, form_action=url_for("edit_bird", bird_id=bird_id), title="Upravit ptáka")

@app.route("/birds/<int:bird_id>/delete", methods=["POST"])
@login_required
def delete_bird(bird_id):
    with get_db() as conn:
        conn.execute("DELETE FROM ptaci WHERE id = ?", (bird_id,))
    flash("Smazáno.", "success")
    return redirect(url_for("bird_list"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)