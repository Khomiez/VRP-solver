"""
Data module for the VRP solver.
Contains the problem data, including distance matrix, demands, and vehicle choices.
"""

# Distance matrix - Simplified to 5 nodes plus Hub (0), G (5), and H (6)
# Index 0 = Hub, 5 = G, 6 = H
distance_matrix = [
    [0, 80, 10, 15, 10, 35, 30, 10, 55],
    [80, 0, 70, 60, 50, 40, 35, 70, 50],
    [10, 70, 0, 20, 10, 40, 40, 40, 50],
    [15, 60, 20, 0, 20, 30, 20, 5, 60],
    [10, 50, 10, 20, 0, 20, 5, 20, 50],
    [35, 40, 40, 30, 20, 0, 10, 10, 70],
    [30, 35, 40, 20, 5, 10, 0, 25, 60],
    [10, 70, 40, 5, 20, 10, 25, 0, 65],
    [55, 50, 50, 60, 50, 70, 60, 65, 0]
]

# Delivery demands: index = node, value = (H, K)
demands = {
    1: (1, 0),
    2: (0, 2),
    3: (1, 2),
    4: (1, 0),
    5: (0, 2),
    6: (0, 2)
}

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
    Convert node number to name (Hub, A-D, G, H).
    
    Args:
        node (int): Node index
        
    Returns:
        str: Node name
    """
    node_names = ['Hub', 'A', 'B', 'C', 'D', 'G', 'H']
    if node < len(node_names):
        return node_names[node]
    return f"Node-{node}"  # Fallback for any additional nodes