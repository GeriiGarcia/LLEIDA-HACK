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

        # Heuristic cost
        self.h = 0

        # Combination of the two
        self.f = 0

    def __eq__(self, other):
        if other is not None:
            return self.subroute == other.subroute
        
    def get_cost(self):
        return sum(self.subroutes.g)

    def update_h(self, h):
        self.h = h

    def update_f(self):
        self.f = sum(self.subroutes.g) + self.h

    def add_subroute(self, children):
        # Adding a new station to the route list
        self.subroute.append(children)
    def get_route_key(self):
        return str(self.head) + str(self.subroutes[0].net) 
    def __repr__(self):
        return f"<Route {self.name} {self.path} {self.method}>"