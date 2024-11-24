
import copy

def remove_cycles(routes):
    """
     It removes from path_list the set of paths that include some cycles in their path.
     Format of the parameter is:
        Args:
            path_list (LIST of Path Class): Expanded paths
        Returns:
            path_list (list): Expanded paths without cycles.
    """
    no_cycle = []
    if len(routes) > 0:
        for route in routes:
            # mirar si hay ciclos en el ultimo subroute
            subroute = copy.deepcopy(route.subroute[0].path) # lista de id
            new_subroute = set(subroute)
            if (len(subroute) == len(new_subroute)):
                no_cycle.append(route)
    return no_cycle