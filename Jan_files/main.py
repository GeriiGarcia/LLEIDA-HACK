from qgis.core import QgsProject, QgsFeatureRequest, QgsMapLayer, QgsWkbTypes, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsField
from PyQt5.QtCore import QVariant 
import psycopg2
import math
# Obtain the current project
project = QgsProject.instance()

def getDistance(n1_x, n1_y, n2_x, n2_y):
    return math.sqrt((n2_x - n1_x)**2 + (n2_y - n1_y)**2)
    
def getClosestNodes(node_o, net, num_of_elements):

    # List of nodes closest to node_o
    closest_nodes = []
    for n in node_o.getFeatures():
        no_x = n.geometry().asPoint().x()
        no_y = n.geometry().asPoint().y()
    
    print(no_x, no_y)
    # Iterate over each feature (node) in the network
    i = 0
    for node in net.getFeatures():
        # Get node attributes and geometry
        node_id = node['id']  # Adjust field name as necessary
        node_x = node.geometry().asPoint().x()
        node_y = node.geometry().asPoint().y()

        # Calculate the distance to the origin node (node_o)
        distance = getDistance(n1_x=no_x, n1_y=no_y, n2_x=node_x, n2_y=node_y)
        
        # Add node info to the list
        node_info = {
            "id": node_id,
            "distance": distance
        }

        # Add the node to the closest_nodes list
        closest_nodes.append(node_info)

        if i == num_of_elements+10:
            # Sort the list by distance (ascending order)
            closest_nodes.sort(key=lambda x: x['distance'])
            
            # Select only the top 'num_of_elements' nodes
            closest_nodes = closest_nodes[:num_of_elements]
            
            # reset i to 0
            i = 0

    # We sort one final time and then return the top num_of_elements
    closest_nodes.sort(key=lambda x: x['distance'])    
    return closest_nodes[:num_of_elements]



# Obtain all layers
layers = project.instance().mapLayers()
#
# init = inicio_27bf15cb_684b_4da6_af21_8686475e9962
# final = final_699c07be_02dc_476c_a55b_51038c3991bb
# red1 = red1_cd470ab1_7314_4948_b243_bd637457aa7e
# red2 = 
# red3 =
# red1_puntos =  red1_puntos_6445ab67_d15d_4340_af3c_f80dd1fe6ef5
# red2_puntos = 
# red3_puntos = 

#
red1 = layers['red1_puntos_6445ab67_d15d_4340_af3c_f80dd1fe6ef5']
init = layers['inicio_27bf15cb_684b_4da6_af21_8686475e9962']

# A feature is an element of a layer
red1_fc = red1.featureCount()
    
print(getClosestNodes(node_o=init, net=red1, num_of_elements=10))





