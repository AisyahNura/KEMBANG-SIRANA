"""Force: delete all old entries and create fresh token with truly NULL status."""
import pymysql
import config
import secrets

TOKEN = secrets.token_urlsafe(32)
UNDANGAN_ID = 36
NAMA = 'Tamu Uji'
EMAIL = 'uji@example.com'

conn = pymysql.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

try:
    with conn.cursor() as cur:
        # Delete ALL entries for this undangan to clean slate
        cur.execute("DELETE FROM konfirmasi_kehadiran WHERE undangan_id = %s", (UNDANGAN_ID,))
        conn.commit()
        print(f"✓ Deleted all old entries for undangan {UNDANGAN_ID}")
        
        # Insert ONE fresh entry - only the required columns
        cur.execute("""
            INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token)
            VALUES (%s, %s, %s, %s)
        """, (UNDANGAN_ID, NAMA, EMAIL, TOKEN))
        conn.commit()
        
        # Verify it was inserted with NULL status
        cur.execute("SELECT id, undangan_id, nama, email, token, status_kehadiran FROM konfirmasi_kehadiran WHERE token = %s", (TOKEN,))
        row = cur.fetchone()
        if row:
            print(f"✓ New entry: {row}")
            print(f"\n🔗 OPEN THIS URL (fresh token, no status yet):")
            print(f"   http://127.0.0.1:5000/kehadiran/{TOKEN}")
        else:
            print("✗ Failed to insert")

finally:
    conn.close()
