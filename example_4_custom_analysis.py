"""
Example 4: Custom Analysis
Demonstrates how to perform custom analysis with the library.
"""

from credit_risk import VintageAnalysis, RollRateAnalysis, LoanData, DelinquencyStatus
from credit_risk.utils import generate_sample_loans, export_analytics_to_excel
from datetime import datetime
import pandas as pd

# Generate sample data
print("Generating sample loan data...")
loans = generate_sample_loans(num_loans=1000, num_vintages=12)

# Create analyses
vintage_analysis = VintageAnalysis(loans)
roll_rate_analysis = RollRateAnalysis(loans)

# Example 1: Analyze loans by specific characteristics
print("\n=== Analyzing High-Risk Loans ===")
high_risk_loans = [
    loan for loan in loans 
    if loan.delinquency_days >= 60
]
print(f"Loans with 60+ DPD: {len(high_risk_loans)}")

high_risk_balance = sum(loan.current_balance for loan in high_risk_loans)
total_balance = sum(loan.current_balance for loan in loans)
print(f"High-risk balance: ${high_risk_balance:,.2f} ({high_risk_balance/total_balance:.1%} of portfolio)")

# Example 2: Analyze by loan purpose
print("\n=== Analysis by Loan Purpose ===")
purposes = set(loan.loan_purpose for loan in loans)
for purpose in purposes:
    purpose_loans = [l for l in loans if l.loan_purpose == purpose]
    delinquent = sum(1 for l in purpose_loans if l.delinquency_days > 0)
    print(f"{purpose}: {len(purpose_loans)} loans, {delinquent} delinquent ({delinquent/len(purpose_loans):.1%})")

# Example 3: Analyze by region
print("\n=== Analysis by Region ===")
regions = set(loan.region for loan in loans)
for region in regions:
    region_loans = [l for l in loans if l.region == region]
    delinquent = sum(1 for l in region_loans if l.delinquency_days > 0)
    avg_score = sum(l.customer_score for l in region_loans) / len(region_loans)
    print(f"{region}: {len(region_loans)} loans, Delinquency: {delinquent/len(region_loans):.1%}, Avg Score: {avg_score:.0f}")

# Example 4: Get status transitions
print("\n=== Most Common Transitions ===")
transition_matrix = roll_rate_analysis.calculate_roll_rates_matrix()
transition_matrix_sorted = transition_matrix.stack().sort_values(ascending=False)
for (from_status, to_status), prob in transition_matrix_sorted.head(10).items():
    if prob > 0:
        print(f"{from_status} → {to_status}: {prob:.2%}")

# Example 5: Export to Excel
print("\n=== Exporting to Excel ===")
try:
    output_file = '/Users/siddarthjain/credit_risk_lib/credit_risk_analysis.xlsx'
    export_analytics_to_excel(vintage_analysis, roll_rate_analysis, output_file)
    print(f"Analysis exported to: {output_file}")
except Exception as e:
    print(f"Note: Excel export requires openpyxl. Error: {e}")

# Example 6: Analyze vintage aging
print("\n=== Vintage Age Analysis ===")
metrics = vintage_analysis.calculate_vintage_metrics()
for m in sorted(metrics, key=lambda x: x.vintage_month)[:5]:
    print(f"Vintage {m.vintage_month}: {m.total_loans} loans, PD: {m.early_default_rate:.2%}, RR: {m.delinquency_rate:.2%}")

print("\nExample 4 Complete!")
