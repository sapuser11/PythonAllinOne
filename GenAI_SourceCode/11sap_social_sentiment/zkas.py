from hdbcli import dbapi

def connect_to_hana():
    # Local parameters for connection (replace with actual values or use input())
    host = "dfe44c2a-1282-4fab-b4e2-6c5f19516f88.hana.trial-us10.hanacloud.ondemand.com"
    port = 443             # typically 3<instance_number>15
    user = "DBADMIN"
    password = "Welcome1"

    try:
        # Establish connection
        conn = dbapi.connect(
            address=host,
            port=port,
            user=user,
            password=password
        )
        print("Connection successful!")

        # Create a cursor to execute SQL
        cursor = conn.cursor()
        cursor.execute('SELECT TO_NVARCHAR(SYSUUID) as UUID FROM DUMMY')

        # Fetch and print result
        # for row in cursor.fetchall():
        #     print(row)

        print(cursor.fetchone()["UUID"])
        # Close cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    connect_to_hana()
