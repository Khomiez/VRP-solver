"""
Functions for displaying VRP solutions.
"""

from models.data import node_to_name
from algorithms import solve_vehicle_routing

def display_solution():
    """Find and display the optimal solution with correct path handling."""
    print("\n=======================================")
    print("🔍 FINDING OPTIMAL ROUTING SOLUTION...")
    print("=======================================")
    
    trips_result, total_cost, fixed_cost, fuel_cost, total_vehicles, total_distance, completed = solve_vehicle_routing()

    if not completed:
        print("\n❌ NO SOLUTION FOUND! Cannot assign all deliveries with available vehicles.")
        return

    print("\n=======================================")
    print("🌟 OPTIMAL SOLUTION FOUND")
    print("=======================================")
    
    for i, (veh, veh_fixed_cost, veh_fuel_cost, deliveries, path, distance, final_path) in enumerate(trips_result, 1):
        print(f"\n🚚 Trip #{i} using Vehicle {veh}")
        
        # Display deliveries for this route
        named_deliveries = []
        for node, h, k in deliveries:
            named_deliveries.append(f"{node_to_name(node)} ({h}, {k})")
        print(f"  Deliveries: {', '.join(named_deliveries)}")
        
        # Display the correct final path with node names
        named_path = [node_to_name(node) for node in final_path]
        print(f"  Route     : {' → '.join(named_path)}")
        print(f"  Distance  : {distance}")
        print(f"  Fixed Cost: {veh_fixed_cost}")
        print(f"  Fuel Cost : {veh_fuel_cost}")
        print(f"  Total Cost: {veh_fixed_cost + veh_fuel_cost}")

    print("\n=======================================")
    print(f"💰 Total Fixed Cost: {fixed_cost}")
    print(f"⛽ Total Fuel Cost : {fuel_cost}")
    print(f"💵 Total Cost      : {total_cost}")
    print(f"🚚 Total Vehicles  : {total_vehicles}")
    print(f"📏 Total Distance  : {total_distance}")
    print("✅ All deliveries completed")
    print("=======================================")

def compare_solutions(recursive_solution, ortools_solution):
    """
    Compare recursive solution with OR-Tools solution.
    
    Args:
        recursive_solution: Solution from recursive algorithm
        ortools_solution: Solution from OR-Tools (total_cost, solution_routes)
    """
    if recursive_solution is None or ortools_solution is None:
        print("Cannot compare solutions: one or both solutions are missing.")
        return
    
    ortools_cost, ortools_routes = ortools_solution
    
    # Format the recursive solution
    recursive_trips, recursive_total_cost, recursive_fixed_cost, recursive_fuel_cost, recursive_vehicles, recursive_distance, _ = recursive_solution
    
    print("\n=======================================")
    print("🔄 COMPARING SOLUTIONS")
    print("=======================================")
    
    print("\nRecursive Solution:")
    print(f"  Total Cost    : {recursive_total_cost}")
    print(f"  Fixed Cost    : {recursive_fixed_cost}")
    print(f"  Fuel Cost     : {recursive_fuel_cost}")
    print(f"  Vehicles Used : {recursive_vehicles}")
    print(f"  Total Distance: {recursive_distance}")
    
    print("\nOR-Tools Solution:")
    fixed_cost = sum(route[1] for route in ortools_routes)
    fuel_cost = sum(route[2] for route in ortools_routes)
    vehicles_used = len(ortools_routes)
    total_distance = sum(route[5] for route in ortools_routes)
    print(f"  Total Cost    : {ortools_cost}")
    print(f"  Fixed Cost    : {fixed_cost}")
    print(f"  Fuel Cost     : {fuel_cost}")
    print(f"  Vehicles Used : {vehicles_used}")
    print(f"  Total Distance: {total_distance}")
    
    # Calculate differences
    cost_diff = recursive_total_cost - ortools_cost
    vehicles_diff = recursive_vehicles - vehicles_used
    distance_diff = recursive_distance - total_distance
    
    print("\nDifferences (Recursive - OR-Tools):")
    print(f"  Cost Difference    : {cost_diff:.2f} ({(cost_diff/ortools_cost*100):.2f}% {'higher' if cost_diff > 0 else 'lower'})")
    print(f"  Vehicle Difference : {vehicles_diff}")
    print(f"  Distance Difference: {distance_diff:.2f} ({(distance_diff/total_distance*100):.2f}% {'longer' if distance_diff > 0 else 'shorter'})")
    
    # Detailed route comparison
    print("\nDetailed route comparison:")
    print("OR-Tools solution routes:")
    for i, (veh, _, _, deliveries, _, _, _) in enumerate(ortools_routes):
        nodes = [d[0] for d in deliveries]
        print(f"  Route {i+1}: Vehicle {veh}, delivers to {nodes}")
    
    print("\nRecursive solution routes:")
    for i, (veh, _, _, deliveries, _, _, _) in enumerate(recursive_trips):
        nodes = [d[0] for d in deliveries]
        print(f"  Route {i+1}: Vehicle {veh}, delivers to {nodes}")
    
    # Overall assessment
    if abs(cost_diff) < 0.01 and vehicles_diff == 0:
        print("\n✅ VERIFICATION SUCCESSFUL: Both methods found the same optimal solution!")
    elif cost_diff > 0:
        print(f"\n⚠️ Recursive solution costs {cost_diff:.2f} ({(cost_diff/ortools_cost*100):.2f}%) more than OR-Tools solution.")
    else:
        print(f"\n⚠️ Recursive solution costs {-cost_diff:.2f} ({(-cost_diff/ortools_cost*100):.2f}%) less than OR-Tools solution (unexpected!).")