
try:
    import mysql.connector  # type: ignore[reportMissingImports]
except ImportError as exc:
    raise SystemExit(
        "MySQL connector package is not installed. Install it with: pip install mysql-connector-python"
    ) from exc

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="employee_db",
        port=3306
    )

    if conn.is_connected():
        print("MySQL Database Connected Successfully!")

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")

        print("Tables in database:")
        for table in cursor.fetchall():
            print(table)

        cursor.close()
        conn.close()

except mysql.connector.Error as err:
    print("Connection failed:", err)
