"""Create fresh token with NULL status for testing."""
import pymysql
import secrets
import config

conn = pymysql.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

try:
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        # Check current state
        cur.execute("SELECT * FROM konfirmasi_kehadiran WHERE undangan_id = 36 ORDER BY created_at DESC")
        rows = cur.fetchall()
        print(f"Current entries for undangan_id=36: {len(rows)}")
        for r in rows:
            print(f"  - token={r['token'][:10]}..., status={r.get('status_kehadiran')}, nama={r.get('nama')}")
        
        # Delete all
        cur.execute("DELETE FROM konfirmasi_kehadiran WHERE undangan_id = 36")
        conn.commit()
        print("\n✓ Deleted all entries for undangan_id=36")
        
        # Insert fresh
        TOKEN = secrets.token_urlsafe(32)
        cur.execute(
            "INSERT INTO konfirmasi_kehadiran (undangan_id, nama, email, token, status_kehadiran) VALUES (%s, %s, %s, %s, %s)",
            (36, 'Tamu Uji', 'uji@example.com', TOKEN, None)
        )
        conn.commit()
        print(f"✓ Inserted fresh token")
        
        # Verify
        cur.execute("SELECT token, status_kehadiran, nama FROM konfirmasi_kehadiran WHERE token = %s", (TOKEN,))
        row = cur.fetchone()
        print(f"\nVerify:")
        print(f"  - token: {row['token'][:10]}...")
        print(f"  - status_kehadiran: {row['status_kehadiran']} (should be None/NULL)")
        print(f"  - nama: {row['nama']}")
        
        print(f"\n🔗 http://127.0.0.1:5000/kehadiran/{TOKEN}")
        print("\nCopy the token and paste in browser.")

finally:
    conn.close()
