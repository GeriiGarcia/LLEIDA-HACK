from qgis.core import QgsPointXY, QgsGeometry

class Route:
    """
    A class for keeping the route information from starting station to expanded station.
    Usage:
        # se inicializa la ruta con el nodo de origen
        # >>> path = Route(origin_node)
        # Se puede consultar el último y penúltimo punto QGIS de la última geometría
        # >>> path.last, path.penultimate
        # Se puede añadir una nueva geometría
        # >>> path.add_geom(geometry)
        # Se puede añadir un nuevo punto a la última geometría
        # >>> path.add_point(point)
    """

    def __init__(self, origin_node, origin_net):
        # Crear una geometría con el punto de origen
        self.geom = []
        first_trace = {'geometry': QgsGeomety.fromPointXY(origin_node.point), 'cost': 0, 'name': origin_net}
        self.geom.append(first_trace)

        self.head = self.geom[0].geometry.asPolyline()[0]
        self.last = self.geom[-1].geometry.asPolyline()[-1]
        if len(self.route) >= 2:
            self.penultimate = self.geom[-1].geometry.asPolyline()[-2]
        else:
            self.penultimate = None

    def update_h(self, h):
        self.h = h

    def update_g(self, g):
        self.geom[0].cost += g

    def update_f(self):
        self.f = self.g + self.h

    def add_geom(self, geom, name):
        # Adding a new geometry to the list
        self.geom.append({'geometry': geom, 'cost': 0, 'name': name})

    def add_point(self, point):
        # Adding a point to the last geometry in the list
        if self.geom:
            self.geom[0].geometry.addPointXY(point)
