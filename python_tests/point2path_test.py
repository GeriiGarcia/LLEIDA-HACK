from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField, QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from PyQt5.QtCore import QVariant
import point2path as p2p

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

# Obtener el primer punto de inicio
inicio_features = inicio.getFeatures()
next(inicio_features)
next(inicio_features)
next(inicio_features)
inicio_feature = next(inicio_features)
inicio_geom = inicio_feature.geometry()
inicio_point = inicio_geom.asPoint()

# Transformar el punto de inicio al SRID de la capa red1
crs_src = QgsCoordinateReferenceSystem(4326)  # CRS del punto de inicio
crs_dest = QgsCoordinateReferenceSystem(25830)  # CRS de la capa red1
transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())
inicio_point_transformed = transform.transform(inicio_point)

# coordenadas punto inicial
print("punto inicial")
print(inicio_point_transformed.x(), inicio_point_transformed.y())

nearest_line_point = p2p.point2path(inicio_point, "red1")
print("punto linea mas cercana")
print(nearest_line_point.x(), nearest_line_point.y())

# Crear una nueva capa para los puntos
puntos_layer = QgsVectorLayer("Point?crs=EPSG:25830", "puntos_inicio_red1", "memory")
puntos_layer_data = puntos_layer.dataProvider()
puntos_layer_data.addAttributes([QgsField("name", QVariant.String)])
puntos_layer.updateFields()

# Añadir el punto de inicio a la capa
inicio_feature = QgsFeature()
inicio_feature.setGeometry(QgsGeometry.fromPointXY(inicio_point_transformed))
inicio_feature.setAttributes(["inicio"])
puntos_layer_data.addFeature(inicio_feature)

# Añadir el punto de la línea más cercana a la capa
nearest_line_feature = QgsFeature()
nearest_line_feature.setGeometry(QgsGeometry.fromPointXY(nearest_line_point))
nearest_line_feature.setAttributes(["linea_mas_cercana"])
puntos_layer_data.addFeature(nearest_line_feature)

# Añadir la capa al proyecto
QgsProject.instance().addMapLayer(puntos_layer)