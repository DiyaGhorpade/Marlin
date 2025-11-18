import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="marlin_admin",
        password="Marlin@123"
    )
    print("Connected!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
