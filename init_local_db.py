import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

# Parametros de conexion (usando los proporcionados por el usuario)
DB_USER = "localhost" 
DB_PASS = "2721"
DB_HOST = "localhost"
DB_NAME = "circulacion_db"

def init_db():
    try:
        # 1. Conectar a postgres para crear la base de datos
        # Intentamos con 'localhost' y si falla con 'postgres'
        try:
            conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, dbname="postgres")
        except:
            print("Fallo con usuario 'localhost', intentando con 'postgres'...")
            conn = psycopg2.connect(user="postgres", password=DB_PASS, host=DB_HOST, dbname="postgres")
            
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        cur.close()
        conn.close()
        print(f"Base de datos {DB_NAME} creada.")

        # 2. Conectar a la nueva base de datos
        try:
            conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, dbname=DB_NAME)
        except:
            conn = psycopg2.connect(user="postgres", password=DB_PASS, host=DB_HOST, dbname=DB_NAME)
            
        cur = conn.cursor()
        
        # Leer y ejecutar esquema con encoding flexible
        for filename in ["db_init/01_schema.sql", "db_init/02_seed.sql"]:
            content = ""
            for enc in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(filename, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content:
                cur.execute(content)
                print(f"Ejecutado: {filename}")
            else:
                print(f"No se pudo leer {filename}")

        conn.commit()
        cur.close()
        conn.close()
        print("Inicialización completada exitosamente.")
        
    except Exception as e:
        print(f"Error initializing DB: {e}")

if __name__ == "__main__":
    init_db()
