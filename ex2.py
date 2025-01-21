import json
import pandas as pd
import numpy as np
import gurobipy as gp
from gurobipy import GRB

# Read the input data
with open("data/portfolio-example.json", "r") as f:
    data = json.load(f)

n = data["num_assets"]
sigma = np.array(data["covariance"])
mu = np.array(data["expected_return"])
mu_0 = data["target_return"]
k = data["portfolio_max_size"]

with gp.Model("portfolio") as model:
    # Create continuous variables for portfolio weights (x)
    x = model.addVars(n, lb=0, ub=1, name="x")
    
    # Create binary variables for asset selection (y)
    y = model.addVars(n, vtype=GRB.BINARY, name="y")
    
    # Add variable to represent the portfolio variance (risk)
    risk = model.addVar(name="risk")
    
    # Set objective: minimize portfolio variance
    # Note: risk = x^T * Sigma * x
    quad_expr = gp.QuadExpr()
    for i in range(n):
        for j in range(n):
            quad_expr.add(sigma[i][j] * x[i] * x[j])
    model.setObjective(quad_expr, GRB.MINIMIZE)
    
    # Constraint: sum of weights equals 1
    model.addConstr(gp.quicksum(x[i] for i in range(n)) == 1, "sum_one")
    
    # Constraint: expected return >= target return
    model.addConstr(
        gp.quicksum(mu[i] * x[i] for i in range(n)) >= mu_0,
        name="return"
    )
    
    # Constraint: maximum number of assets (cardinality)
    model.addConstr(gp.quicksum(y[i] for i in range(n)) <= k, "cardinality")
    
    # Constraint: link x and y variables
    # If y[i] = 0, then x[i] must be 0
    for i in range(n):
        model.addConstr(x[i] <= y[i], f"link_{i}")
    
    model.optimize()

    # Extract solution
    portfolio = [var.X for var in model.getVars() if "x" in var.VarName]
    risk = model.ObjVal
    expected_return = model.getRow(model.getConstrByName("return")).getValue()
    
    # Create results DataFrame
    df = pd.DataFrame(
        data=portfolio + [risk, expected_return],
        index=[f"asset_{i}" for i in range(n)] + ["risk", "return"],
        columns=["Portfolio"],
    )
    print(df)