"""
Functions for analyzing VRP solutions.
"""

from models.data import distance_matrix, demands, vehicle_choices

def analyze_solution_quality(solution):
    """
    Analyzes the quality of the solution compared to theoretical ideals.
    Provides metrics on vehicle utilization, distance efficiency,
    and cost breakdown to evaluate solution quality.
    
    Args:
        solution (dict): Solution dictionary
    """
    print("\n=======================================")
    print("🔍 SOLUTION QUALITY ANALYSIS")
    print("=======================================")
    
    # 1. Vehicle utilization
    print("\nVEHICLE UTILIZATION:")
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        v_specs = next((v for v in vehicle_choices if v[0] == name), None)
        h_cap, k_cap = v_specs[2], v_specs[3]
        total_h = sum(demands[n][0] for n in nodes_subset if n in demands)
        total_k = sum(demands[n][1] for n in nodes_subset if n in demands)
        h_util = (total_h / h_cap) * 100 if h_cap > 0 else 0
        k_util = (total_k / k_cap) * 100 if k_cap > 0 else 0
        avg_util = (h_util + k_util) / 2
        
        print(f"  Vehicle {name}: H={total_h}/{h_cap} ({h_util:.1f}%), K={total_k}/{k_cap} ({k_util:.1f}%)")
        print(f"    Average capacity utilization: {avg_util:.1f}%")
    
    # 2. Distance efficiency
    print("\nDISTANCE EFFICIENCY:")
    total_straight_line = 0
    total_actual = 0
    
    for name, fixed_cost, nodes_subset, path, distance, fuel_cost, final_path in solution["trips"]:
        delivery_nodes = [n for n in nodes_subset if n in demands]
        if not delivery_nodes:
            continue
            
        # Calculate straight-line sum (simplistic TSP lower bound)
        if len(delivery_nodes) > 1:
            # Minimum spanning tree (MST) approximation for multi-node routes
            min_dist = 0
            remaining = set(delivery_nodes)
            current = 0  # Start at hub
            
            while remaining:
                # Find nearest node to current
                nearest = min(remaining, key=lambda n: distance_matrix[current][n])
                min_dist += distance_matrix[current][nearest]
                current = nearest
                remaining.remove(nearest)
            
            # Add required connection to G (5) if not in delivery nodes
            if 5 not in nodes_subset:
                min_dist += distance_matrix[current][5]
                current = 5
            
            # Add required connection to H (6) if not in delivery nodes
            if 6 not in nodes_subset:
                min_dist += distance_matrix[current][6]
                current = 6
            
            # Add return to Hub
            min_dist += distance_matrix[current][0]
        else:
            # For single node, it's just hub -> node -> G -> H -> Hub 
            # (unless G or H are the delivery node)
            node = delivery_nodes[0]
            current = 0
            min_dist = distance_matrix[current][node]
            current = node
            
            # Add G if not the delivery node
            if 5 not in nodes_subset:
                min_dist += distance_matrix[current][5]
                current = 5
                
            # Add H if not the delivery node
            if 6 not in nodes_subset:
                min_dist += distance_matrix[current][6]
                current = 6
                
            # Return to Hub
            min_dist += distance_matrix[current][0]
        
        efficiency_ratio = distance/min_dist if min_dist > 0 else float('inf')
        print(f"  Vehicle {name}: Actual={distance}, Theoretical min≈{min_dist:.1f}")
        print(f"    Efficiency ratio: {efficiency_ratio:.2f}x (closer to 1.0 is better)")
        
        total_straight_line += min_dist
        total_actual += distance
    
    # Overall efficiency
    overall_ratio = total_actual/total_straight_line if total_straight_line > 0 else float('inf')
    print(f"\n  Overall efficiency ratio: {overall_ratio:.2f}x theoretical minimum")
    
    # 3. Cost efficiency analysis
    total_fixed_cost = solution["fixed_cost"]
    total_fuel_cost = solution["fuel_cost"]
    total_cost = solution["cost"]
    fixed_cost_pct = (total_fixed_cost / total_cost) * 100 if total_cost > 0 else 0
    fuel_cost_pct = (total_fuel_cost / total_cost) * 100 if total_cost > 0 else 0
    
    print("\nCOST BREAKDOWN:")
    print(f"  Fixed costs: ${total_fixed_cost} ({fixed_cost_pct:.1f}% of total)")
    print(f"  Fuel costs:  ${total_fuel_cost} ({fuel_cost_pct:.1f}% of total)")
    print(f"  Total cost:  ${total_cost}")
    
    # 4. Summary
    print("\nSUMMARY EVALUATION:")
    
    # Evaluate number of vehicles
    min_vehicles_needed = 1  # Theoretical minimum
    print(f"  Vehicles used: {len(solution['trips'])}")
    
    # Evaluate capacity utilization
    total_h_capacity = sum(v_specs[2] for v_specs in vehicle_choices for trip in solution["trips"] if trip[0] == v_specs[0])
    total_k_capacity = sum(v_specs[3] for v_specs in vehicle_choices for trip in solution["trips"] if trip[0] == v_specs[0])
    total_h_demand = sum(demands[n][0] for n in demands)
    total_k_demand = sum(demands[n][1] for n in demands)
    
    h_utilization = (total_h_demand / total_h_capacity) * 100 if total_h_capacity > 0 else 0
    k_utilization = (total_k_demand / total_k_capacity) * 100 if total_k_capacity > 0 else 0
    
    print(f"  Overall capacity utilization: H={h_utilization:.1f}%, K={k_utilization:.1f}%")
    
    # Evaluate routing efficiency
    print(f"  Overall routing efficiency: {overall_ratio:.2f}x theoretical minimum")
    print("=======================================")