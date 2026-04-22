import sqlite3
import csv

# Connect to SQLite database
conn = sqlite3.connect("ptaci.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS ptaci (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT,
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
);
""")

# Read CSV file
with open("dataset_ptaci_final.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    data = [
        (
            row["nazev"],
            row["vedecky_nazev"],
            row["rad"],
            row["celed"],
            int(row["delka_cm"]),
            int(row["rozpeti_cm"]),
            int(row["hmotnost_g"]),
            row["status_ohrozeni"],
            row["typ_potravy"],
            int(row["migrace"]),
            row["vyskyt_kontinent"],
            float(row["snuska_ks"])
        )
        for row in reader
    ]

# Insert data into the table
cursor.executemany("""
INSERT INTO ptaci (
    nazev, vedecky_nazev, rad, celed, delka_cm, rozpeti_cm, hmotnost_g,
    status_ohrozeni, typ_potravy, migrace, vyskyt_kontinent, snuska_ks
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", data)

# Commit and close
conn.commit()
print(f"Imported {len(data)} records into the database.")
conn.close()