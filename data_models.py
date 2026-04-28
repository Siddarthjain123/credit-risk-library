"""
Data models for credit risk analysis.
"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional


class DelinquencyStatus(Enum):
    """Delinquency status categories."""
    CURRENT = "Current"
    DPD_30 = "30+ DPD"
    DPD_60 = "60+ DPD"
    DPD_90 = "90+ DPD"
    CHARGED_OFF = "Charged Off"
    PAID_OFF = "Paid Off"
    DEFAULT = "Default"


@dataclass
class LoanData:
    """
    Data model representing loan information for credit risk analysis.
    
    Attributes:
        loan_id (str): Unique identifier for the loan
        origination_date (datetime): Date when the loan was originated
        observation_date (datetime): Date of observation/snapshot
        principal_amount (float): Original loan principal amount
        current_balance (float): Current outstanding balance
        delinquency_status (DelinquencyStatus): Current delinquency status
        delinquency_days (int): Number of days past due
        payment_amount (float): Monthly payment amount
        interest_rate (float): Loan interest rate (%)
        loan_term_months (int): Total loan term in months
        customer_score (int): Credit score at origination
        loan_purpose (str): Purpose of the loan
        region (str): Geographic region
        vintage_month (int): Vintage cohort (months since origination)
    """
    loan_id: str
    origination_date: datetime
    observation_date: datetime
    principal_amount: float
    current_balance: float
    delinquency_status: DelinquencyStatus
    delinquency_days: int = 0
    payment_amount: float = 0.0
    interest_rate: float = 0.0
    loan_term_months: int = 60
    customer_score: int = 700
    loan_purpose: str = "Personal"
    region: str = "Unknown"
    vintage_month: Optional[int] = None

    def __post_init__(self):
        """Calculate vintage month if not provided."""
        if self.vintage_month is None:
            delta = (self.observation_date - self.origination_date).days
            self.vintage_month = delta // 30


@dataclass
class VintageMetrics:
    """Metrics calculated for a vintage cohort."""
    vintage_month: int
    total_loans: int
    current_loans: int
    delinquent_30_loans: int
    delinquent_60_loans: int
    delinquent_90_loans: int
    charged_off_loans: int
    paid_off_loans: int
    default_loans: int
    current_balance_total: float
    delinquency_rate: float
    charge_off_rate: float
    payoff_rate: float
    early_default_rate: float
    average_dpd: float


@dataclass
class RollRateMetrics:
    """Metrics for roll rate analysis."""
    period: str
    status_from: DelinquencyStatus
    status_to: DelinquencyStatus
    count: int
    percentage: float
