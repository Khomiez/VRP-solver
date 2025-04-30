# Advanced Vehicle Routing Problem (VRP) Solver

A sophisticated Python implementation for solving complex vehicle routing problems with multiple vehicle types, capacities, and costs. This solver combines recursive optimization algorithms with mathematical programming verification through OR-Tools.

## Features

- **Multiple Vehicle Types**: Vehicles with different capacities, fixed costs, and fuel consumption rates
- **Multi-Commodity Constraints**: Support for multiple goods types (H and K) with separate capacity constraints
- **Required Path Constraints**: Routes must pass through specific nodes (G and H) in an optimal order at the end
- **Comprehensive Cost Model**: Balances fixed vehicle costs and distance-based variable costs
- **OR-Tools Verification**: Mathematical model using Google OR-Tools to verify optimality
- **Solution Quality Analysis**: Detailed metrics on vehicle utilization, distance efficiency, and cost breakdown
- **Extensible Framework**: Modular design allows for easy addition of new constraints and problem variants

## Project Structure

```
vrp_solver/
├── README.md
├── main.py                 # Main entry point with command-line interface
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── logger.py           # Logging utilities with configurable verbosity
│   └── timer.py            # Performance timing tools
├── models/                 # Problem models and data structures
│   ├── __init__.py
│   ├── data.py             # Problem data (distances, demands, vehicles)
│   └── solution.py         # Solution representation and evaluation
├── algorithms/             # Core solving algorithms
│   ├── __init__.py
│   ├── routing.py          # Route calculation and feasibility checking
│   ├── recursive_solver.py # Primary recursive optimization algorithm
│   └── ortools_solver.py   # Mathematical programming verification
└── visualization/          # Solution analysis and display
    ├── __init__.py
    ├── solution_display.py    # Pretty-printing of solutions
    ├── solution_validation.py # Validation of solution correctness
    └── solution_analysis.py   # Quantitative solution quality assessment
```

## Usage

```bash
# Run default solver and display solution
python main.py

# Run verification with OR-Tools mathematical model
python main.py --verify

# Analyze solution quality with detailed metrics
python main.py --analyze

# Run quietly (minimal console output)
python main.py --quiet

# Perform comprehensive analysis with OR-Tools comparison
python main.py --verify --analyze

# Run only the OR-Tools solver
python main.py --ortools
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vrp-solver.git
   cd vrp-solver
   ```

2. Install dependencies:
   ```bash
   # Required dependencies
   pip install numpy

   # Optional: for mathematical verification
   pip install ortools 
   ```

## Problem Definition

The solver addresses a specific variant of the Vehicle Routing Problem with these characteristics:

- **Multiple Depots**: A central hub where all vehicles start and end their routes
- **Node Types**: 
  - Hub (node 0)
  - Delivery locations (nodes 1-4, labeled A-D)
  - Required path nodes (nodes 5-6, labeled G-H)
  - Optional extension nodes (nodes 7-8, labeled E-F)
- **Vehicle Fleet**: 5 vehicle types (V, W, X, Y, Z) with different capacities and costs
- **Goods Types**: Two commodity types (H and K) with different demand at each location
- **Cost Structure**: 
  - Fixed cost per vehicle used
  - Variable fuel cost based on distance traveled
- **Path Constraints**: 
  - Every route must start at the hub
  - Every route must end by visiting G, H, and then returning to the hub
  - The order of G and H can be optimized based on which is closer to the last delivery

## Algorithms

The solver uses two primary algorithms:

### 1. Recursive Optimization Algorithm

The main solving approach uses a recursive depth-first search with intelligent pruning:

- Explores all feasible vehicle-to-node assignments
- Considers all possible node subsets for each vehicle
- Optimizes route ordering within each subset
- Applies strategic pruning to reduce the search space
- Prioritizes exploration by vehicle efficiency (capacity-to-cost ratio)

### 2. OR-Tools Mathematical Model

For verification, the problem is formulated as a Mixed Integer Program (MIP):

- Creates binary variables for vehicle selection and node assignment
- Precomputes optimal routes for each vehicle-subset combination
- Enforces capacity constraints, node coverage, and route continuity
- Uses the SCIP solver through Google OR-Tools to find the mathematically optimal solution

## Solution Validation

All solutions are automatically validated to ensure:

- All delivery nodes are visited exactly once
- Vehicle capacity constraints are respected
- Routes start and end at the hub
- Required nodes (G and H) are visited in the correct order
- All cost calculations are accurate

