"""
Functions for validating VRP solutions.
"""

from models.data import demands, vehicle_choices
from algorithms.routing import calculate_route_distance

def verify_solution(solution):
    """
    Verifies that a solution is valid and correct.
    Returns True if valid, False with reason if invalid.
    
    Args:
        solution (dict): Solution dictionary
        
    Returns:
        tuple: (valid, validation_errors) - Boolean indicating if solution is valid and list of errors
    """
    print("\n=======================================")
    print("🔍 SOLUTION VALIDATION")
    print("=======================================")
    
    valid = True
    validation_errors = []
    
    # Get all nodes from the solution
    all_assigned_nodes = set()
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        all_assigned_nodes.update(nodes_subset)
    
    # 1. Check all nodes are visited
    required_nodes = set(demands.keys())
    missing_nodes = required_nodes - all_assigned_nodes
    extra_nodes = all_assigned_nodes - required_nodes - {5, 6}  # Exclude G and H from extras
    
    if missing_nodes:
        valid = False
        validation_errors.append(f"Missing nodes: {missing_nodes}")
    
    if extra_nodes:
        valid = False
        validation_errors.append(f"Extra nodes: {extra_nodes}")
    
    # 2. Check no node is visited more than once
    nodes_count = {}
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        for node in nodes_subset:
            if node in demands:  # Only count delivery nodes
                nodes_count[node] = nodes_count.get(node, 0) + 1
    
    duplicate_nodes = [node for node, count in nodes_count.items() if count > 1]
    if duplicate_nodes:
        valid = False
        validation_errors.append(f"Duplicate nodes: {duplicate_nodes}")
    
    # 3. Check vehicle capacities
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        # Find vehicle specs
        v_specs = next((v for v in vehicle_choices if v[0] == name), None)
        if not v_specs:
            valid = False
            validation_errors.append(f"Unknown vehicle: {name}")
            continue
            
        h_cap, k_cap = v_specs[2], v_specs[3]
        total_h = sum(demands[n][0] for n in nodes_subset if n in demands)
        total_k = sum(demands[n][1] for n in nodes_subset if n in demands)
        
        if total_h > h_cap:
            valid = False
            validation_errors.append(f"Vehicle {name}: H capacity exceeded ({total_h} > {h_cap})")
        
        if total_k > k_cap:
            valid = False
            validation_errors.append(f"Vehicle {name}: K capacity exceeded ({total_k} > {k_cap})")
    
    # 4. Check no vehicle is used more than once
    used_vehicles = [trip[0] for trip in solution["trips"]]
    vehicle_counts = {}
    for v in used_vehicles:
        vehicle_counts[v] = vehicle_counts.get(v, 0) + 1
    
    duplicate_vehicles = [v for v, count in vehicle_counts.items() if count > 1]
    if duplicate_vehicles:
        valid = False
        validation_errors.append(f"Duplicate vehicles: {duplicate_vehicles}")
    
    # 5. Check routes start at Hub and verify path calculation
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        if path[0] != 0:
            valid = False
            validation_errors.append(f"Route for vehicle {name} doesn't start at Hub")
        
        # Verify distance calculation
        recalculated_distance, _ = calculate_route_distance(path)
        if abs(recalculated_distance - distance) > 0.001:
            valid = False
            validation_errors.append(f"Distance calculation error for vehicle {name}: " +
                               f"reported {distance}, calculated {recalculated_distance}")
    
    # 6. Verify cost calculations
    calculated_fixed_cost = sum(trip[1] for trip in solution["trips"])
    calculated_fuel_cost = sum(trip[4] * trip[5] for trip in solution["trips"])
    calculated_total_cost = calculated_fixed_cost + calculated_fuel_cost
    
    if abs(calculated_fixed_cost - solution["fixed_cost"]) > 0.001:
        valid = False
        validation_errors.append(f"Fixed cost calculation error: " +
                           f"reported {solution['fixed_cost']}, calculated {calculated_fixed_cost}")
    
    if abs(calculated_fuel_cost - solution["fuel_cost"]) > 0.001:
        valid = False
        validation_errors.append(f"Fuel cost calculation error: " +
                           f"reported {solution['fuel_cost']}, calculated {calculated_fuel_cost}")
    
    if abs(calculated_total_cost - solution["cost"]) > 0.001:
        valid = False
        validation_errors.append(f"Total cost calculation error: " +
                           f"reported {solution['cost']}, calculated {calculated_total_cost}")
    
    # Display validation results
    if valid:
        print("✅ Solution is VALID - All checks passed")
    else:
        print("❌ Solution is INVALID - Errors found:")
        for error in validation_errors:
            print(f"  - {error}")
    
    return valid, validation_errors