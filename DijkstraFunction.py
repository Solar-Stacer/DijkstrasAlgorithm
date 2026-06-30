import heapq

def getPathToSourceNode(node):
    if node.path_to_source_node:
        previous_node = list(node.path_to_source_node.values())[0]
        while previous_node.path_to_source_node:
            temp_node = list(previous_node.path_to_source_node.values())[0]
            node.path_to_source_node.update({temp_node.name:temp_node})
            if temp_node.path_to_source_node:
                previous_node = list(temp_node.path_to_source_node.values())[0]
                if previous_node.name == "Source Node":
                    node.path_to_source_node.update({previous_node.name:previous_node})
            else:
                node.path_to_source_node.update({temp_node.name:temp_node})
                break

# Based on Pseudocode on Wikipedia
def dijkstra(nodes, print_node=False):
    distance = dict([(node_item.name, node_item) for node_item in nodes.values()])
    Node_list = [*nodes.values()]
    priority_queue = [(Node_list[0].value, Node_list[0])]

    while priority_queue:
        u_value, u = heapq.heappop(priority_queue)
        u_edges = u.connect_item_dict

        neighbor_nodes = {}
        neighbor_edges = {}

        for edge in u_edges.values():
            v = edge.returnNeighbor(u)
            neighbor_nodes.update({v.name:v})
            neighbor_edges.update({v.name:edge})

        for v in neighbor_nodes.values():
            alt = distance[u.name].value + neighbor_edges[v.name].value
            if alt < distance[v.name].value:
                distance[v.name].value = alt
                v.setValue(alt)
                v.path_to_source_node.clear()
                v.path_to_source_node.update({u.name: u})
                priority_queue.append((v.value, v))

    if print_node:
        print(nodes)

'''
if __name__ == "__main__":
    class Edge:
        count = 0
        active_edges = {}

        def __init__(self, start, end, value):
            self.start = start
            self.end = end
            self.name = "Edge " + str(Edge.count)
            self.value = value
            Edge.count += 1
            self.update(start, end)

        def returnNeighbor(self, neighbor):
            if neighbor is not self.start:
                return self.start
            else:
                return self.end

        def update(self, start, end):
            Edge.active_edges.update({self.name: self})
            start.connect_item_dict.update({self.name: self})
            end.connect_item_dict.update({self.name: self})


    class Node:
        active_nodes = {}
        index = 0

        def __init__(self, name, value=inf, edges=None):
            if edges is None:
                self.connect_item_dict = {}
            else:
                self.connect_item_dict = edges
            self.name = name
            self.value = value
            self.index = Node.index
            Node.index += 1
            Node.active_nodes.update({name: self})

        def setValue(self, value):
            self.value = value

        def __lt__(self, other):
            return self.index < other.index

        def __str__(self):
            return f"{self.value}"

        __repr__ = __str__
    A = Node("A", 0)
    B = Node("B")
    C = Node("C")
    D = Node("D")
    E = Node("E")
    F = Node("F")

    edge_1 = Edge(A, B, 2)
    edge_2 = Edge(A, D, 8)
    edge_3 = Edge(B, E, 6)
    edge_4 = Edge(B, D, 5)
    edge_5 = Edge(D, E, 3)
    edge_6 = Edge(D, F, 2)
    edge_7 = Edge(E, F, 1)
    edge_8 = Edge(E, C, 9)
    edge_9 = Edge(F, C, 3)

    dijkstra(Node.active_nodes, True)
'''


