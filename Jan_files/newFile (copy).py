import psycopg2
from shapely.wkt import loads

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
    >>> close_db_connection(conn, cur)
    
    """
    if cur:
        cur.close()
    if conn:
        conn.close()

def extract_coordinates_from_MULTIPATH(multipath):
    # Extract WKT string
    linestring_wkt = multipath[0][0]

    # Parse WKT using Shapely
    linestring = loads(linestring_wkt)

    # Access coordinates as a list of (x, y) tuples
    return list(linestring.coords)
    
def extract_coordinates_from_MULTIPOINT(multipoint):
    # Extract WKT string
    multipoint_wkt = multipoint[0][0]

    # Parse MULTIPOINT using Shapely
    multipoint = loads(multipoint_wkt)

    # Access individual points
    return list(multipoint.coords)


def path2path(node_o, node_d, net_name):
    # Ens conectem a la Base de Dades
    conn, cur = connect_to_db()
    
    # Agafem les dades de les taules
    
    
    # --- Implement A*
    
    slect_all_table_names = f"""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_type = 'BASE TABLE';
    """
    slect_entry_from_table = f"""
    SELECT * FROM eps.red3 WHERE id = {node_o} 
    """
    
    slect_entry_from_table_multipath_undone = f"""
    SELECT ST_AsText(ST_LineMerge(geom)) AS line_1
    FROM eps.red3
    WHERE id = {node_o};
    """
    
    slect_entry_from_table_multipoint_undone = f"""
    SELECT ST_AsText((ST_Dump(geom)).geom) AS single_point
    FROM eps.red3_puntos
    WHERE id = 1;
    """
    
    
    
    # EXTRACT COORDINATES FROM MULTIPATH
    cur.execute(slect_entry_from_table_multipath_undone)
    mtpth = cur.fetchall()
    mtpth_coord = extract_coordinates_from_MULTIPATH(mtpth)

    # EXTRACT COORDINATES FROM MULTIPOINT
    cur.execute(slect_entry_from_table_multipoint_undone)
    mtppt = cur.fetchall()
    mtppt_coords = extract_coordinates_from_MULTIPOINT(mtppt)
    
    print(mtpth_coord)
    print(mtpth_coord[-1])

   
    print("Done")
    
    
    ## ............................... TEST BANK
    
    proves4 = f"""
    SELECT rp.*
    FROM eps.red3_puntos rp
    JOIN eps.red3 r
    ON ST_Intersects(r.geom, rp.geom);
    """
    cur.execute(slect_entry_from_table_multipoint_undone)
    mppth = cur.fetchall()
    print(mtpth[0])
    print("Done")
    
    sql = """
    SELECT * FROM pgr_dijkstra(
        'SELECT id, source, target, cost FROM your_network_table',
        %s, %s, directed := true);
    """
    
    sql_2 = """
    SELECT * FROM pgr_aStar(
        'SELECT id, source, target, cost, reverse_cost, x1, y1, x2, y2 FROM net_name',
        6, 12, directed => false, heuristic => 2);
    
    """
    
    # Ens desconectem de la Base de Dades
    close_db_connection(conn, cur)

path2path(node_o=107286, node_d=107288, net_name="red3")