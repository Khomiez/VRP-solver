"""
Core routing functions for the VRP solver.
Includes route distance calculation and best route finding.
"""

from itertools import permutations
from utils import log
from models.data import distance_matrix, demands

def calculate_route_distance(path):
    """
    Calculate the total distance of a route visiting all nodes in the path,
    plus nodes G and H if not already in the path, then returning to Hub.
    
    This implementation properly considers all possible positions of G and H
    to ensure the globally optimal route is found.
    
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
    
    # If both G and H are not in the path yet, we need to try all possible insertions
    if not g_in_path and not h_in_path:
        # Try inserting G and H at all possible positions in the path
        best_distance = float('inf')
        best_full_path = None
        
        # Try G then H
        for i in range(1, len(original_path) + 1):
            for j in range(i, len(original_path) + 2):
                test_path = original_path.copy()
                test_path.insert(i, 5)  # Insert G
                test_path.insert(j, 6)  # Insert H
                
                # Ensure we return to the Hub
                if test_path[-1] != 0:
                    test_path.append(0)
                
                # Calculate distance
                test_distance = sum(distance_matrix[test_path[k]][test_path[k+1]] for k in range(len(test_path) - 1))
                
                if test_distance < best_distance:
                    best_distance = test_distance
                    best_full_path = test_path
        
        # Try H then G
        for i in range(1, len(original_path) + 1):
            for j in range(i, len(original_path) + 2):
                test_path = original_path.copy()
                test_path.insert(i, 6)  # Insert H
                test_path.insert(j, 5)  # Insert G
                
                # Ensure we return to the Hub
                if test_path[-1] != 0:
                    test_path.append(0)
                
                # Calculate distance
                test_distance = sum(distance_matrix[test_path[k]][test_path[k+1]] for k in range(len(test_path) - 1))
                
                if test_distance < best_distance:
                    best_distance = test_distance
                    best_full_path = test_path
        
        return best_distance, best_full_path
    
    # If only G is missing, try all positions to insert it
    elif not g_in_path:
        best_distance = float('inf')
        best_full_path = None
        
        for i in range(1, len(original_path) + 1):
            test_path = original_path.copy()
            test_path.insert(i, 5)  # Insert G
            
            # Ensure we return to the Hub
            if test_path[-1] != 0:
                test_path.append(0)
            
            # Calculate distance
            test_distance = sum(distance_matrix[test_path[k]][test_path[k+1]] for k in range(len(test_path) - 1))
            
            if test_distance < best_distance:
                best_distance = test_distance
                best_full_path = test_path
        
        return best_distance, best_full_path
    
    # If only H is missing, try all positions to insert it
    elif not h_in_path:
        best_distance = float('inf')
        best_full_path = None
        
        for i in range(1, len(original_path) + 1):
            test_path = original_path.copy()
            test_path.insert(i, 6)  # Insert H
            
            # Ensure we return to the Hub
            if test_path[-1] != 0:
                test_path.append(0)
            
            # Calculate distance
            test_distance = sum(distance_matrix[test_path[k]][test_path[k+1]] for k in range(len(test_path) - 1))
            
            if test_distance < best_distance:
                best_distance = test_distance
                best_full_path = test_path
        
        return best_distance, best_full_path
    
    # If both G and H are already in the path, just ensure we end at the Hub
    else:
        full_path = original_path.copy()
        if full_path[-1] != 0:
            full_path.append(0)
        
        total_distance = sum(distance_matrix[full_path[i]][full_path[i+1]] for i in range(len(full_path) - 1))
        return total_distance, full_path

def find_best_route(nodes):
    """
    Find the shortest route that visits all given nodes, starting at Hub,
    and ending with G and H (in the optimal order) before returning to Hub.
    
    This implementation tests all possible permutations and considers all 
    valid positions for G and H to ensure global optimality.
    
    Args:
        nodes: List of delivery nodes to visit (may include G=5 and H=6)
    
    Returns:
        tuple: (best_path, best_distance, final_path) - The optimal path, its distance, and the complete path
    """
    if not nodes:
        # If no nodes to visit, just go Hub -> G -> H -> Hub or Hub -> H -> G -> Hub
        path1 = [0, 5, 6, 0]
        dist1 = sum(distance_matrix[path1[i]][path1[i+1]] for i in range(len(path1) - 1))
        
        path2 = [0, 6, 5, 0]
        dist2 = sum(distance_matrix[path2[i]][path2[i+1]] for i in range(len(path2) - 1))
        
        if dist1 <= dist2:
            return [0], dist1, path1
        else:
            return [0], dist2, path2

    best_distance = float('inf')
    best_path = None
    best_final_path = None

    log(f"Finding best route for nodes {nodes}", 2)
    
    # For permutations, exclude G and H initially - we'll handle them specially
    permutation_nodes = [n for n in nodes if n not in [5, 6]]
    
    # Try all permutations of the regular delivery nodes
    for perm in permutations(permutation_nodes):
        path = [0] + list(perm)  # Start from Hub (0)
        
        # Calculate distance with optimal G/H placement
        distance, final_path = calculate_route_distance(path)
        
        log(f"  Route {path} optimized to {final_path}, distance = {distance}", 3)

        if distance < best_distance:
            best_distance = distance
            best_path = path
            best_final_path = final_path
    
    log(f"🗺️ Best path found: {best_path}, final path: {best_final_path}, distance = {best_distance}", 2)
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