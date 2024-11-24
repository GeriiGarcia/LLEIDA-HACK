import copy

def remove_cycles(routes):
    """
    Elimina de la lista de rutas aquellas que contienen ciclos en su camino.
    Args:
        routes (LIST of Route Class): Rutas expandidas
    Returns:
        no_cycle (list): Rutas expandidas sin ciclos.
    """
    no_cycle = []
    if len(routes) > 0:
        for route in routes:
            # Mirar si hay ciclos en el último subroute
            print("adios")
            subroute = copy.deepcopy(route.subroutes[0].path)  # lista de id
            new_subroute = set(subroute)
            if len(subroute) == len(new_subroute):
                no_cycle.append(route)
                
    return no_cycle