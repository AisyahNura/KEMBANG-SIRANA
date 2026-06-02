"""Create a fresh token with NULL status_kehadiran (to show chatbot)."""
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
        # Delete old test tokens
        cur.execute("DELETE FROM konfirmasi_kehadiran WHERE undangan_id = %s AND nama = %s", (UNDANGAN_ID, NAMA))
        
        # Insert fresh token (tidak sebutkan status_kehadiran, biar DB handle default-nya)
        cur.execute("""
            INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token)
            VALUES (%s, %s, %s, %s)
        """, (UNDANGAN_ID, NAMA, EMAIL, TOKEN))
        conn.commit()
        print(f"✓ Fresh token created")
        print(f"\n🔗 Open URL:")
        print(f"   http://127.0.0.1:5000/kehadiran/{TOKEN}")

finally:
    conn.close()
