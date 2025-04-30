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
    then visiting the closest of G or H from the last node, then the other one,
    then returning to Hub.
    
    Implements the rule: "Every path should end with node G or H by choosing 
    the closest one from the last visited node first, then go back to Hub."
    
    Args:
        path: List of nodes to visit, starting with Hub (0)
        
    Returns:
        tuple: (total_distance, full_path) - The total distance and complete path
    """
    # Start with the given path
    original_path = list(path)
    
    # Check if G and H are already in the path
    g_in_path = 5 in original_path
    h_in_path = 6 in original_path
    
    # If both G and H are already in the path, make sure we end at Hub
    if g_in_path and h_in_path:
        # Need to ensure path ends with returning to Hub
        full_path = original_path.copy()
        if full_path[-1] != 0:
            full_path.append(0)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                             for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If both G and H are missing, append them based on which is closer to the last node
    if not g_in_path and not h_in_path:
        full_path = original_path.copy()
        last_node = full_path[-1]
        
        # Determine if G or H is closer to the last node
        dist_to_g = distance_matrix[last_node][5]
        dist_to_h = distance_matrix[last_node][6]
        
        if dist_to_g <= dist_to_h:  # G is closer or equal
            # Add G first, then H
            full_path.append(5)  # G
            full_path.append(6)  # H
        else:  # H is closer
            # Add H first, then G
            full_path.append(6)  # H
            full_path.append(5)  # G
            
        # Return to hub
        full_path.append(0)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If only G is missing, add it after the end and return to Hub
    elif not g_in_path:
        full_path = original_path.copy()
        full_path.append(5)  # Add G
        full_path.append(0)  # Return to Hub
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path
    
    # If only H is missing, add it after the end and return to Hub
    elif not h_in_path:
        full_path = original_path.copy()
        full_path.append(6)  # Add H
        full_path.append(0)  # Return to Hub
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] 
                            for i in range(len(full_path) - 1))
        return total_distance, full_path

def find_best_route(nodes):
    """
    Find the shortest route that visits all given nodes, starting at Hub,
    and ending by visiting the closest of G or H from the last node, then
    the other one, then returning to Hub.
    
    Args:
        nodes: List of delivery nodes to visit (may include G=5 and H=6)
    
    Returns:
        tuple: (best_path, best_distance, final_path) - The optimal path, its distance, 
               and the complete path with G/H and return to Hub
    """
    if not nodes:
        # If no nodes to visit, just see if G or H is closer to Hub
        if distance_matrix[0][5] <= distance_matrix[0][6]:
            path = [0, 5, 6, 0]  # Hub -> G -> H -> Hub
        else:
            path = [0, 6, 5, 0]  # Hub -> H -> G -> Hub
        
        dist = sum(distance_matrix[path[i]][path[i+1]] for i in range(len(path) - 1))
        return [0], dist, path

    best_distance = float('inf')
    best_path = None
    best_final_path = None

    log(f"Finding best route for nodes {nodes}", 2)
    
    # For permutations, exclude G and H initially if present
    permutation_nodes = [n for n in nodes if n not in [5, 6]]
    
    # Try all permutations of the delivery nodes
    for perm in permutations(permutation_nodes):
        path = [0] + list(perm)  # Start from Hub (0)
        
        # Handle G and H if they're in the original nodes list
        if 5 in nodes:
            path.append(5)
        if 6 in nodes:
            path.append(6)
        
        # Calculate distance with new rule for G/H
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