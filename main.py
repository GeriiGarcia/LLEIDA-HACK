"""
Código principal algoritmo A-star

"""

from qgis.core import QgsPointXY, QgsProject, QgsGeometry, QgsFeature, QgsField, QgsVectorLayer, QgsWkbTypes

from route import Route
from python_functions import point2near_path_test as p2np
from subroute import Subroute

# from python_functions import expand
from python_functions import remove_cycles
# from python_functions import calculate_cost
from python_functions import remove_redundant_paths
from python_functions import calculate_heuristics
from python_functions import update_f
from python_functions import insert_cost_f


def main():
    
    # Calcular el nodo origen a partir de los inputs
    # origin_point = QgsPointXY() perteneciente a una red
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    inicio = layers.mapLayersByName('inicio')
    origin_point = inicio[0].getFeatures().next().geometry().asPoint()
    final = project.mapLayersByName('final')
    destination_point = final[0].getFeatures().next().geometry().asPoint()
    redes = ['red1', 'red2', 'red3']
    origin_net, origin_node = p2np.point2near_path(origin_point, redes)
    print(origin_net, origin_node)
    dest_net, destination_node = p2np.point2near_path(destination_point, redes)
    print(dest_net, destination_node)

    # path_list = [Route(Subroute(origin_node, origin_net))]
    # visited_stations_cost = {}
    # while path_list != []:
    #     if path_list[0].last != destination_node:

    #         # Sacar el primer punto de la primera geometría
    #         first = path_list.pop(0)

    #         # Expandir el primer punto
    #         # Lista de nodos próximos (2 o más)
    #         exp = expand(first)
    #         rem = remove_cycles(exp)

    #         add_cost = calculate_cost(rem)

    #         # new_expand = rutas expandidas que no son redundantes. No han sido visitadas antes y / o el coste acumulado es menor que el del diccionario
    #         # path_list = lista de rutas a ser expandidas
    #         # visited_stations_cost = diccionario de estaciones visitadas con sus costes acumulados
    #         new_expand, path_list, visited_stations_cost = remove_redundant_paths(add_cost, path_list, visited_stations_cost)

    #         # Calcular la heurística de las rutas expandidas
    #         heu = calculate_heuristics(new_expand, destination_node, dest_net)

    #         # Actualizar el valor de f de las rutas expandidas
    #         f = update_f(heu)

    #         # Insertar las rutas expandidas en la lista de rutas a ser expandidas
    #         path_list = insert_cost_f(f, path_list)
            
    #     else:
    #         return path_list[0]
    # return []


if __name__ == '__main__':
    main()