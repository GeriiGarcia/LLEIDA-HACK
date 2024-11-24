
from python_functions.expandir import get_coords_from_id

def calculate_heuristics(new_expand, destination_node, dest_net):
    """
    Calculate the heuristic of the expanded routes
    """
    coord_final = get_coords_from_id(destination_node, dest_net)

    for route in new_expand:
        coord_inicio = get_coords_from_id(route.head, route.subroutes[0].net)
        
        # Calculate the distance between the two points
        h = coord_inicio.distance(coord_final)
        route.update_h(h)
    return new_expand