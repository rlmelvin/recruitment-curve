import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

st.set_page_config(
    page_title="Anesthesiology Faculty Recruitment Model",
    page_icon="📊",
    layout="wide"
)

st.title("Anesthesiology Faculty Recruitment Model")
st.markdown("### A Dose-Response Approach to Optimizing Compensation and Culture")

st.markdown("""
This tool models the probability of successful faculty recruitment based on compensation 
using a pharmacological dose-response curve approach. The model incorporates departmental 
culture as a key factor that can shift the recruitment curve.
""")

# Load parameters from JSON file
@st.cache_data
def load_parameters():
    param_file = "parameters.json"
    if os.path.exists(param_file):
        with open(param_file, 'r') as f:
            params = json.load(f)
        return params
    else:
        # Default parameters if file doesn't exist
        return {
            "curve_parameters": {
                "a": 0.92,
                "b": 0.023,
                "c": 383
            },
            "culture_bounds": {
                "min": -50,
                "max": 50,
                "default": 0
            },
            "fitted": False
        }

params = load_parameters()

# Display if parameters are fitted from data
if params.get("fitted", False):
    st.info(f"📊 Model parameters fitted from {params['fit_metadata']['n_samples']} data points (RMSE: {params['fit_metadata']['rmse']:.3f})")
else:
    st.info("📊 Using default model parameters")

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

def find_salary_for_probability(target_prob, a, b, c, k=0):
    """
    Find the salary needed to achieve a target recruitment probability
    """
    if target_prob >= a:
        return None
    x = c - k - (1/b) * np.log(a/target_prob - 1)
    return x

st.sidebar.header("Model Parameters")

st.sidebar.markdown("### Curve Parameters")

# Get parameter values from loaded data
curve_params = params["curve_parameters"]
culture_bounds = params["culture_bounds"]

a = st.sidebar.slider(
    "Maximum Probability (a)",
    min_value=0.8,
    max_value=1.0,
    value=curve_params["a"],
    step=0.01,
    help="The maximum achievable recruitment probability"
)

b = st.sidebar.slider(
    "Slope (b)",
    min_value=0.01,
    max_value=0.05,
    value=curve_params["b"],
    step=0.001,
    format="%.3f",
    help="How steeply the probability increases with compensation"
)

c = st.sidebar.slider(
    "Baseline Inflection Point (c)",
    min_value=300,
    max_value=500,
    value=curve_params["c"],
    step=5,
    help="Compensation (in $1000s) at which recruitment probability is 50% of maximum"
)

st.sidebar.markdown("### Culture Factor")
culture_score = st.sidebar.slider(
    "Department Culture Score",
    min_value=int(culture_bounds["min"]),
    max_value=int(culture_bounds["max"]),
    value=int(culture_bounds["default"]),
    step=5,
    help="Positive values make recruitment easier, negative values make it harder. Each point ≈ $1,000 in compensation value."
)

st.sidebar.markdown("### Regional Adjustment")
cost_of_living = st.sidebar.slider(
    "Regional Cost of Living Index",
    min_value=77,
    max_value=231,
    value=100,
    step=1,
    help="Cost of living index relative to national average (100). Manhattan=231, Decatur IL=77"
)

st.sidebar.markdown("### Target Parameters")
target_probability = st.sidebar.slider(
    "Target Recruitment Probability",
    min_value=0.5,
    max_value=0.95,
    value=0.80,
    step=0.05,
    help="Desired probability of successful recruitment"
)

col1, col2 = st.columns([2, 1])

