from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant
import db_connect as db

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
    crs_src = QgsCoordinateReferenceSystem(25830)
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




# Obtener el proyecto actual
project = QgsProject.instance()

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
    
    point = point2path(point, layer_name)
    point = point2path(point, layer_name)
    return point

def calcular_coste(id_origen, id_destino, nombre_red, coste_por_metro):
    """
    Calcular el coste entre dos puntos en una red.

    :param id_origen: ID del punto de inicio (int)
    :param id_destino: ID del punto de fin (int)
    :param nombre_red: Nombre de la capa de la red (str)
    :param coste_por_metro: Coste por metro recorrido (float)
    :return: Coste total calculado (float)

    :Example:
    >>> id_origen = 1
    >>> id_destino = 2
    >>> nombre_red = "red1"
    >>> coste_por_metro = 3
    >>> calcular_coste(id_origen, id_destino, nombre_red, coste_por_metro)
    """
    punto_inicio = get_coords_from_id(id_origen, nombre_red)
    print(f"Punto de inicio: {punto_inicio}")
    punto_fin = get_coords_from_id(id_destino, nombre_red)
    print(f"Punto de fin: {punto_fin}")
    red = project.mapLayersByName(nombre_red)[0]

    # Verificar que la capa tenga geometría de línea
    if red.geometryType() != QgsWkbTypes.LineGeometry:
        raise TypeError("La capa red no tiene geometría de líneas.")

    # Crear una capa temporal para el tramo resaltado
    crs_red = QgsCoordinateReferenceSystem("EPSG:25830")
    highlight_layer = QgsVectorLayer("LineString?crs=EPSG:25830", "Tramo seleccionado", "memory")
    highlight_layer_provider = highlight_layer.dataProvider()

    # Agregar un campo para la distancia
    highlight_layer_provider.addAttributes([QgsField("Distancia_m", QVariant.Double)])
    highlight_layer.updateFields()

    # Inicializar distancia total y geometría resaltada
    distancia_total = 0
    highlight_geom = None

    # Seleccionar el primer tramo (trozo)
    features = red.getFeatures()

    for feature in features:
        # Obtener la geometría de la línea
        geom = feature.geometry()

        if geom and geom.isMultipart():
            # Si la geometría es multipart, combinar las partes
            for part in geom.asMultiPolyline():
                linea = QgsGeometry.fromPolylineXY(part)
                if linea.intersects(QgsGeometry.fromPointXY(punto_inicio)) and linea.intersects(QgsGeometry.fromPointXY(punto_fin)):
                    distancia_total += linea.length()
                    highlight_geom = linea if highlight_geom is None else highlight_geom.combine(linea)
        elif geom:
            # Si la geometría es simple, usarla directamente
            if geom.intersects(QgsGeometry.fromPointXY(punto_inicio)) and geom.intersects(QgsGeometry.fromPointXY(punto_fin)):
                distancia_total += geom.length()
                highlight_geom = geom if highlight_geom is None else highlight_geom.combine(geom)
        
        # Romper después de un tramo (opcional)
        break

    # Crear una nueva feature para la capa temporal
    if highlight_geom:
        new_feature = QgsFeature()
        new_feature.setGeometry(highlight_geom)
        new_feature.setAttributes([distancia_total])
        highlight_layer_provider.addFeature(new_feature)

    # Agregar la capa al proyecto
    project.addMapLayer(highlight_layer)

    # Calcular el coste total
    coste_total = distancia_total * coste_por_metro

    # Mostrar la distancia total recorrida y el coste
    print(f"La distancia recorrida entre los puntos es: {distancia_total:.2f} metros")
    print(f"El coste total es: {coste_total:.2f}")
    return coste_total

# Configurar el entorno de prueba
project = QgsProject.instance()
id_origen = 1025
id_destino = 1415
nombre_red = "red1"
coste_por_metro = 3

# imprimir las coordenadas de los puntos de origen y destino
punto_inicio = get_coords_from_id(id_origen, nombre_red)
print(f"Punto de inicio: {punto_inicio}")
punto_inicio_geom = point2path(punto_inicio, nombre_red)
print("punto geometria: ", point2path(punto_inicio, nombre_red))
# mira si el punto de geometria esta en la red
red = project.mapLayersByName(nombre_red)[0]
features = red.getFeatures()
for feature in features:
    geom = feature.geometry()
    if geom.contains(punto_inicio_geom):
        print("El punto de inicio está en la red.")
        break
punto_fin = get_coords_from_id(id_destino, nombre_red)
print(f"Punto de fin: {punto_fin}")
print("punto geometria: ", point2path(punto_fin, nombre_red))

# Probar la función calcular_coste
coste_total = calcular_coste(id_origen, id_destino, nombre_red, coste_por_metro)