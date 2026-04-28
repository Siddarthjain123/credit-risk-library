"""
Example 1: Basic Vintage Analysis
Demonstrates how to use the VintageAnalysis class to analyze loan performance by cohort.
"""

from credit_risk import VintageAnalysis, DelinquencyStatus, LoanData
from credit_risk.utils import generate_sample_loans
from credit_risk.visualizer import CreditRiskVisualizer
from datetime import datetime

# Generate sample data
print("Generating sample loan data...")
loans = generate_sample_loans(num_loans=1000, num_vintages=12)

# Create vintage analysis
print("Creating vintage analysis...")
vintage_analysis = VintageAnalysis(loans)

# Get summary report
summary = vintage_analysis.summary_report()
print("\n=== Portfolio Summary ===")
print(f"Total Vintages: {summary['total_vintages']}")
print(f"Total Loans Issued: {summary['total_loans_issued']}")
print(f"Portfolio Default Rate: {summary['portfolio_default_rate']:.2%}")
print(f"Portfolio Delinquency Rate: {summary['portfolio_delinquency_rate']:.2%}")
print(f"Average Vintage Default Rate: {summary['average_vintage_default_rate']:.2%}")

# Get detailed metrics
metrics = vintage_analysis.calculate_vintage_metrics()
print("\n=== Vintage Metrics (First 3) ===")
for m in metrics[:3]:
    print(f"\nVintage {m.vintage_month}:")
    print(f"  Total Loans: {m.total_loans}")
    print(f"  Current: {m.current_loans} ({m.current_loans/m.total_loans:.1%})")
    print(f"  Delinquent: {m.delinquent_30_loans + m.delinquent_60_loans + m.delinquent_90_loans} ({m.delinquency_rate:.1%})")
    print(f"  Charged Off: {m.charged_off_loans} ({m.charge_off_rate:.1%})")
    print(f"  Paid Off: {m.paid_off_loans} ({m.payoff_rate:.1%})")

# Create visualizer
visualizer = CreditRiskVisualizer()

# Plot vintage delinquency rates
print("\n=== Plotting Vintage Delinquency and Charge-off Rates ===")
visualizer.plot_vintage_delinquency_rates(vintage_analysis)

# Plot status distribution
print("\n=== Plotting Status Distribution ===")
visualizer.plot_vintage_status_distribution(vintage_analysis)

# Plot default probability
print("\n=== Plotting Default Probability Curve ===")
visualizer.plot_default_probability_curve(vintage_analysis)

print("\nExample 1 Complete!")
