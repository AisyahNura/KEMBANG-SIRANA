"""Fix: Change status_kehadiran to VARCHAR(50) to allow NULL, then test."""
import pymysql
import config

conn = pymysql.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

try:
    with conn.cursor() as cur:
        print("Modifying status_kehadiran column...")
        cur.execute("ALTER TABLE konfirmasi_kehadiran MODIFY COLUMN status_kehadiran VARCHAR(50) NULL")
        conn.commit()
        print("✓ Column changed to VARCHAR(50) NULL")
        
        # Clear all entries
        cur.execute("DELETE FROM konfirmasi_kehadiran WHERE undangan_id = 36")
        conn.commit()
        print("✓ Cleared old entries")
        
        # Insert fresh one
        import secrets
        TOKEN = secrets.token_urlsafe(32)
        cur.execute(
            "INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token) VALUES (%s, %s, %s, %s)",
            (36, 'Tamu Uji', 'uji@example.com', TOKEN)
        )
        conn.commit()
        print(f"✓ Fresh token: {TOKEN}")
        print(f"\n🔗 http://127.0.0.1:5000/kehadiran/{TOKEN}")

finally:
    conn.close()
