import psycopg2

def connect_to_db():
    """
    Connect to the database.
    
    :return: Connection to the database and cursor
    
    :Example:
    >>> conn, cur = connect_to_db()
    
    """
    try:
        conn = psycopg2.connect("dbname=database user=user password=password host=localhost port=5432")
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None, None

def close_db_connection(conn, cur):
    """
    Close the database connection.
    
    :param conn: Connection to the database
    :param cur: Cursor
    
    :Example:
    >>> close_db_connection(conn, cur
    
    """
    if cur:
        cur.close()
    if conn:
        conn.close()
