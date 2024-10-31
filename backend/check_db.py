import psycopg2

def check_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="tms_db",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
        )
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    check_db_connection()