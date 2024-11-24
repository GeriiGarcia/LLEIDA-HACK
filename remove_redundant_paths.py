from route import Route
#import python_functions.point2near_path_test as p2np
from subroute import Subroute





def remove_redundant_paths(expanded_route_list, route_list, visited_nodes_cost={}):
    """
    Aquesta funció elimina les rutes de la route list si apareix alguna alternativa 
    més barata.
    
    expanded_route_list → Llista de les noves rutes (amb els seus costos corresponents)
    route_list → La llista de rutes actuals, d'aquí eliminarèm les rutes cares
    visited_nodes_cost → diccionari d'assistència que ens ajuda a saber quan costa arribar a cada node
    """
    
    remaining_explanded_lists = []
    for route in expanded_route_list:
        # Aconseguim la clau de la ruta
        route_key = route.get_route_key()

        # Afegim la ruta a la llista i al diccionari si no hi és
        if route_key not in visited_nodes_cost.keys():
            visited_nodes_cost[route_key] = route.get_cost()
            remaining_explanded_lists.append(route)

        # Si la clau ja està a la llsita, peró hi ha una alternativa més barata la substituïm
        elif visited_nodes_cost[route_key] > route.get_cost():
            visited_nodes_cost[route_key] = route.get_cost()  
            remaining_explanded_lists.append(route)
            
            # Reemplacem l'antiga llista per la nova llista
            route_list = [r for r in route_list if r.get_route_key() != route_key]
            

        # En cas de que la ruta ja estigui al diccionari i que nova sigui més cara, no fem res
        else:
            continue

    return remaining_explanded_lists, route_list, visited_nodes_cost

            
        
        

    