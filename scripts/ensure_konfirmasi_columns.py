"""Ensure required columns exist in konfirmasi_kehadiran table.

Usage:
  python scripts/ensure_konfirmasi_columns.py

The script reads DB credentials from config.py and will ALTER TABLE to add missing columns:
 - token VARCHAR(100) UNIQUE
 - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""
import pymysql
import config

conn = pymysql.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
try:
    with conn.cursor() as cur:
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='konfirmasi_kehadiran'", (config.DB_NAME,))
        cols = {r[0] for r in cur.fetchall()}
        alters = []
        if 'token' not in cols:
            alters.append("ADD COLUMN token VARCHAR(100) UNIQUE")
        if 'created_at' not in cols:
            alters.append("ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        if alters:
            sql = "ALTER TABLE konfirmasi_kehadiran " + ", ".join(alters)
            print('Running:', sql)
            cur.execute(sql)
            conn.commit()
            print('Done. Added columns:', alters)
        else:
            print('No changes needed; columns already present.')
finally:
    conn.close()
