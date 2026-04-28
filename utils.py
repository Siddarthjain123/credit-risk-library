"""
Utility functions for credit risk analysis.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple
from .data_models import LoanData, DelinquencyStatus
import random


def generate_sample_loans(num_loans: int = 1000, 
                         num_vintages: int = 12) -> List[LoanData]:
    """
    Generate sample loan data for testing and demonstration.
    
    Args:
        num_loans: Number of loans to generate
        num_vintages: Number of vintage cohorts
    
    Returns:
        List of LoanData objects
    """
    loans = []
    observation_date = datetime.now()
    
    for i in range(num_loans):
        vintage_month = random.randint(-num_vintages, 0)
        origination_date = observation_date + timedelta(days=vintage_month * 30)
        
        principal = random.uniform(5000, 50000)
        delinquency_days = random.choices(
            [0, 30, 60, 90, 180],
            weights=[0.70, 0.15, 0.08, 0.05, 0.02]
        )[0]
        
        if delinquency_days == 0:
            status = DelinquencyStatus.CURRENT
        elif delinquency_days < 60:
            status = DelinquencyStatus.DPD_30
        elif delinquency_days < 90:
            status = DelinquencyStatus.DPD_60
        elif delinquency_days < 180:
            status = DelinquencyStatus.DPD_90
        else:
            status = random.choice([DelinquencyStatus.CHARGED_OFF, DelinquencyStatus.DEFAULT])
        
        loan = LoanData(
            loan_id=f'LOAN_{i:06d}',
            origination_date=origination_date,
            observation_date=observation_date,
            principal_amount=principal,
            current_balance=principal * random.uniform(0.5, 0.95),
            delinquency_status=status,
            delinquency_days=delinquency_days,
            payment_amount=principal / 60 * 1.05,
            interest_rate=random.uniform(5, 20),
            loan_term_months=random.choice([36, 48, 60, 72]),
            customer_score=random.randint(600, 800),
            loan_purpose=random.choice(['Personal', 'Auto', 'Home']),
            region=random.choice(['North', 'South', 'East', 'West'])
        )
        loans.append(loan)
    
    return loans


def export_analytics_to_excel(vintage_analysis, 
                              roll_rate_analysis,
                              filepath: str) -> None:
    """
    Export all analytics to Excel file.
    
    Args:
        vintage_analysis: VintageAnalysis instance
        roll_rate_analysis: RollRateAnalysis instance
        filepath: Output file path
    """
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Vintage metrics
        vintage_df = vintage_analysis.get_cumulative_loss_evolution()
        vintage_df.to_excel(writer, sheet_name='Vintage Metrics', index=False)
        
        # Status distribution
        status_df = vintage_analysis.get_status_distribution()
        status_df.to_excel(writer, sheet_name='Status Distribution', index=False)
        
        # Default probability
        pd_df = vintage_analysis.get_default_probability_curve()
        pd_df.to_excel(writer, sheet_name='Default Probability', index=False)
        
        # Roll rate matrix
        roll_matrix = roll_rate_analysis.calculate_roll_rates_matrix()
        roll_matrix.to_excel(writer, sheet_name='Roll Rate Matrix')
        
        # Summary statistics
        vintage_summary = vintage_analysis.summary_report()
        summary_df = pd.DataFrame(list(vintage_summary.items()), 
                                 columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)


def calculate_concentration_risk(loans: List[LoanData]) -> dict:
    """
    Calculate concentration risk metrics.
    
    Args:
        loans: List of LoanData objects
    
    Returns:
        Dictionary with concentration metrics
    """
    df = pd.DataFrame([
        {
            'loan_purpose': loan.loan_purpose,
            'region': loan.region,
            'current_balance': loan.current_balance
        }
        for loan in loans
    ])
    
    total_balance = df['current_balance'].sum()
    
    purpose_concentration = (df.groupby('loan_purpose')['current_balance'].sum() / total_balance)
    region_concentration = (df.groupby('region')['current_balance'].sum() / total_balance)
    
    return {
        'by_purpose': purpose_concentration.to_dict(),
        'by_region': region_concentration.to_dict(),
        'purpose_hhi': (purpose_concentration ** 2).sum(),  # Herfindahl index
        'region_hhi': (region_concentration ** 2).sum()
    }


def calculate_portfolio_statistics(loans: List[LoanData]) -> dict:
    """
    Calculate overall portfolio statistics.
    
    Args:
        loans: List of LoanData objects
    
    Returns:
        Dictionary with portfolio statistics
    """
    df = pd.DataFrame([
        {
            'principal': loan.principal_amount,
            'current_balance': loan.current_balance,
            'dpd': loan.delinquency_days,
            'score': loan.customer_score,
            'rate': loan.interest_rate
        }
        for loan in loans
    ])
    
    return {
        'total_loans': len(df),
        'total_principal': df['principal'].sum(),
        'total_balance': df['current_balance'].sum(),
        'avg_loan_size': df['current_balance'].mean(),
        'avg_credit_score': df['score'].mean(),
        'avg_interest_rate': df['rate'].mean(),
        'avg_dpd': df['dpd'].mean(),
        'max_balance': df['current_balance'].max(),
        'min_balance': df['current_balance'].min()
    }
