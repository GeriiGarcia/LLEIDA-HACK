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
            self.route = node
        else:
            self.route = [node]

        self.net = net

        self.head = self.route[0]
        self.last = self.route[-1]
        if len(self.route) >= 2:
            self.penultimate = self.route[-2]
        # Real cost
        self.g = 0
    

    def __eq__(self, other):
        if other is not None:
            return self.route == other.route

    def update_g(self, g):
        self.g += g

    def add_route(self, children):
        # Adding a new station to the route list
        self.route.append(children)
        self.penultimate = self.route[-2]
        self.last = self.route[-1]


    def __repr__(self):
        return f"<Subroute {self.name} {self.path} {self.method}>"