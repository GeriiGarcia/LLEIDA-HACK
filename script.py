








from qgis.core import QgsProject, QgsApplication

# Inicializa QGIS
QgsApplication.setPrefixPath("/usr", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Carga el proyecto
project = QgsProject.instance()
project.read('Project.qgz')



# Obtén la capa por su nombre
layer = project.mapLayersByName('red1_puntos')[0]

# Itera sobre las características de la capa y haz un print de los datos
for feature in layer.getFeatures():
    print(feature.attributes())








