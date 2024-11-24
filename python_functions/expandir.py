import copy
import psycopg2
from qgis.core import QgsPointXY, QgsProject, QgsGeometry, QgsVectorLayer, QgsFeature, QgsField, QgsSymbol
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from route import Route
from subroute import Subroute

from python_functions import db_connect as db

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

    new_routes = []

    cur.execute(query)
    rows = cur.fetchall()

    next_point = None
    prev_point = None
    if len(rows) > 0:
        next_point = rows[0][0]
        r = copy.deepcopy(ruta)
        r.subroutes[0].add_route(next_point)
        new_routes.append(r)
    if len(rows) > 1:
        prev_point = rows[1][0]
        r = copy.deepcopy(ruta)
        r.subroutes[0].add_route(prev_point)
        new_routes.append(r)

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
                id = row[0]
                new_subroute = Subroute(id, layer_name)
                r = copy.deepcopy(ruta)
                r.add_subroute(new_subroute)
                new_routes.append(r)

    # Cerrar la conexión a la base de datos
    cur.close()
    conn.close()

    return new_routes

