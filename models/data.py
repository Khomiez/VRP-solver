"""
Data module for the VRP solver.
Contains the problem data, including distance matrix, demands, and vehicle choices.
Designed for flexibility and scalability with additional nodes.
"""

# Full node mapping for clarity and future expansion
NODE_MAPPING = {
    0: 'Hub',
    1: 'A',
    2: 'B',
    3: 'C',
    4: 'D',
    5: 'G',  # Notice we're preserving the original indices for G and H
    6: 'H',
    7: 'E',  # Adding E as node 7
    8: 'F'   # Adding F as node 8
}

# Inverse mapping for name lookups
NAME_TO_NODE = {v: k for k, v in NODE_MAPPING.items()}

# Distance matrix - Complete 9x9 matrix for 9 nodes
# Index 0 = Hub, 1-4 = A-D, 5 = G, 6 = H, 7 = E, 8 = F
distance_matrix = [
    [0, 80, 10, 15, 10, 35, 30, 10, 55],  # Hub to all
    [80, 0, 70, 60, 50, 40, 35, 70, 50],  # A to all
    [10, 70, 0, 20, 10, 40, 40, 40, 50],  # B to all
    [15, 60, 20, 0, 20, 30, 20, 5, 60],   # C to all
    [10, 50, 10, 20, 0, 20, 5, 20, 50],   # D to all
    [35, 40, 40, 30, 20, 0, 10, 10, 70],  # G to all
    [30, 35, 40, 20, 5, 10, 0, 25, 60],   # H to all
    [10, 70, 40, 5, 20, 10, 25, 0, 65],   # E to all
    [55, 50, 50, 60, 50, 70, 60, 65, 0]   # F to all
]

# Delivery demands: index = node, value = (H, K)
# Current demands just for nodes A-D, G-H (indices 1-4, 5-6)
demands = {
    1: (1, 0),  # A demands
    2: (0, 2),  # B demands
    3: (1, 2),  # C demands
    4: (1, 0),  # D demands
    5: (0, 2),  # G demands
    6: (0, 2),  # H demands
    # E and F currently have no demands, but could be added later
    # 7: (0, 0),  # E demands (placeholder)
    # 8: (0, 0)   # F demands (placeholder)
}

# Get active delivery nodes (those with demands)
active_delivery_nodes = list(demands.keys())

# Vehicle options - each can be used only once ("Name", fixed_cost, h_cap, k_cap, fuel_cost)
vehicle_choices = [
    ("V", 150, 2, 2, 1),
    ("W", 200, 3, 3, 1),
    ("X", 250, 4, 4, 1),
    ("Y", 350, 5, 5, 1),
    ("Z", 600, 6, 6, 1)
]

# Required end sequence - all routes must end with G -> H -> Hub
REQUIRED_END_SEQUENCE = [5, 6, 0]  # G (5) -> H (6) -> Hub (0)

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
    if node not in active_delivery_nodes:
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