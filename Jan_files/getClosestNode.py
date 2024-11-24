def getClosestNode(node_o, net):
    closestNodes = {}
    
    # Iterem per cada posició de la xarxa i 
    for i in range(0, net.featureCount()):
        node = net.getFeature(i)

        print(node['id'])
        print(node['fid'])
        n_point = node.geometry().asPoint()
        print(n_point.x())
        print(n_point.y())
        print("--------------")
        
        # uptate dict of closest
    
    return "Hola"