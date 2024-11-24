from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant
import db_connect as db

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
    print(punto_inicio)
    punto_fin = get_coords_from_id(id_destino, nombre_red)
    print(punto_fin)
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
id_origen = 632
id_destino = 1043
nombre_red = "red1"
coste_por_metro = 3

# Probar la función calcular_coste
coste_total = calcular_coste(id_origen, id_destino, nombre_red, coste_por_metro)