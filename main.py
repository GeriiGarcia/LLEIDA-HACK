"""
Código principal algoritmo A-star

"""

from qgis.core import QgsPointXY, QgsProject, QgsGeometry, QgsFeature, QgsField, QgsVectorLayer, QgsWkbTypes

from route import Route
import python_functions.point2near_path_test as p2np
from subroute import Subroute

from python_functions.expandir import expandir
from python_functions.remove_cycles import remove_cycles
from python_functions.coste2 import calculate_cost
from python_functions.remove_redundant_paths import remove_redundant_paths
from python_functions.calculate_heuristics import calculate_heuristics
from python_functions.update_f import update_f
from python_functions.insert_cost_f import insert_cost_f
from python_functions.create_layer_from_route import create_layer_from_route



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

    routes = [Route(Subroute(origin_node, origin_net))]
    visited_stations_cost = {}
    while routes != []:
        if routes[0].last != destination_node:

            # Sacar el primer punto de la primera geometría
            first = routes.pop(0)

            # Expandir el primer punto
            # Lista de nodos próximos (2 o más)
            exp = expandir(first)
            rem = remove_cycles(exp)

            add_cost = calculate_cost(rem)

            # new_expand = rutas expandidas que no son redundantes. No han sido visitadas antes y / o el coste acumulado es menor que el del diccionario
            # path_list = lista de rutas a ser expandidas
            # visited_stations_cost = diccionario de estaciones visitadas con sus costes acumulados
            new_expand, routes, visited_stations_cost = remove_redundant_paths(add_cost, routes, visited_stations_cost)

            # Calcular la heurística de las rutas expandidas
            heu = calculate_heuristics(new_expand, destination_node, dest_net)

            # Actualizar el valor de f de las rutas expandidas
            f = update_f(heu)

            # Insertar las rutas expandidas en la lista de rutas a ser expandidas
            routes = insert_cost_f(f, routes)
            
        else:
            # routes[0] tiene el camino más corto
            # Crear una geometria con la ruta routes[0]
            # Crear una capa con la geometría
            create_layer_from_route(routes[0])
    return []


if __name__ == '__main__':
    main()