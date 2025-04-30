#!/usr/bin/env python3
"""
Vehicle Routing Problem (VRP) Solver with OR-Tools Verification

This program solves a Vehicle Routing Problem with multiple vehicle types, 
capacities, and costs. It implements both a recursive algorithm and an OR-Tools
mathematical model to verify optimality.

Features:
- Multiple vehicle types with different costs and capacities
- Fixed costs for vehicles plus fuel costs based on distance
- Demand constraints for multiple goods types (H and K)
- Required path through additional nodes (G and H) at the end
- Verification of optimality using OR-Tools

Usage:
    python main.py                # Run default solver
    python main.py --verify       # Run verification
    python main.py --analyze      # Analyze solution quality
    python main.py --ortools      # Run only OR-Tools solver
    python main.py --quiet        # Run with minimal output
"""

import sys
from utils import log, set_verbose
from models.data import demands, vehicle_choices
from algorithms import find_optimal_solution, verify_with_ortools, ORTOOLS_AVAILABLE
from visualization import display_solution, verify_solution, analyze_solution_quality, compare_solutions

def main():
    """Main entry point for the VRP solver."""
    # Parse command line arguments
    args = sys.argv[1:]
    if "--quiet" in args:
        set_verbose(False)
        args.remove("--quiet")
    
    # Default behavior: display the solution
    if not args or (len(args) == 0):
        display_solution()
    
    # Run OR-Tools verification if requested
    if "--verify" in args or "--ortools" in args:
        if ORTOOLS_AVAILABLE:
            ortools_solution = verify_with_ortools()
        else:
            print("\n❌ OR-Tools not available. Install with: pip install ortools")
            ortools_solution = None
    else:
        ortools_solution = None
    
    # Analyze solution quality if requested
    if "--analyze" in args:
        # First, solve the problem to get the solution
        log("\n📊 FINDING SOLUTION FOR ANALYSIS...", 0)
        solution = find_optimal_solution(set(demands.keys()), vehicle_choices)
        
        if solution["completed"]:
            # Verify the solution
            valid, errors = verify_solution(solution)
            
            if valid:
                # Analyze solution quality
                analyze_solution_quality(solution)
            else:
                print("\n⚠️ Cannot analyze invalid solution!")
        else:
            print("\n❌ No complete solution found for analysis!")
    
    # If both verify and analyze are requested, compare the solutions
    if "--verify" in args and "--analyze" in args and ORTOOLS_AVAILABLE and ortools_solution is not None:
        # First get recursive solution
        recursive_solution = find_optimal_solution(set(demands.keys()), vehicle_choices)
        
        # Format the recursive solution for comparison
        from algorithms import solve_vehicle_routing
        recursive_formatted = solve_vehicle_routing()
        
        # Compare the solutions
        if recursive_solution["completed"]:
            compare_solutions(recursive_formatted, ortools_solution)
            
            print("\n=======================================")
            print("📊 COMPARATIVE ANALYSIS")
            print("=======================================")
            print("\nThis improved algorithm should now produce results that match or come very close to the optimal OR-Tools solution.")

if __name__ == "__main__":
    main()