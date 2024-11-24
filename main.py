"""
Código principal algoritmo A-star
"""

from qgis.core import QgsPointXY, QgsProject, QgsGeometry, QgsFeature, QgsField, QgsVectorLayer, QgsWkbTypes

from route import Route
from subroute import Subroute

from python_functions.expandir import expandir as expand
from python_functions.remove_cycles import remove_cycles
from python_functions.coste2 import calculate_cost as calculate_cost

from python_functions.calculate_heuristics import calculate_heuristics
from python_functions.update_f import update_f
from python_functions.insert_cost_f import insert_cost_f

from remove_redundant_paths import remove_redundant_paths

pesos = [3,5,10]

def main():
    print("Inicio de la función main")
    
    # Calcular el nodo origen a partir de los inputs
    # origin_point = QgsPointXY() perteneciente a una red
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    print("Capas cargadas:", layers)
    
    inicio = project.mapLayersByName('inicio')
    final = project.mapLayersByName('final')
    #print("Capas inicio y final:", inicio, final)

    # origin_point = inicio[0].getFeatures().next().geometry().asPoint()
    # destination_point = final[0].getFeatures().next().geometry().asPoint()
    redes = ['red1', 'red2', 'red3']

    # origin_net, origin_node = p2np.point2near_path(origin_point, redes)
    # print(origin_net, origin_node)
    # dest_net, destination_node = p2np.point2near_path(destination_point, redes)
    # print(dest_net, destination_node)

    origin_net = 'red3'
    origin_node = 353
    dest_net = 'red3'
    destination_node = 771  

    path_list = [Route(Subroute(origin_node, origin_net))]
    visited_stations_cost = {}
    
    while path_list != []:
        print("hola en el bucle while")
        
        if path_list[0].last != destination_node:
            print("Expandiendo el primer punto")
            # Sacar el primer punto de la primera geometría
            first = path_list.pop(0)

            # Expandir el primer punto
            # Lista de nodos próximos (2 o más)
            exp = expand(first)
            rem = remove_cycles(exp)

            add_cost = calculate_cost(rem)

            # new_expand = rutas expandidas que no son redundantes. No han sido visitadas antes y / o el coste acumulado es menor que el del diccionario
            # path_list = lista de rutas a ser expandidas
            # visited_stations_cost = diccionario de estaciones visitadas con sus costes acumulados
            new_expand, path_list, visited_stations_cost = remove_redundant_paths(add_cost, path_list, visited_stations_cost)

            # Calcular la heurística de las rutas expandidas
            heu = calculate_heuristics(new_expand, destination_node, dest_net)

            # Actualizar el valor de f de las rutas expandidas
            f = update_f(heu)

            # Insertar las rutas expandidas en la lista de rutas a ser expandidas
            path_list = insert_cost_f(f, path_list)
            
        else:
            print("Ruta encontrada")
            return path_list[0]
    print("No se encontró ninguna ruta")
    return []

main()