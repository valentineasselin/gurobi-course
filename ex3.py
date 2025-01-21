from functools import partial
import gurobipy as gp
from gurobipy import GRB


class CallbackData:
    def __init__(self):
        self.last_gap_change_time = -GRB.INFINITY
        self.last_gap = GRB.INFINITY


def callback(model, where, *, cbdata):
    if where != GRB.Callback.MIP:
        return
    if model.cbGet(GRB.Callback.MIP_SOLCNT) == 0:
        return

    # Get current runtime and gap
    runtime = model.cbGet(GRB.Callback.RUNTIME)
    objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
    objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
    
    # Calculate current gap
    if abs(objbst) < 1e-10:
        gap = GRB.INFINITY if abs(objbnd) > 1e-10 else 0.0
    else:
        gap = abs(objbnd - objbst) / abs(objbst)
    
    # Check if gap has improved significantly
    if abs(gap - cbdata.last_gap) > epsilon_to_compare_gap:
        cbdata.last_gap = gap
        cbdata.last_gap_change_time = runtime
    
    # Check termination criteria:
    # 1. If we have a feasible solution
    # 2. If time since last significant gap improvement exceeds threshold
    if (runtime - cbdata.last_gap_change_time) > time_from_best:
        print(f"\nTerminating - No significant improvement for {time_from_best} seconds")
        print(f"Current gap: {gap:.2%}")
        print(f"Time since last improvement: {runtime - cbdata.last_gap_change_time:.1f} seconds")
        model.terminate()


with gp.read("data/mkp.mps") as model:
    # Global variables used in the callback function
    time_from_best = 15  # Time threshold for termination (seconds)
    epsilon_to_compare_gap = 1e-4  # Threshold for considering gap improvement significant
    
    # Initialize data passed to the callback function
    callback_data = CallbackData()
    callback_func = partial(callback, cbdata=callback_data)
    
    # Set some useful parameters
    model.Params.OutputFlag = 1  # Enable solver output
    model.Params.MIPGap = 1e-4  # Set desired optimality gap
    
    model.optimize(callback_func)
    
    # Print final solution statistics
    if model.Status == GRB.OPTIMAL:
        print("\nOptimal solution found")
    elif model.Status == GRB.INTERRUPTED:
        print("\nSolution process interrupted by callback")
    print(f"Best objective: {model.ObjVal:.2f}")
    print(f"Final gap: {model.MIPGap:.2%}")
    print(f"Solution time: {model.Runtime:.1f} seconds")