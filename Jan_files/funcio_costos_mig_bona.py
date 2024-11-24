import math
import psycopg2
from shapely import LineString, Point
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
    
def get_closest_point_to_origin(data, origin_coords):
    # Convert origin coordinates to a Point
    origin_point = Point(origin_coords)
    closest_points = []
    
    for record in data:
        # Adjust unpacking based on the structure of `data`
        geom_id = record[0]
        multipath_wkt = record[1]
        
        geom = loads(multipath_wkt)  # Parse WKT into geometry
        min_distance = float('inf')
        closest_point = None
        
        # Handle LINESTRING and MULTILINESTRING
        if geom.geom_type == "LineString":
            points = list(geom.coords)
        elif geom.geom_type == "MultiLineString":
            points = [coord for line in geom for coord in line.coords]
        else:
            continue
        
        # Find the closest point
        for point in points:
            shapely_point = Point(point)
            distance = origin_point.distance(shapely_point)
            if distance < min_distance:
                min_distance = distance
                closest_point = shapely_point
        
        closest_points.append((geom_id, closest_point))
    
    return closest_points[0]

def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)    

def distance_count(coordinates):
    
    # Initialize the total distance
    total_distance = 0

    # Calculate the distance between each pair of consecutive points
    for i in range(len(coordinates) - 1):
        total_distance += calculate_distance(coordinates[i], coordinates[i+1])

    print("Distance_not_normalized:", total_distance)
    
    print("Distance_normalized:", total_distance*25830/1326)
    return total_distance*25830/1326

def get_segment_between_points(cur, origin_coords, dest_coords, path_id):
    
    slect_entry_from_table_multipoint_undone = f"""
    SELECT ST_AsText(ST_LineMerge(geom)) AS line_1
    FROM eps.red3
    WHERE id = {path_id};
    """
    cur.execute(slect_entry_from_table_multipoint_undone)
    data_geometry = cur.fetchall()
    
    coordinates = extract_coordinates_from_MULTIPATH(data_geometry)
    print("Coordinates:", coordinates)    
    
        
    if (origin_coords in coordinates) and (dest_coords in coordinates):
        return_coordinates = coordinates[coordinates.index(origin_coords):coordinates.index(dest_coords)+1] 
        print(return_coordinates)
        if distance_count(coordinates=return_coordinates) == 0:
            return_coordinates = coordinates[coordinates.index(dest_coords):coordinates.index(origin_coords)+1] 

        print("Return Coordinates:", return_coordinates)
        return distance_count(coordinates=return_coordinates) * 10 # edit cost if not red3
    else:
        return 0.0


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
    print("Origen", origin)
    origin_coords = extract_coordinates_from_MULTIPOINT(origin)
    
    select_dest_node_point = f"""
    SELECT ST_AsText((ST_Dump(geom)).geom) AS single_point
    FROM eps.red3_puntos
    WHERE id = {node_d};
    """
    cur.execute(select_dest_node_point)
    dest = cur.fetchall()
    print("Dest", dest)
    dest_coords = extract_coordinates_from_MULTIPOINT(dest)
    
    
    
    # GET THE 10 CLOSESTS GEOMETRY TO ORIGIN

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
    ranked_list = ranked_lists(origin_ids_list, dest_ids_list)
    print("Ranked List", ranked_list)
    
    
    # GET POINTS CLOSEST TO NODE
    # origin
    slect_entry_from_table_multipoint_undone = f"""
    SELECT id, ST_AsText(ST_LineMerge(geom)) AS line_1
    FROM eps.red3
    WHERE id = {ranked_list[0]};
    """
    cur.execute(slect_entry_from_table_multipoint_undone)
    data_geometry = cur.fetchall()
    print("Data Geometry:", data_geometry)
    
    point_closest_origin = get_closest_point_to_origin(data=data_geometry, origin_coords=origin_coords)
    point_closest_origin = (point_closest_origin[1].x, point_closest_origin[1].y)
    print("Point closest to A: ", point_closest_origin)
    
    # dest
    point_closest_dest = get_closest_point_to_origin(data=data_geometry, origin_coords=dest_coords)
    point_closest_dest = (point_closest_dest[1].x, point_closest_dest[1].y)
    print("Point closest to B: ", point_closest_dest)
    
    
    # GET 
    
    # GET PATH BETWEEN ORIGIN AND DEST
    
    cost = get_segment_between_points(cur, point_closest_origin, point_closest_dest, ranked_list[0])
    print(cost)
    
    return cost



    
   
    


    
 
get_cost(node_o=7228, node_d=7232)