with col1:
    # Apply cost of living adjustment to the x-axis range
    col_adjustment = cost_of_living / 100.0
    x = np.linspace(250, 700, 500)
    
    y_baseline = sigmoid_recruitment(x, a, b, c, k=0)
    y_current = sigmoid_recruitment(x, a, b, c, k=culture_score)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(x, y_baseline, 'r--', label='Baseline (Culture = 0)', linewidth=2, alpha=0.7)
    ax.plot(x, y_current, 'b-', label=f'Current (Culture = {culture_score})', linewidth=3)
    
    if culture_score > 0:
        y_negative = sigmoid_recruitment(x, a, b, c, k=-20)
        ax.plot(x, y_negative, 'g:', label='Poor Culture (-20)', linewidth=2, alpha=0.5)
    elif culture_score < 0:
        y_positive = sigmoid_recruitment(x, a, b, c, k=30)
        ax.plot(x, y_positive, 'g:', label='Strong Culture (+30)', linewidth=2, alpha=0.5)
    
    salary_baseline = find_salary_for_probability(target_probability, a, b, c, k=0)
    salary_current = find_salary_for_probability(target_probability, a, b, c, k=culture_score)
    
    # Apply cost of living adjustment to salaries
    salary_baseline_adjusted = salary_baseline * col_adjustment if salary_baseline else None
    salary_current_adjusted = salary_current * col_adjustment if salary_current else None
    
    if salary_current:
        ax.plot([salary_current, salary_current], [0, target_probability], 'b--', alpha=0.5)
        ax.plot([250, salary_current], [target_probability, target_probability], 'b--', alpha=0.5)
        ax.scatter([salary_current], [target_probability], color='blue', s=100, zorder=5)
    
    ax.set_xlabel('Compensation ($1000s)', fontsize=12)
    ax.set_ylabel('Probability of Recruitment', fontsize=12)
    title = 'Anesthesiology Faculty Recruitment Model'
    if cost_of_living != 100:
        title += f' (National Equivalent - Regional at {cost_of_living}%)'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    ax.set_xlim(250, 700)
    ax.set_ylim(0, 1)
    
    ax2 = ax.twiny()
    ax2.set_xlim(250, 700)
    ax2.set_xticks([300, 400, 500, 600])
    ax2.set_xticklabels(['$300K', '$400K', '$500K', '$600K'])
    ax2.set_xlabel('Annual Compensation', fontsize=12)
    
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("### Recruitment Analysis")
    
    if salary_current_adjusted:
        st.metric(
            "Recommended Salary (Regional)", 
            f"${salary_current_adjusted:.0f},000",
            f"${(salary_current_adjusted - salary_baseline_adjusted):.0f}K vs baseline" if culture_score != 0 else None
        )
        
        if cost_of_living != 100:
            st.markdown(f"**National Equivalent:** ${salary_current:.0f}K")
            st.markdown(f"**Regional Adjustment:** {cost_of_living}% of national")
        
        st.markdown(f"**Target Probability:** {target_probability:.0%}")
        
        if culture_score != 0:
            savings = salary_baseline_adjusted - salary_current_adjusted
            st.markdown(f"**Culture Impact:** ${abs(savings):.0f}K {'savings' if savings > 0 else 'additional cost'}")
    else:
        st.error("Target probability exceeds maximum achievable probability")
    
    st.markdown("### Key Insights")
    
    inflection_salary = c - culture_score
    inflection_salary_adjusted = inflection_salary * col_adjustment
    st.markdown(f"• **50% probability at:** ${inflection_salary_adjusted:.0f}K")
    
    eighty_percent_salary = find_salary_for_probability(0.8, a, b, c, k=culture_score)
    if eighty_percent_salary:
        eighty_adjusted = eighty_percent_salary * col_adjustment
        st.markdown(f"• **80% probability at:** ${eighty_adjusted:.0f}K")
    
    ninety_percent_salary = find_salary_for_probability(0.9, a, b, c, k=culture_score)
    if ninety_percent_salary:
        ninety_adjusted = ninety_percent_salary * col_adjustment
        st.markdown(f"• **90% probability at:** ${ninety_adjusted:.0f}K")

st.markdown("---")

st.markdown("### Understanding the Model")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    #### Compensation Zones
    - **Below $350K:** Very low recruitment probability
    - **$350-450K:** Steep increase in recruitment success
    - **$450-550K:** Diminishing returns begin
    - **Above $550K:** Minimal additional benefit
    """)
    
    st.markdown("""
    #### Culture Score Components
    - **Work-Life Balance** (0-10 points)
    - **Academic Environment** (0-10 points)
    - **Department Reputation** (0-10 points)
    - **Workplace Climate** (0-10 points)
    - **Career Development** (0-10 points)
    """)

with col4:
    st.markdown("""
    #### Strategic Implications
    - Every 10-point culture improvement ≈ $10K salary savings
    - Focus on culture when compensation is constrained
    - Identify point of diminishing returns for your institution
    - Balance direct compensation with culture investments
    """)
    
    st.markdown("""
    #### Model Assumptions
    - Based on Southeast academic medical center data
    - Reflects current competitive market conditions
    - Culture factors are additive and linear
    - Individual preferences may vary
    - Cost of living ranges from 77% (Decatur, IL) to 231% (Manhattan, NY)
    """)

st.markdown("---")
st.markdown("*This is a proof of concept for modeling faculty recruitment. Future versions will incorporate historical data for parameter fitting.*")