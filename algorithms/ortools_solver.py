"""
OR-Tools solver for the VRP solver.
Uses Google OR-Tools to solve the VRP as a Mixed Integer Programming problem.
"""

from itertools import combinations
import sys
from utils import log, timer
from models.data import distance_matrix, demands, vehicle_choices
# Import routing functions with original names
from algorithms.routing import find_best_route, is_valid_assignment

# Try to import OR-Tools, but make it optional
try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    print("Note: OR-Tools not available. Install with: pip install ortools")

def verify_with_ortools():
    """
    Create and solve a mathematical model of the problem using OR-Tools
    to verify the solution from our recursive algorithm.
    
    This function formulates the vehicle routing problem as a Mixed Integer Program (MIP)
    and uses OR-Tools to solve it. The main difference from the recursive approach is that
    this formulation:
    
    1. Uses a mathematical model with variables, constraints and an objective function
    2. Leverages a commercial-grade solver (SCIP) to find the optimal solution
    3. Provides a different algorithmic approach to verify our recursive solution
    
    Returns:
        tuple: (total_cost, solution_routes) if successful, None otherwise
    """
    if not ORTOOLS_AVAILABLE:
        print("\n=======================================")
        print("❌ OR-TOOLS NOT AVAILABLE")
        print("=======================================")
        print("Install OR-Tools to use mathematical verification:")
        print("pip install ortools")
        return None
        
    print("\n=======================================")
    print("🧮 VERIFYING WITH OR-TOOLS MIP MODEL")
    print("=======================================")
    
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("❌ Could not create solver!")
        return None
    
    # Input data
    vehicles = list(range(len(vehicle_choices)))  # Vehicle indices
    vehicle_names = [vc[0] for vc in vehicle_choices]
    fixed_costs = [vc[1] for vc in vehicle_choices]
    h_capacities = [vc[2] for vc in vehicle_choices]
    k_capacities = [vc[3] for vc in vehicle_choices]
    fuel_costs = [vc[4] for vc in vehicle_choices]
    
    nodes = list(demands.keys())  # Customer nodes: 1, 2, 3, 4
    h_demands = [demands[n][0] for n in nodes]
    k_demands = [demands[n][1] for n in nodes]
    
    all_nodes = [0] + nodes + [5, 6]  # Hub (0), customer nodes, G (5), H (6)
    
    print(f"Problem size: {len(vehicles)} vehicles, {len(nodes)} customer nodes")
    
    # Create variables
    
    # use[v] = 1 if vehicle v is used, 0 otherwise
    use = {}
    for v in vehicles:
        use[v] = solver.IntVar(0, 1, f'use_{v}')
    
    # assign[v][n] = 1 if vehicle v visits node n, 0 otherwise
    assign = {}
    for v in vehicles:
        assign[v] = {}
        for n in nodes:
            assign[v][n] = solver.IntVar(0, 1, f'assign_{v}_{n}')
    
    # Define precomputed route costs
    # For each vehicle, for each subset of nodes, calculate the best route cost
    route_costs = {}  # route_costs[v][frozenset({n1, n2, ...})] = (path, distance)
    
    print("Precomputing all possible routes...")
    for v in vehicles:
        route_costs[v] = {}
        vehicle_fuel_cost = fuel_costs[v]
        
        for subset_size in range(1, len(nodes) + 1):
            for subset in combinations(nodes, subset_size):
                # Check if this subset is valid for the vehicle's capacity
                if not is_valid_assignment(subset, h_capacities[v], k_capacities[v]):
                    continue
                
                # Find the best route for this subset
                path, distance, final_path = find_best_route(subset)
                
                # Calculate the cost: fixed cost + fuel cost * distance
                total_cost = fixed_costs[v] + vehicle_fuel_cost * distance
                
                # Store the route and cost
                subset_key = frozenset(subset)
                route_costs[v][subset_key] = (path, distance, total_cost, final_path)
    
    print(f"Computed {sum(len(routes) for routes in route_costs.values())} valid routes")
    
    # Create route variables - use binary variables to select which route each vehicle takes
    route_vars = {}
    for v in vehicles:
        route_vars[v] = {}
        for subset_key, (path, distance, cost, final_path) in route_costs[v].items():
            route_vars[v][subset_key] = solver.IntVar(0, 1, f'route_{v}_{list(subset_key)}')
    
    # Objective: minimize total cost
    objective = solver.Objective()
    for v in vehicles:
        for subset_key, (path, distance, cost, final_path) in route_costs[v].items():
            objective.SetCoefficient(route_vars[v][subset_key], cost)
    objective.SetMinimization()
    
    # Constraints:
    
    # 1. Each vehicle takes at most one route
    for v in vehicles:
        solver.Add(sum(route_vars[v][subset_key] for subset_key in route_costs[v]) <= 1)
    
    # 2. Each node must be visited exactly once
    for n in nodes:
        solver.Add(sum(
            route_vars[v][subset_key] for v in vehicles 
            for subset_key in route_costs[v] if n in subset_key
        ) == 1)
    
    # 3. Link use[v] variables with route selection
    for v in vehicles:
        solver.Add(use[v] == sum(route_vars[v][subset_key] for subset_key in route_costs[v]))
    
    # 4. Link assign[v][n] variables with route selection
    for v in vehicles:
        for n in nodes:
            solver.Add(assign[v][n] == sum(
                route_vars[v][subset_key] for subset_key in route_costs[v] if n in subset_key
            ))
    
    # Solve the model
    print("Solving the mathematical model...")
    with timer("OR-Tools MIP solver time"):
        status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print("\n✅ Optimal solution found with OR-Tools!")
        
        # Extract solution
        total_cost = solver.Objective().Value()
        vehicles_used = sum(use[v].solution_value() for v in vehicles)
        
        # Extract routes
        solution_routes = []
        for v in vehicles:
            for subset_key, (path, distance, cost, final_path) in route_costs[v].items():
                if route_vars[v][subset_key].solution_value() > 0.5:  # Route is selected
                    # Calculate fixed and fuel costs separately
                    vehicle_fixed_cost = fixed_costs[v]
                    vehicle_fuel_cost = fuel_costs[v] * distance
                    
                    # Format the route for output
                    subset_nodes = list(subset_key)
                    route_deliveries = [(n, f"H={demands[n][0]}", f"K={demands[n][1]}") for n in subset_nodes]
                    
                    solution_routes.append((
                        vehicle_names[v],
                        vehicle_fixed_cost,
                        vehicle_fuel_cost,
                        route_deliveries,
                        path,
                        distance,
                        final_path
                    ))
        
        # Display solution found by OR-Tools
        fixed_cost = sum(route[1] for route in solution_routes)
        fuel_cost = sum(route[2] for route in solution_routes)
        total_distance = sum(route[5] for route in solution_routes)
        
        print(f"\nSolution Statistics:")
        print(f"  Total Cost: {total_cost}")
        print(f"  Fixed Cost: {fixed_cost}")
        print(f"  Fuel Cost: {fuel_cost}")
        print(f"  Vehicles Used: {vehicles_used}")
        print(f"  Total Distance: {total_distance}")
        
        print("\nRoutes:")
        for i, (veh, veh_fixed_cost, veh_fuel_cost, deliveries, path, distance, final_path) in enumerate(solution_routes, 1):
            print(f"\n  Trip #{i} using Vehicle {veh}")
            
            # Display deliveries
            named_deliveries = []
            for node, h, k in deliveries:
                from models.data import node_to_name
                named_deliveries.append(f"{node_to_name(node)} ({h}, {k})")
            print(f"    Deliveries: {', '.join(named_deliveries)}")
            
            # Display route
            from models.data import node_to_name
            named_path = [node_to_name(node) for node in final_path]
            print(f"    Route: {' → '.join(named_path)}")
            print(f"    Distance: {distance}")
            print(f"    Total Cost: {veh_fixed_cost + veh_fuel_cost}")
        
        return total_cost, solution_routes
    
    else:
        print("❌ The solver couldn't find an optimal solution.")
        if status == pywraplp.Solver.FEASIBLE:
            print("  A feasible solution was found, but optimality couldn't be proven.")
        elif status == pywraplp.Solver.INFEASIBLE:
            print("  The problem is infeasible.")
        elif status == pywraplp.Solver.UNBOUNDED:
            print("  The problem is unbounded.")
        else:
            print("  Unknown solver status.")
        return None