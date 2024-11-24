"""
Atr:
    route: list of nodes
    net: network
    head: first node
    last: last node
    penultimate: penultimate node
    g: real cost
    h: heuristic cost
    f: combination of the two
"""

class Subroute:
    def __init__(self, node, net):
        if type(node) is list:
            self.path = node
        else:
            self.path = [node]

        self.net = net

        self.head = self.path[0]
        self.last = self.path[-1]
        if len(self.path) >= 2:
            self.penultimate = self.path[-2]
        else:
            self.penultimate = []
        # Real cost
        self.g = 0
    

    def __eq__(self, other):
        if other is not None:
            return self.path == other.path

    def update_g(self, g):
        self.g += g

    def add_route(self, children):
        # Adding a new station to the route list
        self.path.append(children)
        self.penultimate = self.path[-2]
        self.last = self.path[-1]
        self.head = self.last


    def __repr__(self):
        return f"<Subroute {self.path}>"