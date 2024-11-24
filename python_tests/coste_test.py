import unittest
from qgis.core import QgsPointXY, QgsProject
from coste import calcular_coste

coste_por_metro = 3  # Ejemplo de coste por metro

calcular_coste(1, 10, "red1", coste_por_metro)