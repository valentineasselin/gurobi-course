import numpy as np
import gurobipy as gp
from gurobipy import GRB

def generate_knapsack(num_items):
    # Fix seed value
    rng = np.random.default_rng(seed=0)
    # Item values, weights
    values = rng.uniform(low=1, high=25, size=num_items)
    weights = rng.uniform(low=5, high=100, size=num_items)
    # Knapsack capacity
    capacity = 0.7 * weights.sum()
    
    return values, weights, capacity

def solve_knapsack_model(values, weights, capacity):
    num_items = len(values)
    # Turn values and weights numpy arrays to dict
    value_dict = {i: values[i] for i in range(num_items)}
    weight_dict = {i: weights[i] for i in range(num_items)}
    
    with gp.Env() as env:
        with gp.Model(name="knapsack", env=env) as model:
            # Define binary decision variables for each item
            x = model.addVars(num_items, vtype=GRB.BINARY, name="items")
            
            # Set objective: maximize total value
            obj = x.prod(value_dict)  # Multiplies each x[i] by corresponding value_dict[i]
            model.setObjective(obj, GRB.MAXIMIZE)
            
            # Add capacity constraint
            weight_expr = x.prod(weight_dict)  # Multiplies each x[i] by corresponding weight_dict[i]
            model.addConstr(weight_expr <= capacity, name="capacity")
            
            # Optimize the model
            model.optimize()
            
            # Print results if optimal solution found
            if model.status == GRB.OPTIMAL:
                print(f"\nOptimal objective value: {model.objVal:.2f}")
                print("\nSelected items:")
                selected = []
                for i in range(num_items):
                    if x[i].x > 0.5:  # Check if item is selected (binary var close to 1)
                        selected.append(i)
                print(f"Number of items selected: {len(selected)}")
                print(f"First few selected items: {selected[:5]}...")
                
                total_weight = sum(weights[i] for i in selected)
                print(f"\nTotal weight: {total_weight:.2f}")
                print(f"Capacity: {capacity:.2f}")
                print(f"Capacity utilization: {(total_weight/capacity)*100:.1f}%")
            else:
                print("No optimal solution found")

# Generate and solve a test problem
data = generate_knapsack(10000)
solve_knapsack_model(*data)