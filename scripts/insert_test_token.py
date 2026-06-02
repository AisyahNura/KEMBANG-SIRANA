"""Insert a test token into konfirmasi_kehadiran using project's DB config.

Usage:
  python scripts/insert_test_token.py --undangan-id 1 --nama "Tamu Uji" --email uji@example.com

The script reads DB credentials from config.py in project root.
"""
import argparse
import secrets
import pymysql
import config

parser = argparse.ArgumentParser()
parser.add_argument('--undangan-id', type=int, required=True)
parser.add_argument('--nama', type=str, default='Tamu Uji')
parser.add_argument('--email', type=str, default='uji@example.com')
parser.add_argument('--token', type=str, default=None)
args = parser.parse_args()

token = args.token or secrets.token_urlsafe(32)

conn = pymysql.connect(host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD, database=config.DB_NAME)
try:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM undangan WHERE id = %s", (args.undangan_id,))
        if cur.fetchone() is None:
            print(f"Undangan id {args.undangan_id} tidak ditemukan.")
        else:
            cur.execute(
                "INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token) VALUES (%s, %s, %s, %s)",
                (args.undangan_id, args.nama, args.email, token)
            )
            conn.commit()
            print('Inserted test token:', token)
            print('Open this URL in browser: http://127.0.0.1:5000/kehadiran/' + token)
finally:
    conn.close()
