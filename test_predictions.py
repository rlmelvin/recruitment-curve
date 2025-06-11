#!/usr/bin/env python3
"""
Test predictions on unseen recruitment data using fitted parameters.

This script loads fitted parameters and evaluates model performance on test data.
"""

import numpy as np
import pandas as pd
import json
import argparse
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt


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


def test_predictions(test_data_path, param_file='parameters.json', threshold=0.5, plot=False):
    """
    Test recruitment predictions on unseen data.
    
    Parameters:
    test_data_path: Path to CSV file with test data
    param_file: Path to parameters JSON file
    threshold: Probability threshold for binary classification
    plot: Whether to show plots
    
    Returns:
    Dictionary with test metrics
    """
    # Load parameters
    with open(param_file, 'r') as f:
        params = json.load(f)
    
    if not params.get('fitted', False):
        print("Warning: Using default parameters (not fitted from data)")
    
    curve_params = params['curve_parameters']
    a, b, c = curve_params['a'], curve_params['b'], curve_params['c']
    
    # Load test data
    df = pd.read_csv(test_data_path)
    salaries = df['salary offer ($USD)'] / 1000
    actual = df['acceptance']
    
    # Make predictions (assuming culture = 0 for now)
    probabilities = sigmoid_recruitment(salaries, a, b, c, k=0)
    predictions = (probabilities >= threshold).astype(int)
    
    # Calculate metrics
    accuracy = accuracy_score(actual, predictions)
    auc = roc_auc_score(actual, probabilities)
    cm = confusion_matrix(actual, predictions)
    
    # Calculate additional metrics
    tn, fp, fn, tp = cm.ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    results = {
        'n_samples': len(df),
        'accuracy': float(accuracy),
        'auc': float(auc),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'confusion_matrix': cm.tolist(),
        'threshold': threshold
    }
    
    # Print results
    print(f"\nTest Results on {len(df)} samples:")
    print(f"Accuracy: {accuracy:.3f}")
    print(f"AUC: {auc:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"F1 Score: {f1:.3f}")
    print(f"\nConfusion Matrix:")
    print(f"                 Predicted")
    print(f"                 Reject  Accept")
    print(f"Actual Reject    {tn:>6}  {fp:>6}")
    print(f"Actual Accept    {fn:>6}  {tp:>6}")
    
    # Calculate prediction intervals
    residuals = actual - probabilities
    residual_std = np.std(residuals)
    
    print(f"\nResidual Analysis:")
    print(f"Mean residual: {np.mean(residuals):.3f}")
    print(f"Std residual: {residual_std:.3f}")
    
    if plot:
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Scatter plot with curve
        ax1 = axes[0, 0]
        ax1.scatter(salaries[actual == 1], actual[actual == 1], 
                   color='green', alpha=0.6, label='Accepted', s=50)
        ax1.scatter(salaries[actual == 0], actual[actual == 0], 
                   color='red', alpha=0.6, label='Rejected', s=50)
        
        x_range = np.linspace(salaries.min() - 50, salaries.max() + 50, 500)
        y_curve = sigmoid_recruitment(x_range, a, b, c)
        ax1.plot(x_range, y_curve, 'b-', linewidth=2, label='Model Prediction')
        ax1.axhline(y=threshold, color='orange', linestyle='--', label=f'Threshold={threshold}')
        
        ax1.set_xlabel('Salary Offer ($1000s)')
        ax1.set_ylabel('Recruitment Probability')
        ax1.set_title('Model Predictions vs Actual')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Residual plot
        ax2 = axes[0, 1]
        ax2.scatter(salaries, residuals, alpha=0.6)
        ax2.axhline(y=0, color='red', linestyle='-')
        ax2.axhline(y=2*residual_std, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(y=-2*residual_std, color='red', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Salary Offer ($1000s)')
        ax2.set_ylabel('Residual (Actual - Predicted)')
        ax2.set_title('Residual Plot')
        ax2.grid(True, alpha=0.3)
        
        # 3. Probability distribution
        ax3 = axes[1, 0]
        ax3.hist(probabilities[actual == 1], bins=20, alpha=0.6, 
                color='green', label='Accepted', density=True)
        ax3.hist(probabilities[actual == 0], bins=20, alpha=0.6, 
                color='red', label='Rejected', density=True)
        ax3.axvline(x=threshold, color='orange', linestyle='--', label=f'Threshold={threshold}')
        ax3.set_xlabel('Predicted Probability')
        ax3.set_ylabel('Density')
        ax3.set_title('Distribution of Predicted Probabilities')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. ROC curve
        from sklearn.metrics import roc_curve
        ax4 = axes[1, 1]
        fpr, tpr, thresholds = roc_curve(actual, probabilities)
        ax4.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC={auc:.3f})')
        ax4.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random')
        ax4.set_xlabel('False Positive Rate')
        ax4.set_ylabel('True Positive Rate')
        ax4.set_title('ROC Curve')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    # Analyze misclassifications
    misclassified = df[predictions != actual].copy()
    if len(misclassified) > 0:
        misclassified['predicted_prob'] = probabilities[predictions != actual]
        misclassified['error_type'] = misclassified.apply(
            lambda row: 'False Positive' if row['acceptance'] == 0 else 'False Negative', 
            axis=1
        )
        
        print(f"\nMisclassification Analysis:")
        print(f"Total misclassified: {len(misclassified)}")
        
        fp_salaries = misclassified[misclassified['error_type'] == 'False Positive']['salary offer ($USD)'] / 1000
        fn_salaries = misclassified[misclassified['error_type'] == 'False Negative']['salary offer ($USD)'] / 1000
        
        if len(fp_salaries) > 0:
            print(f"False Positives: {len(fp_salaries)} (mean salary: ${fp_salaries.mean():.0f}K)")
        if len(fn_salaries) > 0:
            print(f"False Negatives: {len(fn_salaries)} (mean salary: ${fn_salaries.mean():.0f}K)")
        
        # Suggest culture bounds based on misclassifications
        if len(fn_salaries) > 0:
            # False negatives might indicate positive culture effects
            avg_fn_salary = fn_salaries.mean()
            expected_prob = sigmoid_recruitment(avg_fn_salary, a, b, c)
            culture_shift_needed = (1/b) * np.log(a/0.8 - 1) - (1/b) * np.log(a/expected_prob - 1)
            print(f"\nEstimated positive culture effect for false negatives: +{culture_shift_needed:.0f} points")
        
        if len(fp_salaries) > 0:
            # False positives might indicate negative culture effects
            avg_fp_salary = fp_salaries.mean()
            expected_prob = sigmoid_recruitment(avg_fp_salary, a, b, c)
            culture_shift_needed = (1/b) * np.log(a/expected_prob - 1) - (1/b) * np.log(a/0.2 - 1)
            print(f"Estimated negative culture effect for false positives: -{culture_shift_needed:.0f} points")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Test recruitment model predictions')
    parser.add_argument('test_file', help='Path to CSV file with test data')
    parser.add_argument('--params', default='parameters.json', help='Path to parameters file')
    parser.add_argument('--threshold', type=float, default=0.5, help='Classification threshold')
    parser.add_argument('--plot', action='store_true', help='Show diagnostic plots')
    
    args = parser.parse_args()
    
    results = test_predictions(args.test_file, args.params, args.threshold, args.plot)
    
    # Save results
    output_file = args.test_file.replace('.csv', '_test_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to {output_file}")


if __name__ == "__main__":
    main()