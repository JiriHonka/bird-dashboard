# bird-dashboard

## Reset database

The application uses a local SQLite database file `ptaci.db`.
To restore the default dataset, delete `ptaci.db` and then run:

```bash
python -c "from app import init_db; init_db()"
python import_csv.py
```
