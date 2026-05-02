import psycopg2
import os

DB_USER = "postgres"
DB_PASS = "2721"
DB_HOST = "localhost"
DB_NAME = "circulacion_db"

def insert_sample_data():
    try:
        conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, dbname=DB_NAME)
        cur = conn.cursor()
        
        filename = "db_init/03_sample_data.sql"
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        cur.execute(content)
        conn.commit()
        print(f"Datos de ejemplo insertados exitosamente desde {filename}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting sample data: {e}")

if __name__ == "__main__":
    insert_sample_data()
