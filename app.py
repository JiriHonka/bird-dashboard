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
    status_filter = request.args.getlist("status_ohrozeni")
    typ_potravy_filter = request.args.getlist("typ_potravy")
    kontinent_filter = request.args.getlist("vyskyt_kontinent")
    migrace_filter = request.args.getlist("migrace")
 
    # Build dynamic query
    query = "SELECT * FROM ptaci WHERE 1=1"
    params = []
 
    if status_filter:
        placeholders = ",".join("?" * len(status_filter))
        query += f" AND status_ohrozeni IN ({placeholders})"
        params.extend(status_filter)
 
    if typ_potravy_filter:
        placeholders = ",".join("?" * len(typ_potravy_filter))
        query += f" AND typ_potravy IN ({placeholders})"
        params.extend(typ_potravy_filter)
 
    if kontinent_filter:
        placeholders = ",".join("?" * len(kontinent_filter))
        query += f" AND vyskyt_kontinent IN ({placeholders})"
        params.extend(kontinent_filter)
 
    if migrace_filter:
        placeholders = ",".join("?" * len(migrace_filter))
        query += f" AND migrace IN ({placeholders})"
        params.extend([int(m) for m in migrace_filter])
 
    query += " ORDER BY nazev ASC"
    cursor.execute(query, params)
    ptaci = cursor.fetchall()
 
    # Get all unique values for filter dropdowns
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
        statuses=statuses,
        typy_potravy=typy_potravy,
        kontinenty=kontinenty,
        selected_status=status_filter,
        selected_typ=typ_potravy_filter,
        selected_kontinent=kontinent_filter,
        selected_migrace=migrace_filter,
        celkem=len(ptaci)
    )
 
if __name__ == "__main__":
    app.run(debug=True)