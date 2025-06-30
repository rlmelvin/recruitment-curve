import matplotlib.pyplot as plt
import numpy as np
import json
import os

def sigmoid_recruitment(x, a, b, c, k=0):
    """
    Calculate recruitment probability using sigmoidal dose-response curve
    
    Parameters:
    x: compensation in thousands
    a: maximum probability (asymptote)
    b: slope (steepness)
    c: inflection point
    k: culture factor (shifts curve left/right)
    """
    return a / (1 + np.exp(-b * (x - (c - k))))

def generate_figure():
    """Generates and saves the recruitment model figure."""
    param_file = "parameters.json"
    if os.path.exists(param_file):
        with open(param_file, 'r') as f:
            params = json.load(f)
    else:
        # Default parameters if file doesn't exist
        params = {
            "curve_parameters": {
                "a": 0.92,
                "b": 0.023,
                "c": 383
            }
        }

    curve_params = params["curve_parameters"]
    a = curve_params["a"]
    b = curve_params["b"]
    c = curve_params["c"]

    x_national = np.linspace(250, 700, 500)
    
    y_baseline = sigmoid_recruitment(x_national, a, b, c, k=0)
    y_positive_culture = sigmoid_recruitment(x_national, a, b, c, k=30)
    y_negative_culture = sigmoid_recruitment(x_national, a, b, c, k=-20)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x_national, y_baseline, 'r-', label='Baseline Culture', linewidth=2)
    ax.plot(x_national, y_positive_culture, 'b--', label='Positive Culture (+30)', linewidth=2)
    ax.plot(x_national, y_negative_culture, 'g:', label='Negative Culture (-20)', linewidth=2)

    ax.set_xlabel('Annual Compensation ($1000s)', fontsize=12)
    ax.set_ylabel('Probability of Recruitment', fontsize=12)
    ax.set_title('Anesthesiology Faculty Recruitment Model', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    ax.set_xlim(300, 650)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig('explorations/recruitment_curve_figure.png', dpi=300)
    print("Figure saved to explorations/recruitment_curve_figure.png")

if __name__ == "__main__":
    generate_figure()