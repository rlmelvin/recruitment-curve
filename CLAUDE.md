# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anesthesiology Faculty Recruitment Model - a Streamlit web application that models the probability of successful faculty recruitment based on compensation using a pharmacological dose-response curve approach. The model helps department chairs optimize recruitment strategies by balancing compensation offers with departmental culture investments.

## Key Commands

### Running the Application
```bash
streamlit run recruitment_model_app.py
```
The app will open at `http://localhost:8501`

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture and Core Concepts

### Mathematical Model
The application implements a sigmoidal dose-response curve:
```python
P(Recruitment) = a / (1 + exp(-b(x - (c - k))))
```

Key parameters:
- `a`: Maximum recruitment probability (asymptote)
- `b`: Slope (steepness of the curve)
- `c`: Baseline inflection point (compensation at 50% probability)
- `k`: Culture factor (shifts curve left/right)

### Application Structure
- **recruitment_model_app.py**: Single-file Streamlit application containing:
  - `sigmoid_recruitment()`: Core mathematical function
  - `find_salary_for_probability()`: Inverse function to calculate required salary
  - Interactive sidebar with parameter sliders
  - Real-time visualization using matplotlib
  - Metrics display and strategic insights

### Key Design Decisions
1. Culture score ranges from -50 to +50, where each point represents approximately $1,000 in compensation value
2. The model assumes culture factors have linear, additive effects on the recruitment curve
3. Default parameters (a=0.92, b=0.023, c=383) are based on the ideation document's analysis of Southeast academic medical center data

## Development Context

The project originated from extensive research documented in `ideation.md` about the competitive anesthesiologist labor market. The application translates theoretical concepts into a practical tool for academic medical centers facing recruitment challenges with budget constraints.