from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant

# Obtener el proyecto actual
project = QgsProject.instance()

def calcular_coste(punto_inicio, punto_fin, red, coste_por_metro):
    """
    Calcular el coste entre dos puntos en una red.

    :param punto_inicio: Coordenadas del punto de inicio (QgsPointXY)
    :param punto_fin: Coordenadas del punto de fin (QgsPointXY)
    :param red: Capa de la red (QgsVectorLayer)
    :param coste_por_metro: Coste por metro recorrido (float)
    :return: Coste total calculado (float)

    :Example:
    >>> punto_inicio = QgsPointXY(279199.23649999964982271, 4110101.92349999956786633)
    >>> punto_fin = QgsPointXY(279513.26609999965876341, 4109468.53299999982118607)
    >>> red1 = project.mapLayersByName("red1")[0]
    >>> coste_por_metro = 3
    >>> calcular_coste(punto_inicio, punto_fin, red1, coste_por_metro)
    """
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


