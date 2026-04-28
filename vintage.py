"""
Vintage analysis module for credit risk analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from .data_models import LoanData, DelinquencyStatus, VintageMetrics


class VintageAnalysis:
    """
    Analyze loan performance by vintage cohorts.
    
    Vintage analysis groups loans by their origination date (cohort)
    and tracks their performance over time.
    """

    def __init__(self, loans: List[LoanData]):
        """
        Initialize vintage analysis.
        
        Args:
            loans: List of LoanData objects
        """
        self.loans = loans
        self.df = self._prepare_dataframe()

    def _prepare_dataframe(self) -> pd.DataFrame:
        """Convert loan list to DataFrame."""
        data = []
        for loan in self.loans:
            data.append({
                'loan_id': loan.loan_id,
                'origination_date': loan.origination_date,
                'observation_date': loan.observation_date,
                'principal_amount': loan.principal_amount,
                'current_balance': loan.current_balance,
                'delinquency_status': loan.delinquency_status.value,
                'delinquency_days': loan.delinquency_days,
                'payment_amount': loan.payment_amount,
                'interest_rate': loan.interest_rate,
                'loan_term_months': loan.loan_term_months,
                'customer_score': loan.customer_score,
                'loan_purpose': loan.loan_purpose,
                'region': loan.region,
                'vintage_month': loan.vintage_month
            })
        return pd.DataFrame(data)

    def calculate_vintage_metrics(self) -> List[VintageMetrics]:
        """
        Calculate metrics for each vintage cohort.
        
        Returns:
            List of VintageMetrics for each vintage cohort
        """
        metrics_list = []
        
        for vintage in sorted(self.df['vintage_month'].unique()):
            vintage_df = self.df[self.df['vintage_month'] == vintage]
            
            total = len(vintage_df)
            current = len(vintage_df[vintage_df['delinquency_status'] == 'Current'])
            dpd_30 = len(vintage_df[vintage_df['delinquency_status'] == '30+ DPD'])
            dpd_60 = len(vintage_df[vintage_df['delinquency_status'] == '60+ DPD'])
            dpd_90 = len(vintage_df[vintage_df['delinquency_status'] == '90+ DPD'])
            charged_off = len(vintage_df[vintage_df['delinquency_status'] == 'Charged Off'])
            paid_off = len(vintage_df[vintage_df['delinquency_status'] == 'Paid Off'])
            default = len(vintage_df[vintage_df['delinquency_status'] == 'Default'])
            
            delinquent = dpd_30 + dpd_60 + dpd_90
            
            metrics = VintageMetrics(
                vintage_month=int(vintage),
                total_loans=total,
                current_loans=current,
                delinquent_30_loans=dpd_30,
                delinquent_60_loans=dpd_60,
                delinquent_90_loans=dpd_90,
                charged_off_loans=charged_off,
                paid_off_loans=paid_off,
                default_loans=default,
                current_balance_total=vintage_df['current_balance'].sum(),
                delinquency_rate=delinquent / total if total > 0 else 0,
                charge_off_rate=charged_off / total if total > 0 else 0,
                payoff_rate=paid_off / total if total > 0 else 0,
                early_default_rate=default / total if total > 0 else 0,
                average_dpd=vintage_df['delinquency_days'].mean()
            )
            metrics_list.append(metrics)
        
        return metrics_list

    def get_cumulative_loss_evolution(self) -> pd.DataFrame:
        """
        Calculate cumulative loss by vintage over time.
        
        Returns:
            DataFrame with vintage month as index and loss metrics as columns
        """
        metrics_list = self.calculate_vintage_metrics()
        data = []
        
        for m in metrics_list:
            total_losses = (m.charged_off_loans + m.default_loans) * (
                m.current_balance_total / m.total_loans if m.total_loans > 0 else 0
            )
            data.append({
                'vintage_month': m.vintage_month,
                'total_loans': m.total_loans,
                'cumulative_losses': total_losses,
                'charge_off_rate': m.charge_off_rate,
                'delinquency_rate': m.delinquency_rate
            })
        
        return pd.DataFrame(data)

    def get_status_distribution(self) -> pd.DataFrame:
        """
        Get status distribution by vintage.
        
        Returns:
            DataFrame with vintage and status distribution
        """
        metrics_list = self.calculate_vintage_metrics()
        data = []
        
        for m in metrics_list:
            total = m.total_loans if m.total_loans > 0 else 1
            data.append({
                'vintage_month': m.vintage_month,
                'current_pct': (m.current_loans / total) * 100,
                'dpd_30_pct': (m.delinquent_30_loans / total) * 100,
                'dpd_60_pct': (m.delinquent_60_loans / total) * 100,
                'dpd_90_pct': (m.delinquent_90_loans / total) * 100,
                'charged_off_pct': (m.charged_off_loans / total) * 100,
                'paid_off_pct': (m.paid_off_loans / total) * 100,
                'default_pct': (m.default_loans / total) * 100
            })
        
        return pd.DataFrame(data)

    def get_default_probability_curve(self) -> pd.DataFrame:
        """
        Calculate probability of default by vintage age.
        
        Returns:
            DataFrame with vintage age and default probability
        """
        metrics_list = self.calculate_vintage_metrics()
        data = []
        
        for m in metrics_list:
            default_prob = (m.default_loans + m.charged_off_loans) / m.total_loans if m.total_loans > 0 else 0
            data.append({
                'vintage_month': m.vintage_month,
                'default_probability': default_prob,
                'pd_percentage': default_prob * 100
            })
        
        return pd.DataFrame(data)

    def summary_report(self) -> Dict:
        """
        Generate a summary report for all vintages.
        
        Returns:
            Dictionary with summary statistics
        """
        metrics_list = self.calculate_vintage_metrics()
        
        total_issues = sum(m.total_loans for m in metrics_list)
        total_defaults = sum(m.default_loans + m.charged_off_loans for m in metrics_list)
        total_delinquent = sum(m.delinquent_30_loans + m.delinquent_60_loans + m.delinquent_90_loans 
                              for m in metrics_list)
        
        return {
            'total_vintages': len(metrics_list),
            'total_loans_issued': total_issues,
            'total_defaults': total_defaults,
            'portfolio_default_rate': total_defaults / total_issues if total_issues > 0 else 0,
            'total_delinquent': total_delinquent,
            'portfolio_delinquency_rate': total_delinquent / total_issues if total_issues > 0 else 0,
            'average_vintage_default_rate': np.mean([m.early_default_rate for m in metrics_list]),
            'oldest_vintage_month': min([m.vintage_month for m in metrics_list]),
            'newest_vintage_month': max([m.vintage_month for m in metrics_list])
        }
