from flask import Flask, render_template, request
import sqlite3
 
app = Flask(__name__)
 
def get_db():
    conn = sqlite3.connect("ptaci.db")
    conn.row_factory = sqlite3.Row
    return conn
 
@app.route("/")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
 
    # Get filter values from query params
    rad_filter = [v for v in request.args.getlist("rad") if v]
    status_filter = [v for v in request.args.getlist("status_ohrozeni") if v]
    typ_potravy_filter = [v for v in request.args.getlist("typ_potravy") if v]
    kontinent_filter = [v for v in request.args.getlist("vyskyt_kontinent") if v]
    migrace_filter = [v for v in request.args.getlist("migrace") if v]
    hmotnost_od = request.args.get("hmotnost_od")
    hmotnost_do = request.args.get("hmotnost_do")
 
    # Build dynamic query and matching summary query
    query = "SELECT * FROM ptaci WHERE 1=1"
    stats_query = "SELECT COUNT(*), AVG(delka_cm), AVG(hmotnost_g), MAX(hmotnost_g) FROM ptaci WHERE 1=1"
    order_query = "SELECT rad, COUNT(*) AS cnt FROM ptaci WHERE 1=1"
    migration_query = "SELECT SUM(migrace) AS tazni, COUNT(*) - SUM(migrace) AS netazni FROM ptaci WHERE 1=1"
    weight_query = "SELECT typ_potravy, AVG(hmotnost_g) AS avg_hmotnost FROM ptaci WHERE 1=1"
    continent_query = "SELECT vyskyt_kontinent, COUNT(*) AS cnt FROM ptaci WHERE 1=1"
    params = []
 
    if rad_filter:
        placeholders = ",".join("?" * len(rad_filter))
        clause = f" AND rad IN ({placeholders})"
        query += clause
        stats_query += clause
        order_query += clause
        migration_query += clause
        params.extend(rad_filter)
 
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        clause = f" AND status_ohrozeni IN ({placeholders})"
        query += clause
        stats_query += clause
        order_query += clause
        migration_query += clause
        weight_query += clause
        continent_query += clause
        params.extend(status_filter)
 
    if typ_potravy_filter:
        placeholders = ",".join("?" * len(typ_potravy_filter))
        clause = f" AND typ_potravy IN ({placeholders})"
        query += clause
        stats_query += clause
        order_query += clause
        migration_query += clause
        weight_query += clause
        continent_query += clause
        params.extend(typ_potravy_filter)
 
    if kontinent_filter:
        placeholders = ",".join("?" * len(kontinent_filter))
        clause = f" AND vyskyt_kontinent IN ({placeholders})"
        query += clause
        stats_query += clause
        order_query += clause
        migration_query += clause
        weight_query += clause
        continent_query += clause
        params.extend(kontinent_filter)
 
    if migrace_filter:
        placeholders = ",".join("?" * len(migrace_filter))
        clause = f" AND migrace IN ({placeholders})"
        query += clause
        stats_query += clause
        order_query += clause
        migration_query += clause
        weight_query += clause
        continent_query += clause
        valid_migrace = []
        for m in migrace_filter:
            try:
                valid_migrace.append(int(m))
            except ValueError:
                continue
        params.extend(valid_migrace)
 
    if hmotnost_od:
        try:
            val = int(hmotnost_od)
            query += " AND hmotnost_g >= ?"
            stats_query += " AND hmotnost_g >= ?"
            order_query += " AND hmotnost_g >= ?"
            migration_query += " AND hmotnost_g >= ?"
            weight_query += " AND hmotnost_g >= ?"
            continent_query += " AND hmotnost_g >= ?"
            params.append(val)
        except ValueError:
            pass
 
    if hmotnost_do:
        try:
            val = int(hmotnost_do)
            query += " AND hmotnost_g <= ?"
            stats_query += " AND hmotnost_g <= ?"
            order_query += " AND hmotnost_g <= ?"
            migration_query += " AND hmotnost_g <= ?"
            weight_query += " AND hmotnost_g <= ?"
            continent_query += " AND hmotnost_g <= ?"
            params.append(val)
        except ValueError:
            pass
 
    query += " ORDER BY nazev ASC"
    cursor.execute(query, params)
    ptaci = cursor.fetchall()
 
    cursor.execute(stats_query, params)
    count, avg_delka, avg_hmotnost, max_hmotnost = cursor.fetchone()
    avg_delka = round(avg_delka, 1) if avg_delka is not None else 0
    avg_hmotnost = round(avg_hmotnost, 1) if avg_hmotnost is not None else 0
    max_hmotnost = max_hmotnost if max_hmotnost is not None else 0
 
    cursor.execute(migration_query, params)
    tazni, netazni = cursor.fetchone()
    tazni = int(tazni or 0)
    netazni = int(netazni or 0)
 
    order_query += " GROUP BY rad ORDER BY cnt DESC, rad ASC LIMIT 5"
    cursor.execute(order_query, params)
    rad_rows = cursor.fetchall()
    rad_labels = [row[0] for row in rad_rows]
    rad_counts = [row[1] for row in rad_rows]
 
    weight_query += " GROUP BY typ_potravy ORDER BY avg_hmotnost DESC"
    cursor.execute(weight_query, params)
    weight_rows = cursor.fetchall()
    weight_labels = [row[0] for row in weight_rows]
    weight_avgs = [round(row[1], 1) for row in weight_rows]
 
    continent_query += " GROUP BY vyskyt_kontinent ORDER BY cnt DESC"
    cursor.execute(continent_query, params)
    continent_rows = cursor.fetchall()
    continent_labels = [row[0] for row in continent_rows]
    continent_counts = [row[1] for row in continent_rows]
 
    # Get all unique values for filter dropdowns
    cursor.execute("SELECT DISTINCT rad FROM ptaci ORDER BY rad")
    rady = [row[0] for row in cursor.fetchall()]
 
    cursor.execute("SELECT DISTINCT status_ohrozeni FROM ptaci ORDER BY status_ohrozeni")
    statuses = [row[0] for row in cursor.fetchall()]
 
    cursor.execute("SELECT DISTINCT typ_potravy FROM ptaci ORDER BY typ_potravy")
    typy_potravy = [row[0] for row in cursor.fetchall()]
 
    cursor.execute("SELECT DISTINCT vyskyt_kontinent FROM ptaci ORDER BY vyskyt_kontinent")
    kontinenty = [row[0] for row in cursor.fetchall()]
 
    conn.close()
 
    return render_template(
        "dashboard.html",
        ptaci=ptaci,
        rady=rady,
        statuses=statuses,
        typy_potravy=typy_potravy,
        kontinenty=kontinenty,
        selected_rad=rad_filter,
        selected_status=status_filter,
        selected_typ=typ_potravy_filter,
        selected_kontinent=kontinent_filter,
        selected_migrace=migrace_filter,
        selected_hmotnost_od=hmotnost_od,
        selected_hmotnost_do=hmotnost_do,
        celkem=count,
        prumerna_delka=avg_delka,
        prumerna_hmotnost=avg_hmotnost,
        max_hmotnost=max_hmotnost,
        rad_labels=rad_labels,
        rad_counts=rad_counts,
        tazni_count=tazni,
        netazni_count=netazni,
        weight_labels=weight_labels,
        weight_avgs=weight_avgs,
        continent_labels=continent_labels,
        continent_counts=continent_counts
    )
 
if __name__ == "__main__":
    app.run(debug=True)