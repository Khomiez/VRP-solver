"""
Algorithms for the VRP solver.
"""

from algorithms.routing import calculate_route_distance, find_best_route, is_valid_assignment
from algorithms.recursive_solver import find_optimal_solution, solve_vehicle_routing

# Import OR-Tools solver only if available
try:
    from algorithms.ortools_solver import verify_with_ortools, ORTOOLS_AVAILABLE
except ImportError:
    ORTOOLS_AVAILABLE = False
    
    def verify_with_ortools():
        """Placeholder function when OR-Tools is not available."""
        print("OR-Tools not available. Install with: pip install ortools")
        return None

__all__ = [
    'calculate_route_distance',
    'find_best_route',
    'is_valid_assignment',
    'find_optimal_solution',
    'solve_vehicle_routing',
    'verify_with_ortools',
    'ORTOOLS_AVAILABLE'
]