# Anesthesiology Faculty Recruitment Model

A Streamlit web application that models the probability of successful faculty recruitment based on compensation using a pharmacological dose-response curve approach. The model can be fitted to actual offer/acceptance data for improved accuracy.

## Overview

This tool helps department chairs and administrators optimize faculty recruitment strategies by:
- Modeling recruitment probability as a function of compensation using a sigmoid curve
- Fitting parameters from historical offer/acceptance data
- Incorporating departmental culture as a key factor with data-driven bounds
- Identifying optimal compensation levels to achieve target recruitment rates
- Testing model performance on unseen data

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Using Default Parameters
```bash
streamlit run recruitment_model_app.py
```

### Fitting to Your Data
1. Prepare a CSV with columns: `salary offer ($USD)`, `acceptance` (0/1)
2. Fit the model:
   ```bash
   python fit_parameters.py your_data.csv --plot
   ```
3. Run the app with fitted parameters:
   ```bash
   streamlit run recruitment_model_app.py
   ```

## Scripts and Tools

### Data Fitting (`fit_parameters.py`)
Fits sigmoid curve parameters from offer/acceptance data and estimates culture factor bounds.

```bash
# Fit parameters with visualization
python fit_parameters.py data.csv --plot

# Fit and save to custom file
python fit_parameters.py data.csv --output custom_params.json
```

### Model Testing (`test_predictions.py`)
Evaluates model performance on test data with comprehensive metrics.

```bash
# Test with diagnostic plots
python test_predictions.py test_data.csv --plot

# Use custom threshold
python test_predictions.py test_data.csv --threshold 0.7
```

### Sample Data Generation (`generate_sample_data.py`)
Creates synthetic recruitment data for testing the fitting pipeline.

```bash
# Generate 200 samples with default settings
python generate_sample_data.py

# Custom parameters
python generate_sample_data.py --samples 500 --noise 0.15 --culture-std 30
```

## Data Format

Your CSV file should contain exactly two columns:
- `salary offer ($USD)`: Annual salary offers in US dollars
- `acceptance`: Binary (0 = rejected, 1 = accepted)

Example:
```csv
salary offer ($USD),acceptance
350000,0
425000,1
380000,0
450000,1
```

## Model Parameters

The sigmoid recruitment model uses the equation:
```
P(Recruitment) = a / (1 + exp(-b(x - (c - k))))
```

Where:
- **a**: Maximum recruitment probability (asymptote)
- **b**: Slope (steepness of the curve)
- **c**: Baseline inflection point (compensation at 50% probability)
- **k**: Culture factor (shifts curve left/right)

### Parameter Sources
- **Default**: Based on Southeast academic medical center analysis
- **Fitted**: Estimated from your historical data using nonlinear regression
- **Culture Bounds**: Dynamically estimated from data variance

## App Features

- **Adaptive Parameters**: Automatically loads fitted parameters if available
- **Data-Driven Culture Bounds**: Slider ranges based on actual data variance
- **Real-time Visualization**: Interactive curve updates with parameter changes
- **Salary Recommendations**: Compensation targets for desired recruitment probability
- **Regional Adjustments**: Cost of living adjustments for different markets
- **Performance Metrics**: Display of model fit quality when using fitted parameters

## Testing and Validation

The package includes comprehensive testing tools:

- **Accuracy Metrics**: Precision, recall, F1-score, AUC
- **Diagnostic Plots**: ROC curves, residual analysis, probability distributions
- **Misclassification Analysis**: Identifies patterns in prediction errors
- **Cross-validation Ready**: Easily test on hold-out datasets

## File Structure

```
recruitment_curve/
├── recruitment_model_app.py    # Main Streamlit application
├── fit_parameters.py           # Parameter fitting script
├── test_predictions.py         # Model testing and validation
├── generate_sample_data.py     # Synthetic data generator
├── parameters.json             # Model parameters (auto-updated)
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## Advanced Usage

### Custom Parameter Files
```bash
# Fit to specific parameter file
python fit_parameters.py data.csv --output dept_specific.json

# Use specific parameters in testing
python test_predictions.py test.csv --params dept_specific.json
```

### Batch Processing
```bash
# Generate multiple test datasets
for i in {1..5}; do
    python generate_sample_data.py --output test_${i}.csv --seed $i
done

# Test each dataset
for file in test_*.csv; do
    python test_predictions.py "$file" --plot
done
```