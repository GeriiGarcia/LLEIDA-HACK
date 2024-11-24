def remove_redundant_paths(add_cost, path_list, visited_stations_cost):
    """
    Elimina rutas redundantes comparando costos acumulados
    
    Args:
        add_cost: Lista de tuplas (ruta, costo_acumulado)
        path_list: Lista de rutas a expandir
        visited_stations_cost: Diccionario de estaciones visitadas con sus costos
    
    Returns:
        new_expand: Lista de rutas no redundantes
        path_list: Lista actualizada de rutas
        visited_stations_cost: Diccionario actualizado de costos
    """
    new_expand = []
    
    for route, cost in zip(path_list, add_cost):
        last_node = route.last
        
        # Si el nodo no ha sido visitado o tiene menor costo
        if last_node not in visited_stations_cost or cost < visited_stations_cost[last_node]:
            visited_stations_cost[last_node] = cost
            new_expand.append(route)
            
    return new_expand, path_list, visited_stations_cost