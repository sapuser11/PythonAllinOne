import psycopg2
import os
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()

    try:
        db_url = os.getenv("DB_URL")

        if not db_url:
            raise Exception("❌ DB_URL not loaded from .env")
    
        conn = psycopg2.connect(db_url)

        query_sql = 'SELECT VERSION()'

        cur = conn.cursor()
        cur.execute(query_sql)

        version = cur.fetchone()[0]
        print("connected Postgres " + version)
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

def execute_ddl(conn, table_name, columns):
        """
        Create a table with the given name and columns.
        columns: list of tuples (column_name, column_type)
        """
        cols = ', '.join([f"{name} {dtype}" for name, dtype in columns])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols});"
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()

def create_table_anubhav(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS anubhav_training (
                id SERIAL PRIMARY KEY,
                course_name VARCHAR(50) UNIQUE,
                trainer VARCHAR(100),
                price INTEGER,
                duration INTEGER
            );
        """)
        conn.commit()

def execute_dql(conn, query, params=None):
        """
        Execute a query and return all results.
        """
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if cur.description:
                return cur.fetchall()
            return None

def execute_dml(conn, data):
    with conn.cursor() as cur:
        for course_name, details in data.items():
            cur.execute("""
                INSERT INTO anubhav_training (course_name, trainer, price, duration)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (course_name) DO NOTHING;
            """, (course_name, details["trainer"], details["price"], details["hours"]))
        conn.commit()

if __name__ == "__main__":
    main()