from python_functions import db_connect as db
import psycopg2
from qgis.core import QgsPointXY, QgsProject, QgsGeometry, QgsVectorLayer, QgsFeature, QgsField, QgsSymbol
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from route import Route
from subroute import Subroute

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

# expandir(qgspointxy: POINT)
# return: lista de rutas expandidas
# input: redx_punto

# qgspointxy: POINT
def expandir(ruta):
    conn, cur = db.connect_to_db()

    id_point = ruta.head
    qgspointxy = get_coords_from_id(id_point, ruta.subroutes[0].net)

    # Convertir QgsPointXY a WKT
    point_wkt = f"POINT({qgspointxy.x()} {qgspointxy.y()})"
    print(point_wkt)

    # Encontrar el siguiente y anterior punto más cercano en la misma capa
    query = f"""
    WITH nearest_points AS (
        SELECT id, geom, ST_Distance(geom, ST_GeomFromText('{point_wkt}', 25830)) AS distance
        FROM eps.{ruta.subroutes[0].net}_puntos
        ORDER BY distance
    )
    SELECT id, ST_AsText(ST_StartPoint(geom)) AS start_geom_wkt, ST_AsText(ST_EndPoint(geom)) AS end_geom_wkt
    FROM nearest_points
    WHERE NOT ST_Equals(geom, ST_GeomFromText('{point_wkt}', 25830))
    ORDER BY distance
    LIMIT 2;
    """
    
    cur.execute(query)
    rows = cur.fetchall()

    next_point = None
    prev_point = None
    if len(rows) > 0:
        next_point = QgsGeometry.fromWkt(rows[0][1]).asPoint()
    if len(rows) > 1:
        prev_point = QgsGeometry.fromWkt(rows[1][1]).asPoint()

    # Buscar puntos en otras capas dentro de un radio de 250 metros
    layers = ["red1_puntos", "red2_puntos", "red3_puntos"]
    other_points = []
    for layer in layers:
        if layer != ruta.subroutes[0].net + "_puntos":
            layer_name = layer
            query = f"""
            SELECT id, ST_AsText(geom) AS geom_wkt
            FROM eps.{layer_name}
            WHERE ST_DWithin(geom, ST_GeomFromText('{point_wkt}', 25830), 250);
            """
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                geom = QgsGeometry.fromWkt(row[1])
                if geom.isMultipart():
                    points = geom.asMultiPoint()
                else:
                    points = [geom.asPoint()]
                for point in points:
                    other_points.append((row[0], layer_name, point))

    # Cerrar la conexión a la base de datos
    cur.close()
    conn.close()

    # Crear nuevas rutas basadas en next_point y prev_point
    new_routes = []
    if next_point:
        new_subroute = Subroute(next_point, ruta.subroutes[0].net)
        print(new_subroute)
        new_route = Route(ruta.subroutes + [new_subroute])
        new_routes.append(new_route)

    if prev_point:
        new_subroute = Subroute(prev_point, ruta.subroutes[0].net)
        new_route = Route(ruta.subroutes + [new_subroute])
        new_routes.append(new_route)

    if other_points:
        for point in other_points:
            new_subroute = Subroute(point, layer_name)
            new_route = ruta.add_subroute(new_subroute)
            new_routes.append(new_route)

    return new_routes

# Ejemplo de uso
start_point = QgsPointXY(453113.747931, 4212144.949761)
subroute = Subroute(23160, "red3")
ruta = Route([subroute])

result = expandir(ruta)
for route in result:
    print(route)