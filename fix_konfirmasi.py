"""Quick fix: add missing columns and insert test token locally."""
import pymysql
import config
import secrets

TOKEN = 'DuJNKRrAKfN7jA1usbju5V9NX6ho2XHehrXJGxorhgk'
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
        # Check and add token column
        cur.execute("SHOW COLUMNS FROM konfirmasi_kehadiran LIKE 'token'")
        if cur.fetchone() is None:
            print("Adding token column...")
            cur.execute("ALTER TABLE konfirmasi_kehadiran ADD COLUMN token VARCHAR(100) UNIQUE")
            conn.commit()
            print("✓ token column added")
        else:
            print("✓ token column already exists")

        # Check and add created_at column
        cur.execute("SHOW COLUMNS FROM konfirmasi_kehadiran LIKE 'created_at'")
        if cur.fetchone() is None:
            print("Adding created_at column...")
            cur.execute("ALTER TABLE konfirmasi_kehadiran ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("✓ created_at column added")
        else:
            print("✓ created_at column already exists")

        # Verify undangan exists
        cur.execute("SELECT id, kegiatan FROM undangan WHERE id = %s", (UNDANGAN_ID,))
        row = cur.fetchone()
        if row is None:
            print(f"✗ Undangan id {UNDANGAN_ID} not found")
            conn.close()
            exit(1)
        print(f"✓ Found undangan: {row}")

        # Insert token
        cur.execute("DELETE FROM konfirmasi_kehadiran WHERE token = %s", (TOKEN,))
        cur.execute(
            "INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token) VALUES (%s, %s, %s, %s)",
            (UNDANGAN_ID, NAMA, EMAIL, TOKEN)
        )
        conn.commit()
        print(f"✓ Token inserted for undangan_id {UNDANGAN_ID}")
        print(f"\n🔗 Open this URL in browser:")
        print(f"   http://127.0.0.1:5000/kehadiran/{TOKEN}")

finally:
    conn.close()
