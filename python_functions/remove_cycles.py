

def remove_cycles(path_list):
    """
     It removes from path_list the set of paths that include some cycles in their path.
     Format of the parameter is:
        Args:
            path_list (LIST of Path Class): Expanded paths
        Returns:
            path_list (list): Expanded paths without cycles.
    """
    no_cycle = []
    if len(path_list) > 0:
        for path in path_list:
            route = copy.deepcopy(path.route)
            new_route = set(route)
            if (len(route) == len(new_route)):
                no_cycle.append(path)
    return no_cycle