## Solution Quality Analysis

The solver provides detailed metrics on solution quality:

- **Vehicle Utilization**: How efficiently each vehicle's capacity is used
- **Distance Efficiency**: Comparison to theoretical minimum distances
- **Cost Breakdown**: Analysis of fixed vs. variable costs
- **Comparative Analysis**: When using the --verify flag, compares the recursive solution to the OR-Tools mathematical solution

## Customization

To customize the problem instance, edit the following files:

- `models/data.py`: 
  - Modify the distance matrix to change node locations
  - Adjust demands to change delivery requirements
  - Update vehicle_choices to modify the available fleet

- `algorithms/routing.py`: 
  - Modify route calculation logic to implement different routing rules
  - Adjust feasibility checking for additional constraints

- `algorithms/recursive_solver.py`: 
  - Tune the optimization algorithm parameters
  - Modify the pruning strategy to balance speed vs. optimality

## Example Output

When running the solver, you'll see detailed output like:

```
=======================================
🔍 FINDING OPTIMAL ROUTING SOLUTION...
=======================================

=======================================
🌟 OPTIMAL SOLUTION FOUND
=======================================

🚚 Trip #1 using Vehicle V
  Deliveries: A (H=1, K=0), D (H=1, K=0)
  Route     : Hub → A → D → G → H → Hub
  Distance  : 190
  Fixed Cost: 150
  Fuel Cost : 190
  Total Cost: 340

🚚 Trip #2 using Vehicle W
  Deliveries: B (H=0, K=2), C (H=1, K=2)
  Route     : Hub → B → C → G → H → Hub
  Distance  : 95
  Fixed Cost: 200
  Fuel Cost : 95
  Total Cost: 295

=======================================
💰 Total Fixed Cost: 350
⛽ Total Fuel Cost : 285
💵 Total Cost      : 635
🚚 Total Vehicles  : 2
📏 Total Distance  : 285
✅ All deliveries completed
=======================================
```

## Advanced Features

### Solution Quality Analysis

The `--analyze` flag provides detailed metrics:

```
=======================================
🔍 SOLUTION QUALITY ANALYSIS
=======================================

VEHICLE UTILIZATION:
  Vehicle V: H=2/2 (100.0%), K=0/2 (0.0%)
    Average capacity utilization: 50.0%
  Vehicle W: H=1/3 (33.3%), K=4/3 (133.3%)
    Average capacity utilization: 83.3%

DISTANCE EFFICIENCY:
  Vehicle V: Actual=190, Theoretical min≈180.0
    Efficiency ratio: 1.06x (closer to 1.0 is better)
  Vehicle W: Actual=95, Theoretical min≈90.0
    Efficiency ratio: 1.06x (closer to 1.0 is better)

  Overall efficiency ratio: 1.06x theoretical minimum

COST BREAKDOWN:
  Fixed costs: $350 (55.1% of total)
  Fuel costs:  $285 (44.9% of total)
  Total cost:  $635

SUMMARY EVALUATION:
  Vehicles used: 2
  Overall capacity utilization: H=60.0%, K=80.0%
  Overall routing efficiency: 1.06x theoretical minimum
=======================================
```

### Comparison with OR-Tools

The `--verify --analyze` combination provides a comprehensive comparison:

```
=======================================
🔄 COMPARING SOLUTIONS
=======================================

Recursive Solution:
  Total Cost    : 635
  Fixed Cost    : 350
  Fuel Cost     : 285
  Vehicles Used : 2
  Total Distance: 285

OR-Tools Solution:
  Total Cost    : 635
  Fixed Cost    : 350
  Fuel Cost     : 285
  Vehicles Used : 2
  Total Distance: 285

Differences (Recursive - OR-Tools):
  Cost Difference    : 0.00 (0.00% higher)
  Vehicle Difference : 0
  Distance Difference: 0.00 (0.00% longer)

✅ VERIFICATION SUCCESSFUL: Both methods found the same optimal solution!
```

## Contributing

Contributions are welcome! Areas for potential improvement:

1. Implementing additional VRP variants (time windows, pickup-and-delivery)
2. Enhancing the heuristic approach for larger problem instances
3. Adding visualization tools (route maps, Gantt charts)
4. Improving performance through parallelization or GPU acceleration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Google OR-Tools team for their excellent optimization library
- The operations research community for developing effective VRP algorithms