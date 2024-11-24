from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant
from python_functions import db_connect as db

def point2path(point, path):
    """
    Encuentra el punto más cercano en una línea a partir de un punto dado y una ruta en la base de datos.

    :param point: Un objeto QgsPointXY que representa el punto de entrada.
    :param path: Una cadena que representa el nombre de la tabla en la base de datos donde se encuentran las líneas.

    :return: Un objeto QgsPointXY que representa el punto más cercano en la línea.
    """
    conn, cur = db.connect_to_db()

    # Convertir QgsPointXY a WKT
    point_wkt = f"POINT({point.x()} {point.y()})"

    # Encontrar el punto más cercano en la red utilizando ST_ClosestPoint
    query = f"""
    WITH closest_line AS (
        SELECT id, ST_ClosestPoint(geom, ST_GeomFromText('{point_wkt}', 25830)) AS closest_point
        FROM eps.{path}
        ORDER BY ST_Distance(geom, ST_GeomFromText('{point_wkt}', 25830))
        LIMIT 1
    )
    SELECT ST_AsText(closest_point) AS geom_wkt
    FROM closest_line;
    """
    
    cur.execute(query)
    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        geom_wkt = row[0]
        closest_point = QgsGeometry.fromWkt(geom_wkt).asPoint()
        return closest_point
    else:
        return None

def get_coords_from_id(id, layer_name):
    conn, cur = db.connect_to_db()
    query = f"""
    SELECT ST_AsText(geom) AS geom_wkt
    FROM eps.{layer_name}_puntos
    WHERE id = {id};
    """
    cur.execute(query)
    row = cur.fetchone()
    geom = QgsGeometry.fromWkt(row[0])
    point = geom.asPoint()
    cur.close()
    conn.close()
    return point

def calculate_cost(routes):
    """
    Calcular el coste de una lista de rutas.

    :param routes: Lista de rutas (list of Route objects)
    :param coste_por_metro: Coste por metro recorrido (float)
    :return: Lista de rutas con el coste actualizado (list of Route objects)
    """

    for route in routes:
        total_cost = 0
        for subroute in route.subroutes:
            if subroute.net == 1:
                coste_por_metro = 3
            elif subroute.net == 2:
                coste_por_metro = 5
            elif subroute.net == 3:
                coste_por_metro = 10

            for i in range(len(subroute.path) - 1):
                punto_inicio = get_coords_from_id(subroute.path[i], subroute.net)
                punto_fin = get_coords_from_id(subroute.path[i + 1], subroute.net)
                punto_inicio_geom = point2path(punto_inicio, subroute.net)
                punto_fin_geom = point2path(punto_fin, subroute.net)
                distancia_euclidiana = punto_inicio_geom.distance(punto_fin_geom)
                total_cost += distancia_euclidiana * coste_por_metro
        route.g = total_cost
    return routes