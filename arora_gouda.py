import json
import threading
import time

nodes = {}
k = 0
isRunning = False
states = []

def clear():
    global nodes
    global k
    global isRunning
    global states
    nodes = {}
    k = 0
    isRunning = False
    states = []
    return generate_js_graph()

class Node:
    def __init__(self, node_id, root_id, distance, parent_id=None):
        self.node_id = node_id
        self.root_id = root_id
        self.distance = distance
        self.parent_id = parent_id

    def __str__(self):
        return str(self.node_id)

    def __repr__(self):
        return str(self.node_id)

def get_node_from_node_dict(node_dict):
    try:
        nodeId = int(node_dict['id'])
        rootId = int(node_dict['root'])
        distance = int(node_dict['distance'])
        parent = int(node_dict['parent'])
        return Node(nodeId, rootId, distance, parent)
    except:
        return None

def get_node_by_id(nodeId):
    for node in nodes:
        if node.node_id == nodeId:
            return node
    return None

def add_node(node_dict):
    global k
    global nodes
    node = get_node_from_node_dict(node_dict)
    if (node and not get_node_by_id(node.node_id)):
        nodes[node] = []
        k += 1
        return generate_js_graph()
    else:
        return None

def remove_node(nodeId):
    global nodes
    global k
    node = get_node_by_id(nodeId['id'])
    if node:
        del nodes[node]
        for nod in nodes:
            if node in nodes[nod]:
                nodes[nod].remove(node)
        k -= 1
        return generate_js_graph()
    else:
        return None

def exist_edge(fromNode, toNode):
    return toNode in nodes[fromNode] or fromNode in nodes[toNode]

def add_edge(edge_dict):
    fromNode = get_node_by_id(int(edge_dict['from']))
    toNode = get_node_by_id(int(edge_dict['to']))

    if (fromNode and toNode and not exist_edge(fromNode, toNode)):
        nodes[fromNode].append(toNode)
        nodes[toNode].append(fromNode)
        return generate_js_graph()
    else:
        return None

def remove_edge(edge_dict):
    fromNode = get_node_by_id(edge_dict['from'])
    toNode = get_node_by_id(edge_dict['to'])

    if (fromNode and toNode and exist_edge(fromNode, toNode)):
        nodes[fromNode].remove(toNode)
        nodes[toNode].remove(fromNode)
        return generate_js_graph()
    else:
        return None

def generate_js_graph():
    nodes_js = []
    edges_js = []
    for node in nodes:
        nodes_js.append({'id': node.node_id, 'label': get_label_from_node(node)})

    inserted = []
    for node in nodes:
        for edge in nodes[node]:
            ab = (node.node_id, edge.node_id)
            ba = (edge.node_id, node.node_id)
            if ab not in inserted and ba not in inserted:
                edges_js.append({'from': node.node_id, 'to': edge.node_id})
                a = (node.node_id, edge.node_id)
                inserted.append(a)

    js = {'nodes': nodes_js, 'edges': edges_js}
    return js

def get_label_from_node(node):
    node_id = 'id=%s' % node.node_id
    root = 'root=%s' % node.root_id
    distance = 'distance=%s' % node.distance
    parent = 'parent=%s' % node.parent_id
    return '%s\n%s\n%s\n%s' % (node_id, root, distance, parent)

def check_inconsistency(node):
    global states
    global nodes

    hasInconsistency = False

    a = node.root_id < node.node_id
    b = (node.parent_id == None) and ((node.root_id != node.node_id) or (node.distance != 0))
    c = (node.parent_id != None) and not exist_edge(node, get_node_by_id(node.parent_id))
    d = (node.distance >= k)

    if a or b or c or d:
        node.parent_id = None
        node.root_id = node.node_id
        node.distance = 0
        hasInconsistency = True
        states.append(generate_js_graph())

    for neighbor in nodes[node]:
        if neighbor.distance < k and neighbor.node_id == node.root_id:
            if neighbor.root_id != node.root_id or neighbor.distance != node.distance - 1:
                node.root_id = neighbor.root_id
                node.distance = neighbor.distance + 1
                hasInconsistency = True                    
                states.append(generate_js_graph())
        elif neighbor.distance < k and neighbor.node_id != node.root_id:
            if node.root_id < neighbor.root_id:
                node.parent_id = neighbor.node_id
                node.root_id = neighbor.root_id
                node.distance = neighbor.distance + 1
                hasInconsistency = True
                states.append(generate_js_graph())

    return hasInconsistency

def worker(node):
    while (isRunning):
        check_inconsistency(node)

def run():
    global isRunning
    global states

    states = []
    for node in nodes:
        isRunning = True
        t = threading.Thread(target=worker, args=(node,))
        t.start()

    time.sleep(10)
    isRunning = False
    time.sleep(1)

    return {'states': states}