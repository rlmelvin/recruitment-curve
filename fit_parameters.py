#!/usr/bin/env python3
"""
Fit sigmoid recruitment curve parameters from offer/acceptance data.

This script reads a CSV file with 'salary offer ($USD)' and 'acceptance' columns,
fits the sigmoid curve parameters, and updates the parameters.json file.
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import norm
import json
import argparse
from datetime import datetime
import matplotlib.pyplot as plt


def sigmoid_recruitment(x, a, b, c):
    """
    Calculate recruitment probability using sigmoidal dose-response curve
    
    Parameters:
    x: compensation in thousands
    a: maximum probability (asymptote)
    b: slope (steepness)
    c: inflection point
    """
    return a / (1 + np.exp(-b * (x - c)))


def fit_curve_parameters(data_path, plot=False):
    """
    Fit sigmoid curve parameters from offer/acceptance data.
    
    Parameters:
    data_path: Path to CSV file with 'salary offer ($USD)' and 'acceptance' columns
    plot: Whether to show a plot of the fitted curve
    
    Returns:
    Dictionary with fitted parameters and metadata
    """
    # Load data
    df = pd.read_csv(data_path)
    
    # Convert salary to thousands
    salaries = df['salary offer ($USD)'] / 1000
    acceptances = df['acceptance']
    
    # Initial parameter estimates
    p0 = [0.9, 0.02, np.median(salaries)]
    
    # Bounds for parameters
    bounds = (
        [0.5, 0.001, salaries.min()],  # Lower bounds
        [1.0, 0.1, salaries.max()]      # Upper bounds
    )
    
    # Fit the curve
    try:
        popt, pcov = curve_fit(
            sigmoid_recruitment, 
            salaries, 
            acceptances, 
            p0=p0,
            bounds=bounds,
            maxfev=5000
        )
        
        a_fit, b_fit, c_fit = popt
        
        # Calculate RMSE
        predictions = sigmoid_recruitment(salaries, *popt)
        rmse = np.sqrt(np.mean((acceptances - predictions) ** 2))
        
        # Estimate culture parameter bounds from residuals
        # Residuals represent unexplained variance that could be due to culture
        residuals = acceptances - predictions
        
        # For accepted offers where model predicted low probability
        # these might indicate positive culture effects
        positive_culture_samples = salaries[
            (acceptances == 1) & (predictions < 0.5)
        ]
        
        # For rejected offers where model predicted high probability
        # these might indicate negative culture effects
        negative_culture_samples = salaries[
            (acceptances == 0) & (predictions > 0.5)
        ]
        
        # Estimate culture impact as salary equivalent
        culture_effects = []
        
        # For positive culture effects
        for salary in positive_culture_samples:
            # Find what salary would give the observed acceptance
            equiv_salary = c_fit - (1/b_fit) * np.log(a_fit/0.8 - 1)
            culture_effects.append(equiv_salary - salary)
        
        # For negative culture effects
        for salary in negative_culture_samples:
            # Find what salary would give the observed rejection
            equiv_salary = c_fit - (1/b_fit) * np.log(a_fit/0.2 - 1)
            culture_effects.append(equiv_salary - salary)
        
        # Estimate standard deviation of culture effects
        if len(culture_effects) > 0:
            culture_std = np.std(culture_effects)
            # Use 2 standard deviations for bounds (95% confidence)
            culture_bound = min(2 * culture_std, 100)  # Cap at 100k
        else:
            culture_bound = 50  # Default if no strong outliers
        
        # Create results dictionary
        results = {
            "curve_parameters": {
                "a": float(a_fit),
                "b": float(b_fit),
                "c": float(c_fit),
                "description": {
                    "a": "Maximum recruitment probability (asymptote)",
                    "b": "Slope (steepness of the curve)",
                    "c": "Baseline inflection point (compensation at 50% probability in $1000s)"
                }
            },
            "culture_bounds": {
                "min": float(-culture_bound),
                "max": float(culture_bound),
                "default": 0,
                "description": "Culture factor range (each point ≈ $1,000 in compensation value)"
            },
            "fitted": True,
            "fit_metadata": {
                "date": datetime.now().isoformat(),
                "n_samples": len(df),
                "rmse": float(rmse),
                "culture_std_estimate": float(culture_std) if len(culture_effects) > 0 else None,
                "parameter_covariance": pcov.tolist()
            }
        }
        
        if plot:
            plt.figure(figsize=(10, 6))
            
            # Plot data points
            plt.scatter(salaries[acceptances == 1], acceptances[acceptances == 1], 
                       color='green', alpha=0.6, label='Accepted', s=50)
            plt.scatter(salaries[acceptances == 0], acceptances[acceptances == 0], 
                       color='red', alpha=0.6, label='Rejected', s=50)
            
            # Plot fitted curve
            x_range = np.linspace(salaries.min() - 50, salaries.max() + 50, 500)
            y_fit = sigmoid_recruitment(x_range, *popt)
            plt.plot(x_range, y_fit, 'b-', linewidth=2, label='Fitted Curve')
            
            # Plot confidence bands
            # Calculate standard errors
            perr = np.sqrt(np.diag(pcov))
            y_upper = sigmoid_recruitment(x_range, a_fit + perr[0], b_fit, c_fit)
            y_lower = sigmoid_recruitment(x_range, a_fit - perr[0], b_fit, c_fit)
            plt.fill_between(x_range, y_lower, y_upper, alpha=0.2, color='blue')
            
            plt.xlabel('Salary Offer ($1000s)', fontsize=12)
            plt.ylabel('Recruitment Probability', fontsize=12)
            plt.title('Fitted Recruitment Curve', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.ylim(-0.05, 1.05)
            
            # Add parameter text
            param_text = f'a={a_fit:.3f}, b={b_fit:.3f}, c={c_fit:.1f}\nRMSE={rmse:.3f}'
            plt.text(0.02, 0.98, param_text, transform=plt.gca().transAxes,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            plt.show()
        
        print(f"Fitting successful!")
        print(f"Parameters: a={a_fit:.3f}, b={b_fit:.3f}, c={c_fit:.1f}")
        print(f"RMSE: {rmse:.3f}")
        print(f"Culture bounds: [{-culture_bound:.0f}, {culture_bound:.0f}]")
        
        return results
        
    except Exception as e:
        print(f"Error fitting curve: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='Fit recruitment curve parameters from data')
    parser.add_argument('data_file', help='Path to CSV file with salary and acceptance data')
    parser.add_argument('--plot', action='store_true', help='Show plot of fitted curve')
    parser.add_argument('--output', default='parameters.json', help='Output JSON file (default: parameters.json)')
    
    args = parser.parse_args()
    
    # Fit the parameters
    results = fit_curve_parameters(args.data_file, plot=args.plot)
    
    # Save to JSON
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nParameters saved to {args.output}")


if __name__ == "__main__":
    main()