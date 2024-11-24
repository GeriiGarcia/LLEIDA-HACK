

def update_f(routes):
    """
    Update the value of f of the expanded routes
    """
    for route in routes:
        route.update_f()
    return routes