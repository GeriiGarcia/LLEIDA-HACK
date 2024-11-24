from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField, QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from PyQt5.QtCore import QVariant
import db_connect as bd

def point2path(point, path):
    """
    Encuentra el punto más cercano en una línea a partir de un punto dado y una ruta en la base de datos.

    :param point: Un objeto QgsPoint que representa el punto de entrada.
    :param path: Una cadena que representa el nombre de la tabla en la base de datos donde se encuentran las líneas.

    :return: Un objeto QgsPoint que representa el punto más cercano en la línea.

    :Example:
    >>> point = algo.asPoint()
    >>> path = "nombre_de_la_tabla"
    >>> nearest_point = point2path(point, path)
    """
    conn, cur = bd.connect_to_db()
    crs_src = QgsCoordinateReferenceSystem(4326)
    crs_dest = QgsCoordinateReferenceSystem(25830)
    transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
    point_transformed = transform.transform(point)

    query = f"""
        SELECT id, ST_Distance(geom, ST_SetSRID(ST_MakePoint({point.x()}, {point.y()}), 25830)) AS distance
        FROM eps.{path}
        ORDER BY distance
        LIMIT 1;
    """
    cur.execute(query)
    nearest_line = cur.fetchone()
    nearest_line_id = nearest_line[0]

    query = f"""
        SELECT ST_AsText(ST_ClosestPoint(geom, ST_SetSRID(ST_MakePoint({point.x()}, {point.y()}), 25830)))
        FROM eps.{path}
        WHERE id = {nearest_line_id};
    """
    cur.execute(query)
    nearest_line_geom = cur.fetchone()[0]
    nearest_line_point = QgsGeometry.fromWkt(nearest_line_geom).asPoint()
    
    bd.close_db_connection(conn, cur)
    return nearest_line_point


