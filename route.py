"""
Class route has a list of subroutes
"""

class Route:
    def __init__(self, subroute):
        if type(subroute) is list:
            self.subroutes = subroute
        else:
            self.subroutes = [subroute]

        self.head = self.subroutes[0].head
        self.last = self.subroutes[-1].last
        if len(self.subroutes) >= 2:
            self.penultimate = self.subroutes[-1].penultimate
        else:
            self.penultimate = []

        # Heuristic cost
        self.h = 0

        # Combination of the two
        self.f = 0

    def __eq__(self, other):
        if other is not None:
            return self.subroutes == other.subroutes
        
    def get_cost(self):
        return sum(subroute.g for subroute in self.subroutes)

    def update_h(self, h):
        self.h = h

    def update_f(self):
        self.f = self.get_cost() + self.h

    def add_subroute(self, children):
        # Adding a new station to the route list
        self.subroutes.append(children)

    def get_route_key(self):
        # Devuelve una clave única para la ruta basada en los nodos de la subruta
        return tuple(subroute.last for subroute in self.subroutes)

    def __repr__(self):
        subroutes_str = " -> ".join([str(subroute) for subroute in self.subroutes])
        return f"<Route head={self.head}, last={self.last}, penultimate={self.penultimate}, subroutes=[{subroutes_str}]>"