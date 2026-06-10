import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv

def create_connection():
    load_dotenv()
    try:
        db_url = os.getenv("DB_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
            return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    

def create_table_anubhav(conn):
    try:
        cursor = conn.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS anubhav_sales (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(20) NOT NULL UNIQUE,
            date DATE NOT NULL,
            sales_agent_last_name VARCHAR(50),
            sales_agent_first_name VARCHAR(50),
            customer VARCHAR(100),
            customer_segment VARCHAR(50),
            country VARCHAR(50),
            latitude DECIMAL(10,7),
            longitude DECIMAL(10,7),
            customer_status VARCHAR(20),
            product VaRCHAR(100),
            product_type VARCHAR(50),
            no_customer_meetings INTEGER,
            units_sold INTEGER,
            order_value DECIMAL(15,2)
        );
        '''
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        print("Table 'anubhav_sales' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")


def load_data_from_excel(file_path):
    df = pd.read_excel(file_path)
    data = df.to_dict(orient='records')
    return data

def insert_data(conn, data):
    try:
        cursor = conn.cursor()
        insert_query = '''
        INSERT INTO anubhav_sales (
            order_id, date, sales_agent_last_name, sales_agent_first_name,
            customer, customer_segment, country, latitude, longitude,
            customer_status, product, product_type, no_customer_meetings,
            units_sold, order_value
        ) VALUES (
            %(order_id)s, %(date)s, %(sales_agent_last_name)s, %(sales_agent_first_name)s,
            %(customer)s, %(customer_segment)s, %(country)s, %(latitude)s, %(longitude)s,
            %(customer_status)s, %(product)s, %(product_type)s, %(no_customer_meetings)s,
            %(units_sold)s, %(order_value)s
        ) ON CONFLICT (order_id) DO NOTHING;
        '''
        cursor.executemany(insert_query, data)
        conn.commit()
        cursor.close()
        print(f"Inserted {cursor.rowcount} records into 'anubhav_sales'.")
    except Exception as e:
        print(f"Error inserting data: {e}")

##Read the data from DB and return dataframe
def read_data(conn):
    if conn is None:
        conn = create_connection()
        
    try:
        df = pd.read_sql("SELECT * FROM anubhav_sales;", conn)
        return df
    except Exception as e:
        print(f"Error reading data: {e}")
        return pd.DataFrame()        
    
def main():
    conn = create_connection()
    if conn:
        create_table_anubhav(conn)
        data = load_data_from_excel('./Sales_Data.xlsx')
        insert_data(conn, data)
        df = read_data(conn)
        print(df.head())
        conn.close()

if __name__ == "__main__":
    main()