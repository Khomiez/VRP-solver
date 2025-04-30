"""
Recursive optimization algorithm for the VRP solver.
"""

from itertools import combinations
from utils import log, timer
from models.data import demands, vehicle_choices
from models.solution import VRPSolution
# Import routing functions with original names
from algorithms.routing import find_best_route, is_valid_assignment

def find_optimal_solution(nodes_to_assign, available_vehicles, used_vehicles=None, current_solution=None, best_solution=None, depth=0):
    """
    Improved recursive function to find the optimal assignment of vehicles to nodes.
    The improvements include:
    1. More conservative pruning to avoid missing optimal solutions
    2. Exhaustive exploration of node assignments
    3. Better estimation of lower bounds on costs
    4. Removal of early termination conditions that might exclude optimal solutions
    
    Args:
        nodes_to_assign: Set of delivery nodes not yet assigned
        available_vehicles: List of vehicles that can be used
        used_vehicles: Set of vehicles already used
        current_solution: Current solution being considered
        best_solution: Best solution found so far
        depth: Recursion depth for logging
    
    Returns:
        dict: Best solution found (dictionary with trip details and costs)
    """
    indent = "  " * depth
    log(f"\n{indent}🔍 EXPLORING SOLUTION (depth {depth})", 1)
    log(f"{indent}Nodes to assign: {nodes_to_assign}", 1)
    
    if used_vehicles is None:
        used_vehicles = set()
    if current_solution is None:
        current_solution = []
    if best_solution is None:
        best_solution = {
            "trips": [], 
            "cost": float('inf'), 
            "fixed_cost": 0,
            "fuel_cost": 0,
            "vehicles_used": float('inf'), 
            "total_distance": float('inf'), 
            "completed": False
        }

    # Base case: all nodes assigned (solution found)
    if not nodes_to_assign:
        # Calculate total fixed cost and total fuel cost separately
        total_fixed_cost = sum(trip[1] for trip in current_solution)
        total_fuel_cost = sum(trip[4] * trip[5] for trip in current_solution)  # distance * fuel_cost_per_unit
        total_cost = total_fixed_cost + total_fuel_cost
        
        vehicles_used = len(current_solution)
        total_distance = sum(trip[4] for trip in current_solution)
        
        log(f"{indent}✅ COMPLETE SOLUTION FOUND:", 1)
        log(f"{indent}  Fixed Cost: {total_fixed_cost}, Fuel Cost: {total_fuel_cost}", 1)
        log(f"{indent}  Total Cost: {total_cost}, Vehicles: {vehicles_used}, Distance: {total_distance}", 1)
        
        # Evaluate if this is better than our best solution so far
        # First priority: minimize total cost (fixed + fuel)
        # Second priority: minimize number of vehicles
        # Third priority: minimize total distance
        better_solution = False
        
        if not best_solution["completed"]:
            better_solution = True
            log(f"{indent}  First complete solution found!", 1)
        elif total_cost < best_solution["cost"]:
            better_solution = True
            log(f"{indent}  Better cost: {total_cost} < {best_solution['cost']}", 1)
        elif total_cost == best_solution["cost"] and vehicles_used < best_solution["vehicles_used"]:
            better_solution = True
            log(f"{indent}  Same cost but fewer vehicles: {vehicles_used} < {best_solution['vehicles_used']}", 1)
        elif (total_cost == best_solution["cost"] and
              vehicles_used == best_solution["vehicles_used"] and
              total_distance < best_solution["total_distance"]):
            better_solution = True
            log(f"{indent}  Same cost and vehicles but shorter distance: {total_distance} < {best_solution['total_distance']}", 1)

        if better_solution:
            best_solution = {
                "trips": current_solution.copy(),
                "cost": total_cost,
                "fixed_cost": total_fixed_cost,
                "fuel_cost": total_fuel_cost,
                "vehicles_used": vehicles_used,
                "total_distance": total_distance,
                "completed": True
            }
            log(f"{indent}🌟 NEW BEST SOLUTION FOUND!", 1)
            
        return best_solution

    # Early pruning logic - more conservative to avoid missing optimal solutions
    if best_solution["completed"]:
        # Calculate current costs so far
        current_fixed_cost = sum(trip[1] for trip in current_solution) 
        current_fuel_cost = sum(trip[4] * trip[5] for trip in current_solution)
        current_cost = current_fixed_cost + current_fuel_cost
        
        # Calculate minimum additional cost (both fixed and potential minimum fuel)
        min_additional_fixed_cost = min((v[1] for v in available_vehicles if v[0] not in used_vehicles), default=float('inf'))
        
        # A more conservative lower bound on additional fuel cost
        # Use minimum distance between any two nodes as the minimum distance estimate
        min_dist_between_nodes = 5  # Conservative estimate based on distance matrix
        
        # For unassigned nodes, we need at least one more vehicle and distance
        min_additional_fuel_cost = 0
        if nodes_to_assign:
            # At minimum, need to visit unassigned nodes and return to hub
            min_additional_fuel_cost = min_dist_between_nodes * len(nodes_to_assign)
        
        # More conservative pruning - only prune if we're far over the best cost
        if current_cost + min_additional_fixed_cost > best_solution["cost"] * 1.1:  # 10% buffer
            log(f"{indent}⏱️ Pruning: Current cost + min additional cost significantly exceeds best solution", 1)
            return best_solution

    # Sort vehicles by efficiency (highest capacity-to-cost ratio first)
    # This helps explore more promising vehicle choices earlier
    sorted_vehicles = sorted(
        [v for v in available_vehicles if v[0] not in used_vehicles],
        key=lambda v: (v[2] + v[3]) / (v[1] + 10 * v[4]),  # Less aggressive cost estimate
        reverse=True
    )
    
    log(f"{indent}Available vehicles (sorted by efficiency): {[v[0] for v in sorted_vehicles]}", 1)

    for name, fixed_cost, h_cap, k_cap, fuel_cost in sorted_vehicles:
        log(f"{indent}🚗 Trying vehicle {name} (Fixed Cost:{fixed_cost}, Fuel Cost/dist:{fuel_cost}, H:{h_cap}, K:{k_cap})", 1)
        
        # Try all possible combinations of nodes for this vehicle
        remaining_nodes = list(nodes_to_assign)
        log(f"{indent}  Trying node combinations for vehicle {name}...", 1)
        
        # For each possible subset size 
        # We'll try all subset sizes instead of just limiting to 4
        for subset_size in range(min(len(remaining_nodes), len(remaining_nodes)), 0, -1):
            log(f"{indent}  Looking at subsets of size {subset_size}", 2)
            
            # Try all possible combinations of delivery nodes
            for nodes_subset in combinations(remaining_nodes, subset_size):
                log(f"{indent}  Testing nodes {nodes_subset}", 2)
                
                # Skip if this subset exceeds vehicle capacity
                if not is_valid_assignment(nodes_subset, h_cap, k_cap):
                    continue

                # Find best route for this subset
                path, distance, final_path = find_best_route(nodes_subset)

                # Add this trip to current solution
                # Store: (name, fixed_cost, nodes_subset, path, distance, fuel_cost_per_unit, final_path)
                log(f"{indent}  ➕ Adding trip with vehicle {name} to solution", 2)
                current_solution.append((name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path))
                used_vehicles.add(name)

                # Recursively solve for remaining nodes
                remaining_nodes_set = set(nodes_to_assign) - set(nodes_subset)
                best_solution = find_optimal_solution(
                    remaining_nodes_set,
                    available_vehicles,
                    used_vehicles,
                    current_solution,
                    best_solution,
                    depth + 1
                )
                
                # Backtrack - remove this trip from solution to try alternatives
                log(f"{indent}  ⏪ Backtracking: removing trip with vehicle {name}", 2)
                current_solution.pop()
                used_vehicles.remove(name)
                
    return best_solution

