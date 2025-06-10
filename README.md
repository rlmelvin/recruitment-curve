# Anesthesiology Faculty Recruitment Model

A Streamlit web application that models the probability of successful faculty recruitment based on compensation using a pharmacological dose-response curve approach.

## Overview

This tool helps department chairs and administrators optimize faculty recruitment strategies by:
- Modeling recruitment probability as a function of compensation
- Incorporating departmental culture as a key factor
- Identifying optimal compensation levels to achieve target recruitment rates
- Visualizing the diminishing returns of excessive compensation

## Installation

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
streamlit run recruitment_model_app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Features

- **Interactive Parameters**: Adjust curve parameters, culture score, and target recruitment probability
- **Real-time Visualization**: See how changes affect the recruitment curve
- **Salary Recommendations**: Get recommended compensation based on your target probability
- **Culture Impact Analysis**: Understand how improving culture can reduce compensation costs

## Model Parameters

- **Maximum Probability (a)**: The ceiling for recruitment success (default: 0.92)
- **Slope (b)**: How steeply probability increases with compensation (default: 0.023)
- **Inflection Point (c)**: Compensation at 50% recruitment probability (default: $383K)
- **Culture Score**: -50 to +50, where each point ≈ $1,000 in compensation value

## Future Enhancements

This is a proof of concept. Future versions will:
- Incorporate historical recruitment data for parameter fitting
- Add subspecialty-specific models
- Include geographic adjustments
- Provide confidence intervals based on actual data