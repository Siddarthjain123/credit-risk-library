"""
Roll rate analysis module for credit risk analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from .data_models import LoanData, DelinquencyStatus, RollRateMetrics


class RollRateAnalysis:
    """
    Analyze loan roll rates - how loans transition between delinquency states.
    
    Roll rate analysis tracks the movement of loans from one delinquency
    status to another over successive observation periods.
    """

    def __init__(self, loans: List[LoanData]):
        """
        Initialize roll rate analysis.
        
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
                'delinquency_status': loan.delinquency_status,
                'delinquency_days': loan.delinquency_days,
                'principal_amount': loan.principal_amount,
                'current_balance': loan.current_balance
            })
        return pd.DataFrame(data)

    def calculate_monthly_roll_rates(self) -> Dict[str, pd.DataFrame]:
        """
        Calculate roll rates for each observation period.
        
        Returns:
            Dictionary with period as key and roll rate matrix as value
        """
        roll_rates = {}
        
        # Sort by observation date to process chronologically
        sorted_df = self.df.sort_values('observation_date')
        
        # Group by observation date for monthly periods
        for period, period_df in sorted_df.groupby(pd.Grouper(key='observation_date', freq='MS')):
            period_str = period.strftime('%Y-%m')
            
            # Group by loan and get transitions
            transitions = {}
            status_list = [s.value for s in DelinquencyStatus]
            
            # Initialize transition matrix
            transition_matrix = pd.DataFrame(0, index=status_list, columns=status_list)
            
            # Count transitions from previous period
            for loan_id, group in period_df.groupby('loan_id'):
                if len(group) > 1:
                    sorted_group = group.sort_values('observation_date')
                    prev_status = sorted_group.iloc[-2]['delinquency_status'].value
                    curr_status = sorted_group.iloc[-1]['delinquency_status'].value
                    
                    transition_matrix.loc[prev_status, curr_status] += 1
            
            roll_rates[period_str] = transition_matrix
        
        return roll_rates

    def calculate_roll_rates_matrix(self) -> pd.DataFrame:
        """
        Calculate overall roll rates across all periods.
        
        Returns:
            DataFrame showing transition probabilities between states
        """
        status_list = [s.value for s in DelinquencyStatus]
        transition_matrix = pd.DataFrame(0.0, index=status_list, columns=status_list)
        
        sorted_df = self.df.sort_values(['loan_id', 'observation_date'])
        
        for loan_id, group in sorted_df.groupby('loan_id'):
            if len(group) > 1:
                sorted_group = group.sort_values('observation_date')
                for i in range(len(sorted_group) - 1):
                    prev_status = sorted_group.iloc[i]['delinquency_status'].value
                    curr_status = sorted_group.iloc[i + 1]['delinquency_status'].value
                    transition_matrix.loc[prev_status, curr_status] += 1
        
        # Convert to probabilities
        transition_probs = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)
        transition_probs = transition_probs.fillna(0)
        
        return transition_probs

    def get_roll_forward_rates(self) -> Dict[str, float]:
        """
        Calculate roll forward rates (movement to worse delinquency status).
        
        Returns:
            Dictionary with status and corresponding forward roll rate
        """
        transition_probs = self.calculate_roll_rates_matrix()
        forward_rates = {}
        
        # Current -> 30 DPD
        current_roll = transition_probs.loc['Current', '30+ DPD']
        forward_rates['Current to 30+ DPD'] = current_roll
        
        # 30 DPD -> 60 DPD
        dpd30_roll = transition_probs.loc['30+ DPD', '60+ DPD']
        forward_rates['30+ DPD to 60+ DPD'] = dpd30_roll
        
        # 60 DPD -> 90 DPD
        dpd60_roll = transition_probs.loc['60+ DPD', '90+ DPD']
        forward_rates['60+ DPD to 90+ DPD'] = dpd60_roll
        
        # 90 DPD -> Charged Off
        dpd90_roll = transition_probs.loc['90+ DPD', 'Charged Off']
        forward_rates['90+ DPD to Charged Off'] = dpd90_roll
        
        return forward_rates

    def get_roll_back_rates(self) -> Dict[str, float]:
        """
        Calculate roll back rates (improvement in delinquency status).
        
        Returns:
            Dictionary with status and corresponding back roll rate
        """
        transition_probs = self.calculate_roll_rates_matrix()
        back_rates = {}
        
        # 30 DPD -> Current
        dpd30_back = transition_probs.loc['30+ DPD', 'Current']
        back_rates['30+ DPD to Current'] = dpd30_back
        
        # 60 DPD -> Current or 30 DPD
        dpd60_back = transition_probs.loc['60+ DPD', 'Current'] + transition_probs.loc['60+ DPD', '30+ DPD']
        back_rates['60+ DPD to Better'] = dpd60_back
        
        # 90 DPD -> Better
        dpd90_back = transition_probs.loc['90+ DPD', 'Current'] + transition_probs.loc['90+ DPD', '30+ DPD'] + transition_probs.loc['90+ DPD', '60+ DPD']
        back_rates['90+ DPD to Better'] = dpd90_back
        
        return back_rates

    def get_cure_rates(self) -> Dict[str, float]:
        """
        Calculate cure rates (movement from delinquent to current).
        
        Returns:
            Dictionary with delinquency status and cure rate
        """
        transition_probs = self.calculate_roll_rates_matrix()
        cure_rates = {}
        
        cure_rates['30+ DPD Cure Rate'] = transition_probs.loc['30+ DPD', 'Current']
        cure_rates['60+ DPD Cure Rate'] = transition_probs.loc['60+ DPD', 'Current']
        cure_rates['90+ DPD Cure Rate'] = transition_probs.loc['90+ DPD', 'Current']
        
        return cure_rates

    def get_default_rates_by_status(self) -> Dict[str, float]:
        """
        Calculate default rates by delinquency status.
        
        Returns:
            Dictionary with status and default/charge-off rate
        """
        transition_probs = self.calculate_roll_rates_matrix()
        default_rates = {}
        
        default_rates['30+ DPD Default Rate'] = transition_probs.loc['30+ DPD', 'Charged Off'] + transition_probs.loc['30+ DPD', 'Default']
        default_rates['60+ DPD Default Rate'] = transition_probs.loc['60+ DPD', 'Charged Off'] + transition_probs.loc['60+ DPD', 'Default']
        default_rates['90+ DPD Default Rate'] = transition_probs.loc['90+ DPD', 'Charged Off'] + transition_probs.loc['90+ DPD', 'Default']
        
        return default_rates

    def get_stability_analysis(self) -> Dict[str, float]:
        """
        Calculate loan stability by status (probability of staying in same status).
        
        Returns:
            Dictionary with status and stability rate
        """
        transition_probs = self.calculate_roll_rates_matrix()
        stability = {}
        
        for status in transition_probs.index:
            stability[f'{status} Stability'] = transition_probs.loc[status, status]
        
        return stability

    def summary_roll_rate_report(self) -> Dict:
        """
        Generate comprehensive roll rate summary report.
        
        Returns:
            Dictionary with all roll rate metrics
        """
        return {
            'forward_rates': self.get_roll_forward_rates(),
            'back_rates': self.get_roll_back_rates(),
            'cure_rates': self.get_cure_rates(),
            'default_rates': self.get_default_rates_by_status(),
            'stability_rates': self.get_stability_analysis()
        }
