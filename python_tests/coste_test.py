import unittest
from qgis.core import QgsPointXY, QgsProject
from coste import calcular_coste

# Obtener el proyecto actual
project = QgsProject.instance()

# Ejemplo de uso de la función
punto_inicio = QgsPointXY(279199.23649999964982271, 4110101.92349999956786633)
punto_fin = QgsPointXY(279513.26609999965876341, 4109468.53299999982118607)
red1 = project.mapLayersByName("red1")[0]
coste_por_metro = 3  # Ejemplo de coste por metro

calcular_coste(punto_inicio, punto_fin, red1, coste_por_metro)