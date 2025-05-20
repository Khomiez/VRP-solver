"""
Core routing functions for the VRP solver.
Includes route distance calculation and best route finding with the new rule.
"""

from itertools import permutations
from utils import log
from models.data import distance_matrix, demands

def calculate_route_distance(path):
    """
    Calculate the total distance of a route visiting all nodes in the path,
    then visiting the closest of nodes 7 or 8 from the last node, then the other one,
    then returning to Hub.
    """
    from models.data import REQUIRED_END_SEQUENCE
    
    # Get required nodes from the constant instead of hard-coding
    required_node1 = REQUIRED_END_SEQUENCE[0]  # 7 (E_BKK)
    required_node2 = REQUIRED_END_SEQUENCE[1]  # 8 (F_New_Location)
    hub = REQUIRED_END_SEQUENCE[2]             # 0 (Hub)
    
    # Start with the given path
    original_path = list(path)
    
    # Check if required nodes are already in the path
    node1_in_path = required_node1 in original_path
    node2_in_path = required_node2 in original_path
    
    # If both required nodes are already in the path, make sure we end at Hub
    if node1_in_path and node2_in_path:
        # Need to ensure path ends with returning to Hub
        full_path = original_path.copy()
        if full_path[-1] != hub:
            full_path.append(hub)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                             for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If both required nodes are missing, append them based on which is closer to the last node
    if not node1_in_path and not node2_in_path:
        full_path = original_path.copy()
        last_node = full_path[-1]
        
        # Determine which required node is closer to the last node
        dist_to_node1 = distance_matrix[last_node][required_node1]
        dist_to_node2 = distance_matrix[last_node][required_node2]
        
        if dist_to_node1 <= dist_to_node2:  # Node1 is closer or equal
            # Add Node1 first, then Node2
            full_path.append(required_node1)
            full_path.append(required_node2)
        else:  # Node2 is closer
            # Add Node2 first, then Node1
            full_path.append(required_node2)
            full_path.append(required_node1)
            
        # Return to hub
        full_path.append(hub)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If only one required node is missing, add it after the end and return to Hub
    elif not node1_in_path:
        full_path = original_path.copy()
        full_path.append(required_node1)
        full_path.append(hub)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If only the other required node is missing, add it after the end and return to Hub
    elif not node2_in_path:
        full_path = original_path.copy()
        full_path.append(required_node2)
        full_path.append(hub)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path

def find_best_route(nodes):
    """
    Find the shortest route that visits all given nodes, starting at Hub,
    and ending by visiting the closest required node, then the other one, 
    then returning to Hub.
    """
    from models.data import REQUIRED_END_SEQUENCE
    
    # Get required nodes from the constant
    required_node1 = REQUIRED_END_SEQUENCE[0]
    required_node2 = REQUIRED_END_SEQUENCE[1]
    hub = REQUIRED_END_SEQUENCE[2]
    
    if not nodes:
        # If no nodes to visit, just see which required node is closer to Hub
        if distance_matrix[hub][required_node1] <= distance_matrix[hub][required_node2]:
            path = [hub, required_node1, required_node2, hub]
        else:
            path = [hub, required_node2, required_node1, hub]
        
        dist = sum(distance_matrix[path[i]][path[i+1]] for i in range(len(path) - 1))
        return [hub], dist, path

    # Rest of the function...
    
    # For permutations, exclude required nodes initially if present
    permutation_nodes = [n for n in nodes if n not in [required_node1, required_node2]]
    
    # Try all permutations of the delivery nodes
    for perm in permutations(permutation_nodes):
        path = [hub] + list(perm)  # Start from Hub
        
        # Handle required nodes if they're in the original nodes list
        if required_node1 in nodes:
            path.append(required_node1)
        if required_node2 in nodes:
            path.append(required_node2)
        
        # Calculate distance with new rule for required nodes
        distance, final_path = calculate_route_distance(path)
        
        log(f"  Route {path} with rule applied: {final_path}, distance = {distance}", 3)

        if distance < best_distance:
            best_distance = distance
            best_path = path
            best_final_path = final_path
    
    log(f"🗺️ Best path with rule: {best_path}, final path: {best_final_path}, distance = {best_distance}", 2)
    return best_path, best_distance, best_final_path

def is_valid_assignment(nodes, h_cap, k_cap):
    """
    Check if a set of nodes can be serviced by a vehicle with given capacities.
    
    Args:
        nodes: List of nodes to check
        h_cap: H capacity of the vehicle
        k_cap: K capacity of the vehicle
        
    Returns:
        bool: True if the assignment is valid, False otherwise
    """
    total_h = sum(demands[n][0] for n in nodes if n in demands)  # Only include regular delivery nodes
    total_k = sum(demands[n][1] for n in nodes if n in demands)
    is_valid = total_h <= h_cap and total_k <= k_cap
    
    if not is_valid:
        log(f"❌ Nodes {nodes} invalid: H={total_h}, K={total_k} exceeds capacity H={h_cap}, K={k_cap}", 2)
    else:
        log(f"✅ Nodes {nodes} valid: H={total_h}, K={total_k} within capacity H={h_cap}, K={k_cap}", 2)
        
    return is_valid