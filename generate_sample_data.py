#!/usr/bin/env python3
"""
Generate sample recruitment data for testing the fitting script.

This script creates synthetic offer/acceptance data based on the sigmoid model
with some noise to simulate real-world variation.
"""

import numpy as np
import pandas as pd
import argparse


def sigmoid_recruitment(x, a, b, c, k=0):
    """
    Calculate recruitment probability using sigmoidal dose-response curve
    """
    return a / (1 + np.exp(-b * (x - (c - k))))


def generate_sample_data(n_samples=200, noise_level=0.1, culture_std=20, 
                        output_file='sample_recruitment_data.csv', seed=42):
    """
    Generate synthetic recruitment data.
    
    Parameters:
    n_samples: Number of samples to generate
    noise_level: Amount of noise to add to the model
    culture_std: Standard deviation for culture effects
    output_file: Output CSV filename
    seed: Random seed for reproducibility
    """
    np.random.seed(seed)
    
    # True parameters (similar to defaults)
    a_true = 0.92
    b_true = 0.023
    c_true = 383
    
    # Generate salary offers
    # Sample more densely around the inflection point
    salaries_low = np.random.uniform(280, 350, n_samples // 3)
    salaries_mid = np.random.uniform(350, 450, n_samples // 3)
    salaries_high = np.random.uniform(450, 600, n_samples - 2 * (n_samples // 3))
    salaries = np.concatenate([salaries_low, salaries_mid, salaries_high])
    np.random.shuffle(salaries)
    
    # Generate hidden culture factors for each offer
    culture_factors = np.random.normal(0, culture_std, n_samples)
    
    # Calculate true probabilities including culture effects
    true_probs = sigmoid_recruitment(salaries, a_true, b_true, c_true, culture_factors)
    
    # Add noise to probabilities
    noisy_probs = true_probs + np.random.normal(0, noise_level, n_samples)
    noisy_probs = np.clip(noisy_probs, 0, 1)
    
    # Generate binary acceptances based on probabilities
    acceptances = np.random.binomial(1, noisy_probs)
    
    # Create dataframe
    df = pd.DataFrame({
        'salary offer ($USD)': (salaries * 1000).astype(int),
        'acceptance': acceptances
    })
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    # Print summary statistics
    print(f"Generated {n_samples} samples")
    print(f"Acceptance rate: {acceptances.mean():.2%}")
    print(f"Salary range: ${salaries.min():.0f}K - ${salaries.max():.0f}K")
    print(f"Mean salary: ${salaries.mean():.0f}K")
    
    # Print acceptance rates by salary band
    print("\nAcceptance rates by salary band:")
    bands = [(280, 350), (350, 400), (400, 450), (450, 500), (500, 600)]
    for low, high in bands:
        mask = (salaries >= low) & (salaries < high)
        if mask.sum() > 0:
            rate = acceptances[mask].mean()
            count = mask.sum()
            print(f"  ${low}K-${high}K: {rate:.1%} ({count} offers)")
    
    print(f"\nData saved to {output_file}")
    
    # Generate a separate test set
    test_file = output_file.replace('.csv', '_test.csv')
    generate_test_data(test_file, a_true, b_true, c_true, culture_std, seed+1)


def generate_test_data(output_file, a, b, c, culture_std, seed):
    """Generate a smaller test dataset"""
    np.random.seed(seed)
    
    n_test = 50
    test_salaries = np.random.uniform(300, 550, n_test)
    test_culture = np.random.normal(0, culture_std * 0.8, n_test)  # Slightly less variation
    
    test_probs = sigmoid_recruitment(test_salaries, a, b, c, test_culture)
    test_probs = np.clip(test_probs + np.random.normal(0, 0.05, n_test), 0, 1)
    test_acceptances = np.random.binomial(1, test_probs)
    
    test_df = pd.DataFrame({
        'salary offer ($USD)': (test_salaries * 1000).astype(int),
        'acceptance': test_acceptances
    })
    
    test_df.to_csv(output_file, index=False)
    print(f"\nTest data ({n_test} samples) saved to {output_file}")
    print(f"Test acceptance rate: {test_acceptances.mean():.2%}")


def main():
    parser = argparse.ArgumentParser(description='Generate sample recruitment data')
    parser.add_argument('--samples', type=int, default=200, help='Number of samples')
    parser.add_argument('--noise', type=float, default=0.1, help='Noise level (0-1)')
    parser.add_argument('--culture-std', type=float, default=20, help='Culture effect std dev')
    parser.add_argument('--output', default='sample_recruitment_data.csv', help='Output filename')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    generate_sample_data(
        n_samples=args.samples,
        noise_level=args.noise,
        culture_std=args.culture_std,
        output_file=args.output,
        seed=args.seed
    )


if __name__ == "__main__":
    main()