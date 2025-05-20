"""
Data module for the VRP solver.
Contains the problem data, including distance matrix, demands, and vehicle choices.
Designed for flexibility and scalability with additional nodes.
"""

# Full node mapping for clarity and future expansion
NODE_MAPPING = {
    0: 'Hub_DMK',
    1: 'A_central rama 9',
    2: 'B_the nine',
    3: 'C_seacon',
    4: 'D_mega bangna',
    5: 'E_BKK',
}

# Inverse mapping for name lookups
NAME_TO_NODE = {v: k for k, v in NODE_MAPPING.items()}

# Required end sequence - all routes must end with D -> E -> Hub or  E -> D -> Hub
REQUIRED_END_SEQUENCE = [4, 5, 0] 

# Distance matrix - Complete 6x6 matrix for 6 nodes
distance_matrix = [
    [0, 19.5, 26.3, 33.2, 40.3, 41.2],
    [19.5, 0, 7.1, 14.3, 22.9, 23.9],
    [26.3, 7.1, 0, 7.8, 16.4, 17.1],
    [33.2, 14.3, 7.8, 0, 8.6, 20.9],
    [40.3, 22.9, 16.4, 8.6, 0, 18.2],
    [41.2, 23.9, 17.1, 20.9, 18.2, 0]
]

# Delivery demands: index = node, value = (H, K)
demands = {
    1: (1, 0),  # A demands
    2: (1, 2),  # B demands
    3: (0, 2),  # C demands
}

# Get active delivery nodes (those with demands)
active_delivery_nodes = [node for node, demand in demands.items() if demand[0] > 0 or demand[1] > 0]

# Vehicle options - each can be used only once ("Name", fixed_cost, h_cap, k_cap, fuel_cost)
vehicle_choices = [
    ("V", 150, 2, 2, 1),
    ("W", 200, 3, 3, 1),
    ("X", 250, 4, 4, 1),
    ("Y", 350, 5, 5, 1),
    ("Z", 600, 6, 6, 1)
]


def node_to_name(node):
    """
    Convert node number to name using the NODE_MAPPING.
    
    Args:
        node (int): Node index
        
    Returns:
        str: Node name
    """
    return NODE_MAPPING.get(node, f"Node-{node}")

def name_to_node(name):
    """
    Convert node name to index using the NAME_TO_NODE mapping.
    
    Args:
        name (str): Node name
        
    Returns:
        int: Node index, or -1 if not found
    """
    return NAME_TO_NODE.get(name, -1)

def get_total_demand():
    """
    Calculate total demand across all nodes.
    
    Returns:
        tuple: (total_h, total_k) - Total demand for H and K
    """
    total_h = sum(demand[0] for demand in demands.values())
    total_k = sum(demand[1] for demand in demands.values())
    return total_h, total_k

def add_node_demand(node, h_demand, k_demand):
    """
    Add or update a node's demand.
    
    Args:
        node (int): Node index
        h_demand (int): Demand for H
        k_demand (int): Demand for K
    """
    demands[node] = (h_demand, k_demand)
    if node not in active_delivery_nodes and (h_demand > 0 or k_demand > 0):
        active_delivery_nodes.append(node)

def remove_node_demand(node):
    """
    Remove a node's demand.
    
    Args:
        node (int): Node index
        
    Returns:
        bool: True if node was removed, False if node not found
    """
    if node in demands:
        del demands[node]
        if node in active_delivery_nodes:
            active_delivery_nodes.remove(node)
        return True
    return False

def get_node_count():
    """
    Get the total number of nodes in the system.
    
    Returns:
        int: Total number of nodes
    """
    return len(distance_matrix)