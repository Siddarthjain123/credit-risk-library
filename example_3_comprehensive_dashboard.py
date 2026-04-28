"""
Example 3: Comprehensive Dashboard
Demonstrates creating a comprehensive dashboard with all metrics.
"""

from credit_risk import VintageAnalysis, RollRateAnalysis
from credit_risk.utils import (
    generate_sample_loans, 
    calculate_concentration_risk,
    calculate_portfolio_statistics
)
from credit_risk.visualizer import CreditRiskVisualizer

# Generate sample data
print("Generating sample loan data...")
loans = generate_sample_loans(num_loans=1000, num_vintages=12)

# Create analyses
print("Creating analyses...")
vintage_analysis = VintageAnalysis(loans)
roll_rate_analysis = RollRateAnalysis(loans)

# Calculate portfolio statistics
portfolio_stats = calculate_portfolio_statistics(loans)
print("\n=== Portfolio Statistics ===")
print(f"Total Loans: {portfolio_stats['total_loans']}")
print(f"Total Principal: ${portfolio_stats['total_principal']:,.2f}")
print(f"Total Current Balance: ${portfolio_stats['total_balance']:,.2f}")
print(f"Average Loan Size: ${portfolio_stats['avg_loan_size']:,.2f}")
print(f"Average Credit Score: {portfolio_stats['avg_credit_score']:.0f}")
print(f"Average Interest Rate: {portfolio_stats['avg_interest_rate']:.2f}%")
print(f"Average Days Past Due: {portfolio_stats['avg_dpd']:.1f}")

# Calculate concentration risk
concentration = calculate_concentration_risk(loans)
print("\n=== Concentration Risk ===")
print(f"Purpose HHI: {concentration['purpose_hhi']:.4f}")
print(f"Region HHI: {concentration['region_hhi']:.4f}")
print("\nBy Purpose:")
for purpose, pct in concentration['by_purpose'].items():
    print(f"  {purpose}: {pct:.1%}")
print("\nBy Region:")
for region, pct in concentration['by_region'].items():
    print(f"  {region}: {pct:.1%}")

# Get vintage summary
vintage_summary = vintage_analysis.summary_report()
print("\n=== Vintage Analysis Summary ===")
print(f"Portfolio Default Rate: {vintage_summary['portfolio_default_rate']:.2%}")
print(f"Portfolio Delinquency Rate: {vintage_summary['portfolio_delinquency_rate']:.2%}")
print(f"Oldest Vintage: {vintage_summary['oldest_vintage_month']} months")
print(f"Newest Vintage: {vintage_summary['newest_vintage_month']} months")

# Get roll rate summary
roll_rate_summary = roll_rate_analysis.summary_roll_rate_report()
print("\n=== Roll Rate Summary ===")
print("\nForward Roll Rates:")
for status, rate in roll_rate_summary['forward_rates'].items():
    print(f"  {status}: {rate:.2%}")

# Create visualizer and plot dashboard
visualizer = CreditRiskVisualizer()
print("\n=== Creating Comprehensive Dashboard ===")
visualizer.plot_comprehensive_dashboard(vintage_analysis, roll_rate_analysis)

print("\nExample 3 Complete!")
