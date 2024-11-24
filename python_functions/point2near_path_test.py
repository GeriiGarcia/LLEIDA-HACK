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
        SELECT id, ST_Distance(geom, ST_SetSRID(ST_MakePoint({point_transformed.x()}, {point_transformed.y()}), 25830)) AS distance
        FROM eps.{path}
        ORDER BY distance
        LIMIT 1;
    """
    cur.execute(query)
    nearest_line = cur.fetchone()
    nearest_line_id = nearest_line[0]

    query = f"""
        SELECT ST_AsText(ST_ClosestPoint(geom, ST_SetSRID(ST_MakePoint({point_transformed.x()}, {point_transformed.y()}), 25830)))
        FROM eps.{path}
        WHERE id = {nearest_line_id};
    """
    cur.execute(query)
    nearest_line_geom = cur.fetchone()[0]
    nearest_line_point = QgsGeometry.fromWkt(nearest_line_geom).asPoint()
    
    bd.close_db_connection(conn, cur)
    return nearest_line_point

def points2paths(point, paths):
    """
    Encuentra el punto más cercano en una de las líneas a partir de un punto dado y un array de rutas en la base de datos.

    :param point: Un objeto QgsPoint que representa el punto de entrada.
    :param paths: Un array de cadenas que representan los nombres de las tablas en la base de datos donde se encuentran las líneas.

    :return: Un objeto QgsPoint que representa el punto más cercano en las líneas y la distancia mínima.

    :Example:
    >>> point = algo.asPoint()
    >>> paths = ["nombre_de_la_tabla1", "nombre_de_la_tabla2"]
    >>> nearest_point, min_distance = points2paths(point, paths)
    """
    nearest_points = []
    dist = []
    crs1 = QgsCoordinateReferenceSystem("EPSG:4326")              # CRS de point1
    crs2 = QgsCoordinateReferenceSystem("EPSG:32630")             # CRS de point2
    crs_destino = QgsCoordinateReferenceSystem("EPSG:32630") 
    for path in paths:
        nearest_point = point2path(point, path)
        nearest_points.append(nearest_point)
        dist.append(calcular_distancia(point, crs1, nearest_point, crs2, crs_destino))
        
    min_distance = min(dist)
    nearest_point = nearest_points[dist.index(min_distance)]
    return nearest_point

def calcular_distancia(point1, crs1, point2, crs2, crs_destino):
    """
    Calcula la distancia entre dos puntos en coordenadas cartesianas,
    transformando sus coordenadas al mismo sistema de referencia espacial (CRS).

    :param point1: Un objeto QgsPointXY que representa el primer punto.
    :param crs1: Un objeto QgsCoordinateReferenceSystem que representa el CRS de point1.
    :param point2: Un objeto QgsPointXY que representa el segundo punto.
    :param crs2: Un objeto QgsCoordinateReferenceSystem que representa el CRS de point2.
    :param crs_destino: Un objeto QgsCoordinateReferenceSystem que representa el CRS de destino para el cálculo.

    :return: Un flotante que representa la distancia entre los dos puntos.
    """
    # Crear transformaciones de CRS
    transform1 = QgsCoordinateTransform(crs1, crs_destino, QgsProject.instance())
    transform2 = QgsCoordinateTransform(crs2, crs_destino, QgsProject.instance())
    
    # Transformar puntos al CRS de destino
    point1_transformed = transform1.transform(point1)
    point2_transformed = transform2.transform(point2)
    
    # Obtener coordenadas cartesianas transformadas
    x1, y1 = point1_transformed.x(), point1_transformed.y()
    x2, y2 = point2_transformed.x(), point2_transformed.y()
    
    # Calcular la distancia euclidiana
    distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    return distance

# Obtener el proyecto actual
project = QgsProject.instance()

# Obtener todas las capas del proyecto
layers = project.mapLayers().values()

# Obtener las capas de red
red1 = project.mapLayersByName("red1")[0]
red2 = project.mapLayersByName("red2")[0]
red3 = project.mapLayersByName("red3")[0]

# Obtener las capas de inicio y final
inicio = project.mapLayersByName("inicio")[0]
final = project.mapLayersByName("final")[0]

# obtener las capas de puntos de las redes
puntos_red1 = project.mapLayersByName("red1_puntos")[0]
puntos_red2 = project.mapLayersByName("red2_puntos")[0]
puntos_red3 = project.mapLayersByName("red3_puntos")[0]

# Obtener todos los puntos de inicio y final
inicio_features = inicio.getFeatures()
# inicio_features = list(inicio.getFeatures())
final_features = list(final.getFeatures())

# Crear una nueva capa para los puntos
puntos_layer = QgsVectorLayer("Point?crs=EPSG:25830", "puntos_inicio_final", "memory")
puntos_layer_data = puntos_layer.dataProvider()
puntos_layer_data.addAttributes([QgsField("name", QVariant.String)])
puntos_layer.updateFields()

# Transformar CRS
crs_src = QgsCoordinateReferenceSystem(4326)  # CRS del punto de inicio
crs_dest = QgsCoordinateReferenceSystem(25830)  # CRS de la capa red1
transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())

# Procesar todos los puntos de inicio
for inicio_feature in inicio_features:
    inicio_geom = inicio_feature.geometry()
    inicio_point = inicio_geom.asPoint()
    inicio_point_transformed = transform.transform(inicio_point)

    # Añadir el punto de inicio a la capa
    new_inicio_feature = QgsFeature()
    new_inicio_feature.setGeometry(QgsGeometry.fromPointXY(inicio_point_transformed))
    new_inicio_feature.setAttributes(["inicio"])
    puntos_layer_data.addFeature(new_inicio_feature)

    # Encontrar el punto de la línea más cercana
    nearest_line_point = points2paths(inicio_point, ["red3", "red2", "red1"])

    # Añadir el punto de la línea más cercana a la capa
    nearest_line_feature = QgsFeature()
    nearest_line_feature.setGeometry(QgsGeometry.fromPointXY(nearest_line_point))
    nearest_line_feature.setAttributes(["linea_mas_cercana"])
    puntos_layer_data.addFeature(nearest_line_feature)

# Procesar todos los puntos de final
for final_feature in final_features:
    final_geom = final_feature.geometry()
    final_point = final_geom.asPoint()
    final_point_transformed = transform.transform(final_point)

    # Añadir el punto de final a la capa
    new_final_feature = QgsFeature()
    new_final_feature.setGeometry(QgsGeometry.fromPointXY(final_point_transformed))
    new_final_feature.setAttributes(["final"])
    puntos_layer_data.addFeature(new_final_feature)

    # Encontrar el punto de la línea más cercana
    nearest_line_point = points2paths(final_point, ["red3", "red2", "red1"])

    # Añadir el punto de la línea más cercana a la capa
    nearest_line_feature = QgsFeature()
    nearest_line_feature.setGeometry(QgsGeometry.fromPointXY(nearest_line_point))
    nearest_line_feature.setAttributes(["linea_mas_cercana"])
    puntos_layer_data.addFeature(nearest_line_feature)

# Añadir la capa al proyecto
QgsProject.instance().addMapLayer(puntos_layer)