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
    mp_list = []
    for i in range(0, len(multipoint)):
        # Extract WKT string
        multipoint_wkt = multipoint[i][0]

        # Parse MULTIPOINT using Shapely
        linestring = loads(multipoint_wkt)
        
        mp_list.append(list(linestring.coords))

    # Access individual points
    return mp_list[0]

def ranked_lists(origin_ids_list, dest_ids_list):
    
    # Create a dictionary to store ranks from both lists
    rank_dict = {}

    # Add ranks from the origin list
    for rank, vertex in enumerate(origin_ids_list):
        rank_dict[vertex] = rank_dict.get(vertex, 0) + rank

    # Add ranks from the destination list
    for rank, vertex in enumerate(dest_ids_list):
        rank_dict[vertex] = rank_dict.get(vertex, len(origin_ids_list)) + rank

    # Sort vertices by combined rank
    return sorted(rank_dict.keys(), key=lambda v: rank_dict[v])
    


def get_cost(node_o, node_d):
    # Ens conectem a la Base de Dades
    conn, cur = connect_to_db()
    
    cost = 0
    
    # GET ORIGIN AND DESTINATION POINTS
    select_origin_node_point = f"""
    SELECT ST_AsText((ST_Dump(geom)).geom) AS single_point
    FROM eps.red3_puntos
    WHERE id = {node_o};
    """
    cur.execute(select_origin_node_point)
    origin = cur.fetchall()
    origin_coords = extract_coordinates_from_MULTIPOINT(origin)
    
    select_dest_node_point = f"""
    SELECT ST_AsText((ST_Dump(geom)).geom) AS single_point
    FROM eps.red3_puntos
    WHERE id = {node_d};
    """
    cur.execute(select_origin_node_point)
    dest = cur.fetchall()
    dest_coords = extract_coordinates_from_MULTIPOINT(dest)
    
    
    
    # GET THE 10 CLOSESTS GEOMETRY TO ORIGIN
    
    print(origin_coords)
    
    closests_to_origin_query = f"""    
    WITH reference_point AS (
        SELECT ST_SetSRID(ST_MakePoint{origin_coords[0]}, 25830) AS geom
    )
    SELECT 
        r.id, 
        ST_AsText(ST_LineMerge(r.geom)) AS line_1,
        ST_Distance(r.geom, reference_point.geom) AS distance
    FROM 
        eps.red3 AS r, 
        reference_point
    WHERE 
        ST_DWithin(r.geom, reference_point.geom, 100) -- 100 is the range
    ORDER BY 
        distance ASC
    LIMIT 10;

    """
    
    cur.execute(closests_to_origin_query)
    closests_to_origin_data = cur.fetchall()
    
    
    # GET THE 10 CLOSESTS GEOMETRY TO THE DESTINATION
    
    closests_to_dest_query = f"""    
    WITH reference_point AS (
        SELECT ST_SetSRID(ST_MakePoint{dest_coords[0]}, 25830) AS geom
    )
    SELECT 
        r.id, 
        ST_AsText(ST_LineMerge(r.geom)) AS line_1,
        ST_Distance(r.geom, reference_point.geom) AS distance
    FROM 
        eps.red3 AS r, 
        reference_point
    WHERE 
        ST_DWithin(r.geom, reference_point.geom, 100) -- 100 is the range
    ORDER BY 
        distance ASC
    LIMIT 10;
    """
    
    cur.execute(closests_to_dest_query)
    closests_to_dest_data = cur.fetchall()
    
    
    # GET THE CLOSEST ID
    origin_ids_list = [row[0] for row in closests_to_origin_data]
    dest_ids_list = [row[0] for row in closests_to_dest_data]
    print(origin_ids_list)
    print(dest_ids_list)
    ranked_list = ranked_lists(origin_ids_list, dest_ids_list)
    print(ranked_list)
    
    # GET THE COST OF THE WHOLE CLOSEST PATH
    calculate_cost_query = f"""
    SELECT 
        ST_Length(geom) * 10 AS cost
    FROM 
        eps.red3
    WHERE 
        id = {ranked_list[0]};
    """


    # Execute the query with the specific ID
    cur.execute(calculate_cost_query)

    # Fetch the result
    line_cost = cur.fetchone()

    # Print the cost
    print(f"The total cost for LINESTRING with ID 111 is: {line_cost[0]} units.")

    
    return cost

    
get_cost(node_o=2986, node_d=2983)