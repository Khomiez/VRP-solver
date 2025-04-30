"""
Solution model for the VRP solver.
Defines the solution structure and helper functions.
"""

class VRPSolution:
    """
    Class representing a Vehicle Routing Problem solution.
    """
    
    def __init__(self):
        """Initialize an empty solution."""
        self.trips = []
        self.cost = float('inf')
        self.fixed_cost = 0
        self.fuel_cost = 0
        self.vehicles_used = float('inf')
        self.total_distance = float('inf')
        self.completed = False
    
    def update_from_dict(self, solution_dict):
        """
        Update solution from a dictionary.
        
        Args:
            solution_dict (dict): Dictionary with solution data
        """
        self.trips = solution_dict["trips"]
        self.cost = solution_dict["cost"]
        self.fixed_cost = solution_dict["fixed_cost"]
        self.fuel_cost = solution_dict["fuel_cost"]
        self.vehicles_used = solution_dict["vehicles_used"]
        self.total_distance = solution_dict["total_distance"]
        self.completed = solution_dict["completed"]
    
    def to_dict(self):
        """
        Convert solution to a dictionary.
        
        Returns:
            dict: Dictionary representation of the solution
        """
        return {
            "trips": self.trips,
            "cost": self.cost,
            "fixed_cost": self.fixed_cost,
            "fuel_cost": self.fuel_cost,
            "vehicles_used": self.vehicles_used,
            "total_distance": self.total_distance,
            "completed": self.completed
        }
    
    def is_better_than(self, other_solution):
        """
        Determine if this solution is better than another solution.
        
        Args:
            other_solution: The solution to compare with
            
        Returns:
            bool: True if this solution is better, False otherwise
        """
        if not other_solution.completed:
            return self.completed
        
        if not self.completed:
            return False
            
        # First priority: minimize total cost
        if self.cost < other_solution.cost:
            return True
            
        # Second priority: minimize number of vehicles
        if self.cost == other_solution.cost and self.vehicles_used < other_solution.vehicles_used:
            return True
            
        # Third priority: minimize total distance
        if (self.cost == other_solution.cost and 
            self.vehicles_used == other_solution.vehicles_used and
            self.total_distance < other_solution.total_distance):
            return True
            
        return False
    
    def format_for_output(self, demands):
        """
        Format the solution for output.
        
        Args:
            demands (dict): Demand data
            
        Returns:
            tuple: Formatted solution data
        """
        if not self.completed:
            return [], 0, 0, 0, 0, 0, False
            
        formatted_trips = []
        for name, fixed_cost, nodes_subset, path, distance, fuel_cost_per_unit, final_path in self.trips:
            trip_fuel_cost = distance * fuel_cost_per_unit
            trip_deliveries = [(node, f"H={demands[node][0]}", f"K={demands[node][1]}") 
                              for node in nodes_subset if node in demands]
            formatted_trips.append((name, fixed_cost, trip_fuel_cost, trip_deliveries, 
                                  path, distance, final_path))
            
        return (
            formatted_trips,
            self.cost,
            self.fixed_cost,
            self.fuel_cost,
            self.vehicles_used,
            self.total_distance,
            True
        )