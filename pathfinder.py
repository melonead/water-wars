import math
offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


class Node:

    def __init__(self, node_id):
        self.cost = float("inf")
        self.id = node_id
        self.type = 'normal'
        self.parent = None
        self.neighbors = None
        self.processed = False
        node_id = self.id.split(':')
        x = int(node_id[0])
        y = int(node_id[1])
        self.pos = [x * tile_size, y * tile_size]

    def get_neighbors(self, graph):
        global offsets
        node_id = self.id.split(':')
        x = int(node_id[0])
        y = int(node_id[1])
        temp_list = []
        for offset in offsets:
            try:
                node = graph[str(x + offset[0]) + ':' + str(y + offset[1])]
            except KeyError:
                continue
            if node.type != 'obstacle':
                temp_list.append(node)
        self.neighbors = temp_list
        n = []
        for neighbor, offset in zip(self.neighbors, offsets):
            if offset[1] == 0 or offset[0] == 0:
                n.append([neighbor, 1 * tile_size])
            else:
                n.append([neighbor, math.sqrt(2) * tile_size])
        self.neighbors = n
        return self.neighbors

    def set_cost(self, cost):
        self.cost = cost

    def set_parent(self, parent):
        self.parent = parent

tile_size = 20
#graph = {str(int(x/tile_size)) + ':' + str(int(y/tile_size)) : Node(str(int(x/tile_size)) + ':' + str(int(y/tile_size))) for y in range(0, SCREEN_SIZE[1], tile_size) for x in range(0, SCREEN_SIZE[1], tile_size)}
graph = {}
search = False


start_node_key = None
end_node_key = None
open_nodes = []
path_nodes = []

open_nodes = list(graph.values())

def heuristic_function(node, end_node):
    start_post = node.pos
    end_pos = end_node.pos
    width = end_node.pos[0] - node.pos[0]
    height = end_node.pos[1] - node.pos[1]
    return math.sqrt(width ** 2 + height ** 2)

def least_cost_node(open_nodes, graph, goal_node_key):
    least_cost = float("inf")
    least_cost_node = None
    for node in open_nodes:
        node.estimated_total_cost = node.cost + heuristic_function(node, graph[goal_node_key])
        if node.estimated_total_cost < least_cost and not node.processed:
            least_cost_node = node
            least_cost = node.estimated_total_cost
    return least_cost_node
            
def shortest_path(graph, start_node_key, goal_node_key, open_nodes, path_nodes):
    current_node = graph[start_node_key]
    neighbors = current_node.get_neighbors(graph)
    while open_nodes:
        for neighbor in neighbors:
            if neighbor[0].type != 'start':
                if current_node.type == 'start':
                    neighbor[0].cost = neighbor[1]
                    neighbor[0].parent = current_node
                cost = current_node.cost + neighbor[1]
                if neighbor[0].processed:
                    if cost > neighbor[0].cost:
                        continue
                    elif cost < neighbor[0].cost:
                        neighbor[0].processed = False
                        open_nodes.append(neighbor[0])
                if cost < neighbor[0].cost:
                    neighbor[0].cost = cost
                    neighbor[0].parent = current_node
        if current_node.type == 'goal':
            break
        open_nodes.remove(current_node)
        current_node.processed = True
        current_node = least_cost_node(open_nodes, graph, goal_node_key)
        
        if open_nodes:
            neighbors = current_node.get_neighbors(graph)

    node = graph[goal_node_key]
    while node.parent != None:
        path_nodes.append(node)
        node = node.parent
        path_nodes = list(reversed(path_nodes))
    
    return path_nodes