def solve_vehicle_routing(restricted_vehicles=None):
    """
    Main function to solve the vehicle routing problem.
    
    Args:
        restricted_vehicles: If specified, only these vehicles will be used
        
    Returns:
        tuple: (formatted_trips, total_cost, fixed_cost, fuel_cost, total_vehicles, total_distance, completed)
    """
    log("\n🚀 STARTING VEHICLE ROUTING SOLVER", 0)
    
    nodes_to_assign = set(demands.keys())
    log(f"Nodes to deliver to: {nodes_to_assign}", 1)
    
    # Create list of available vehicles (potentially restricted)
    if restricted_vehicles:
        available_vehicles = [v for v in vehicle_choices if v[0] in restricted_vehicles]
        log(f"Using restricted vehicle set: {[v[0] for v in available_vehicles]}", 1)
    else:
        available_vehicles = vehicle_choices
        log(f"Using all available vehicles: {[v[0] for v in available_vehicles]}", 1)

    # Find the optimal solution
    log("\n📊 FINDING OPTIMAL SOLUTION...", 0)
    with timer("Recursive algorithm optimization time"):
        solution = find_optimal_solution(nodes_to_assign, available_vehicles)

    if not solution["completed"]:
        log("\n❌ NO SOLUTION FOUND! Cannot assign all deliveries with available vehicles.", 0)
        return [], 0, 0, 0, 0, 0, False

    # Format the results
    formatted_trips = []
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost_per_unit, final_path in solution["trips"]:
        trip_fuel_cost = distance * fuel_cost_per_unit
        trip_deliveries = [(node, f"H={demands[node][0]}", f"K={demands[node][1]}") for node in nodes_subset if node in demands]
        formatted_trips.append((name, fixed_cost, trip_fuel_cost, trip_deliveries, path, distance, final_path))

    return (
        formatted_trips,
        solution["cost"],
        solution["fixed_cost"],
        solution["fuel_cost"],
        solution["vehicles_used"],
        solution["total_distance"],
        True
    )