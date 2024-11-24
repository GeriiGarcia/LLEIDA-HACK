def insert_cost_f(expand_routes, list_of_routes):
    """
    Insert the cost f of the expanded routes in the list of routes
    """
    lista = list_of_routes + expand_routes
    return sorted(lista, key=lambda route: route.f)