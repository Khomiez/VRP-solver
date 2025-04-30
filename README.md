# Vehicle Routing Problem (VRP) Solver

A sophisticated Python implementation for solving vehicle routing problems with multiple vehicle types, capacities, and costs.

## Features

- **Multiple Vehicle Types**: Different capacities, fixed costs, and fuel consumption rates
- **Multiple Goods Types**: Support for different types of goods with separate capacity constraints
- **Required Node Sequence**: Routes must pass through specific nodes in an optimal order
- **OR-Tools Verification**: Mathematical model using Google OR-Tools to verify optimality
- **Solution Analysis**: Detailed quality metrics and solution validation

## Project Structure

```
vrp_solver/
├── README.md
├── main.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   └── timer.py
├── models/
│   ├── __init__.py
│   ├── data.py
│   └── solution.py
├── algorithms/
│   ├── __init__.py
│   ├── routing.py
│   ├── recursive_solver.py
│   └── ortools_solver.py
└── visualization/
    ├── __init__.py
    ├── solution_display.py
    ├── solution_validation.py
    └── solution_analysis.py
```

## Usage

```bash
# Run default solver
python main.py

# Run verification with OR-Tools (requires OR-Tools installation)
python main.py --verify

# Analyze solution quality
python main.py --analyze

# Quiet mode (less verbose output)
python main.py --quiet

# Comprehensive analysis with comparison to OR-Tools
python main.py --verify --analyze
```

## Installation

```bash
# Install required dependencies
pip install ortools  # Optional, for mathematical verification
```

## Algorithms

The solver uses two primary algorithms:

1. **Recursive Algorithm**: A depth-first search with pruning to find optimal vehicle assignments and routes
2. **OR-Tools MIP Model**: A Mixed Integer Programming formulation for mathematical verification

Both approaches consider:
- Optimal ordering of delivery nodes 
- Strategic insertion of required nodes (G and H)
- Vehicle capacity constraints for multiple goods types
- Minimizing total cost (fixed vehicle costs + distance-based fuel costs)

## Customization

To customize the problem instance, edit the following files:

- `models/data.py`: Modify the distance matrix, demands, and vehicle options
- `algorithms/routing.py`: Adjust route calculation logic if needed
- `algorithms/recursive_solver.py`: Tune the optimization algorithm parameters

## Dependencies

- Python 3.6+
- OR-Tools (optional, for verification)