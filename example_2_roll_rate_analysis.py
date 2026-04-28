"""
Example 2: Roll Rate Analysis
Demonstrates how to use the RollRateAnalysis class to analyze loan transitions.
"""

from credit_risk import RollRateAnalysis, VintageAnalysis
from credit_risk.utils import generate_sample_loans
from credit_risk.visualizer import CreditRiskVisualizer

# Generate sample data
print("Generating sample loan data...")
loans = generate_sample_loans(num_loans=1000, num_vintages=12)

# Create roll rate analysis
print("Creating roll rate analysis...")
roll_rate_analysis = RollRateAnalysis(loans)

# Get roll rate matrix
print("\n=== Roll Rate Transition Matrix ===")
transition_matrix = roll_rate_analysis.calculate_roll_rates_matrix()
print(transition_matrix.round(4))

# Get forward roll rates
forward_rates = roll_rate_analysis.get_roll_forward_rates()
print("\n=== Forward Roll Rates (Deterioration) ===")
for status, rate in forward_rates.items():
    print(f"{status}: {rate:.2%}")

# Get cure rates
cure_rates = roll_rate_analysis.get_cure_rates()
print("\n=== Cure Rates (Improvement) ===")
for status, rate in cure_rates.items():
    print(f"{status}: {rate:.2%}")

# Get default rates
default_rates = roll_rate_analysis.get_default_rates_by_status()
print("\n=== Default Rates by Status ===")
for status, rate in default_rates.items():
    print(f"{status}: {rate:.2%}")

# Get stability rates
stability_rates = roll_rate_analysis.get_stability_analysis()
print("\n=== Stability Rates (Stay in Same Status) ===")
for status, rate in stability_rates.items():
    print(f"{status}: {rate:.2%}")

# Create visualizer
visualizer = CreditRiskVisualizer()

# Plot roll rate heatmap
print("\n=== Plotting Roll Rate Heatmap ===")
visualizer.plot_roll_rate_heatmap(roll_rate_analysis)

# Plot forward roll rates
print("\n=== Plotting Forward Roll Rates ===")
visualizer.plot_forward_roll_rates(roll_rate_analysis)

# Plot cure rates
print("\n=== Plotting Cure Rates ===")
visualizer.plot_cure_rates(roll_rate_analysis)

# Plot default rates
print("\n=== Plotting Default Rates by Status ===")
visualizer.plot_default_rates_by_status(roll_rate_analysis)

print("\nExample 2 Complete!")
