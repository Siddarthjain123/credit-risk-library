# Credit Risk Library - API Documentation

## Table of Contents
1. [Data Models](#data-models)
2. [Vintage Analysis](#vintage-analysis)
3. [Roll Rate Analysis](#roll-rate-analysis)
4. [Visualizer](#visualizer)
5. [Utilities](#utilities)

---

## Data Models

### DelinquencyStatus (Enum)
Status categories for loans.

```python
class DelinquencyStatus(Enum):
    CURRENT = "Current"              # Loan is current
    DPD_30 = "30+ DPD"              # 30-59 days past due
    DPD_60 = "60+ DPD"              # 60-89 days past due
    DPD_90 = "90+ DPD"              # 90+ days past due
    CHARGED_OFF = "Charged Off"      # Loan written off
    PAID_OFF = "Paid Off"           # Loan fully repaid
    DEFAULT = "Default"             # Loan in default
```

### LoanData (Dataclass)
Represents a single loan record.

**Parameters:**
- `loan_id` (str): Unique identifier for the loan
- `origination_date` (datetime): Date when the loan was originated
- `observation_date` (datetime): Date of observation/snapshot
- `principal_amount` (float): Original loan principal amount
- `current_balance` (float): Current outstanding balance
- `delinquency_status` (DelinquencyStatus): Current delinquency status
- `delinquency_days` (int): Number of days past due (default: 0)
- `payment_amount` (float): Monthly payment amount (default: 0.0)
- `interest_rate` (float): Loan interest rate % (default: 0.0)
- `loan_term_months` (int): Total loan term in months (default: 60)
- `customer_score` (int): Credit score at origination (default: 700)
- `loan_purpose` (str): Purpose of the loan (default: "Personal")
- `region` (str): Geographic region (default: "Unknown")
- `vintage_month` (int, optional): Vintage cohort calculated automatically

### VintageMetrics (Dataclass)
Aggregated metrics for a vintage cohort.

**Attributes:**
- `vintage_month` (int): Months since origination
- `total_loans` (int): Total loans in vintage
- `current_loans` (int): Number of current loans
- `delinquent_30_loans` (int): 30+ DPD loans
- `delinquent_60_loans` (int): 60+ DPD loans
- `delinquent_90_loans` (int): 90+ DPD loans
- `charged_off_loans` (int): Charged off loans
- `paid_off_loans` (int): Paid off loans
- `default_loans` (int): Defaulted loans
- `current_balance_total` (float): Total current balance
- `delinquency_rate` (float): % of delinquent loans
- `charge_off_rate` (float): % of charged off loans
- `payoff_rate` (float): % of paid off loans
- `early_default_rate` (float): % of defaults
- `average_dpd` (float): Mean days past due

---

## Vintage Analysis

### VintageAnalysis Class

Analyze loan performance by origination cohort.

#### Constructor
```python
vintage = VintageAnalysis(loans: List[LoanData])
```

#### Methods

##### calculate_vintage_metrics()
Calculate detailed metrics for each vintage cohort.

```python
metrics: List[VintageMetrics] = vintage.calculate_vintage_metrics()
```

Returns a list of VintageMetrics, one per vintage cohort.

**Example:**
```python
for m in metrics:
    print(f"Vintage {m.vintage_month}: {m.delinquency_rate:.1%} delinquent")
```

---

##### get_cumulative_loss_evolution()
Track cumulative loss by vintage over time.

```python
df: pd.DataFrame = vintage.get_cumulative_loss_evolution()
```

**Returns DataFrame with columns:**
- `vintage_month`: Vintage cohort
- `total_loans`: Count of loans
- `cumulative_losses`: Total loss amount
- `charge_off_rate`: % of charged offs
- `delinquency_rate`: % delinquent

---

##### get_status_distribution()
Get status breakdown by vintage.

```python
df: pd.DataFrame = vintage.get_status_distribution()
```

**Returns DataFrame with columns:**
- `vintage_month`: Vintage cohort
- `current_pct`: % Current
- `dpd_30_pct`: % 30+ DPD
- `dpd_60_pct`: % 60+ DPD
- `dpd_90_pct`: % 90+ DPD
- `charged_off_pct`: % Charged Off
- `paid_off_pct`: % Paid Off
- `default_pct`: % Default

---

##### get_default_probability_curve()
Calculate probability of default by vintage age.

```python
df: pd.DataFrame = vintage.get_default_probability_curve()
```

**Returns DataFrame with columns:**
- `vintage_month`: Vintage age
- `default_probability`: PD as decimal
- `pd_percentage`: PD as percentage

---

##### summary_report()
Generate comprehensive vintage summary.

```python
report: Dict = vintage.summary_report()
```

**Returns Dictionary with keys:**
- `total_vintages`: Number of vintage cohorts
- `total_loans_issued`: Total loans
- `total_defaults`: Loans in default/charged off
- `portfolio_default_rate`: Overall default %
- `total_delinquent`: Delinquent loan count
- `portfolio_delinquency_rate`: Overall delinquency %
- `average_vintage_default_rate`: Mean vintage PD
- `oldest_vintage_month`: Age of oldest vintage
- `newest_vintage_month`: Age of newest vintage

---

## Roll Rate Analysis

### RollRateAnalysis Class

Analyze loan transitions between delinquency states.

#### Constructor
```python
roll_rates = RollRateAnalysis(loans: List[LoanData])
```

#### Methods

##### calculate_roll_rates_matrix()
Calculate transition probability matrix between states.

```python
matrix: pd.DataFrame = roll_rates.calculate_roll_rates_matrix()
```

Returns a matrix where:
- Index: FROM status
- Columns: TO status
- Values: Transition probability

**Example:**
```python
# Probability of Current → 30+ DPD
prob = matrix.loc['Current', '30+ DPD']
```

---

##### get_roll_forward_rates()
Calculate forward roll rates (deterioration).

```python
rates: Dict[str, float] = roll_rates.get_roll_forward_rates()
```

**Returns Dictionary with keys:**
- `'Current to 30+ DPD'`: Probability
- `'30+ DPD to 60+ DPD'`: Probability
- `'60+ DPD to 90+ DPD'`: Probability
- `'90+ DPD to Charged Off'`: Probability

---

##### get_roll_back_rates()
Calculate backward roll rates (improvement).

```python
rates: Dict[str, float] = roll_rates.get_roll_back_rates()
```

**Returns Dictionary with keys:**
- `'30+ DPD to Current'`: Probability
- `'60+ DPD to Better'`: Probability
- `'90+ DPD to Better'`: Probability

---

##### get_cure_rates()
Calculate cure rates (return to Current).

```python
rates: Dict[str, float] = roll_rates.get_cure_rates()
```

**Returns Dictionary with keys:**
- `'30+ DPD Cure Rate'`: Probability
- `'60+ DPD Cure Rate'`: Probability
- `'90+ DPD Cure Rate'`: Probability

---

##### get_default_rates_by_status()
Calculate default rates by delinquency status.

```python
rates: Dict[str, float] = roll_rates.get_default_rates_by_status()
```

**Returns Dictionary with keys:**
- `'30+ DPD Default Rate'`: Probability
- `'60+ DPD Default Rate'`: Probability
- `'90+ DPD Default Rate'`: Probability

---

##### get_stability_analysis()
Calculate probability of staying in same status.

```python
rates: Dict[str, float] = roll_rates.get_stability_analysis()
```

**Returns Dictionary with keys:**
- `'{Status} Stability'`: Probability for each status

---

##### summary_roll_rate_report()
Generate comprehensive roll rate summary.

```python
report: Dict = roll_rates.summary_roll_rate_report()
```

**Returns Dictionary with keys:**
- `forward_rates`: Dictionary of forward roll rates
- `back_rates`: Dictionary of backward roll rates
- `cure_rates`: Dictionary of cure rates
- `default_rates`: Dictionary of default rates
- `stability_rates`: Dictionary of stability rates

---

## Visualizer

### CreditRiskVisualizer Class

Create visualizations for credit risk analysis.

#### Constructor
```python
viz = CreditRiskVisualizer(style: str = 'seaborn-v0_8-darkgrid')
```

#### Methods

##### plot_vintage_delinquency_rates()
Plot delinquency and charge-off rates by vintage.

```python
viz.plot_vintage_delinquency_rates(
    vintage_analysis: VintageAnalysis,
    figsize: tuple = (12, 6)
)
```

**Output:** Two-panel chart showing:
- Left: Delinquency rate trend
- Right: Charge-off rate trend

---

##### plot_vintage_status_distribution()
Plot status distribution stacked area chart.

```python
viz.plot_vintage_status_distribution(
    vintage_analysis: VintageAnalysis,
    figsize: tuple = (14, 6)
)
```

---

##### plot_default_probability_curve()
Plot probability of default curve.

```python
viz.plot_default_probability_curve(
    vintage_analysis: VintageAnalysis,
    figsize: tuple = (10, 6)
)
```

---

##### plot_roll_rate_heatmap()
Plot transition matrix as heatmap.

```python
viz.plot_roll_rate_heatmap(
    roll_rate_analysis: RollRateAnalysis,
    figsize: tuple = (10, 8)
)
```

---

##### plot_forward_roll_rates()
Plot forward roll rates as bar chart.

```python
viz.plot_forward_roll_rates(
    roll_rate_analysis: RollRateAnalysis,
    figsize: tuple = (10, 6)
)
```

---

##### plot_cure_rates()
Plot cure rates as bar chart.

```python
viz.plot_cure_rates(
    roll_rate_analysis: RollRateAnalysis,
    figsize: tuple = (10, 6)
)
```

---

##### plot_default_rates_by_status()
Plot default rates as bar chart.

```python
viz.plot_default_rates_by_status(
    roll_rate_analysis: RollRateAnalysis,
    figsize: tuple = (10, 6)
)
```

---

##### plot_comprehensive_dashboard()
Plot multi-panel dashboard with all metrics.

```python
viz.plot_comprehensive_dashboard(
    vintage_analysis: VintageAnalysis,
    roll_rate_analysis: RollRateAnalysis
)
```

Creates a 3x3 dashboard with:
- Delinquency rate trend
- Charge-off rate trend
- Loans issued by vintage
- Status distribution
- Forward roll rates
- Cure rates
- Default rates

---

## Utilities

### Utility Functions

##### generate_sample_loans()
Generate sample loan data for testing.

```python
loans: List[LoanData] = generate_sample_loans(
    num_loans: int = 1000,
    num_vintages: int = 12
)
```

**Returns:** List of LoanData objects with realistic distributions.

---

##### export_analytics_to_excel()
Export all analytics to Excel file.

```python
export_analytics_to_excel(
    vintage_analysis: VintageAnalysis,
    roll_rate_analysis: RollRateAnalysis,
    filepath: str
)
```

**Creates Excel with sheets:**
- Vintage Metrics
- Status Distribution
- Default Probability
- Roll Rate Matrix
- Summary

---

##### calculate_concentration_risk()
Calculate concentration risk by product and geography.

```python
risk: Dict = calculate_concentration_risk(loans: List[LoanData])
```

**Returns Dictionary with:**
- `by_purpose`: Concentration by loan purpose
- `by_region`: Concentration by region
- `purpose_hhi`: Herfindahl index for purposes
- `region_hhi`: Herfindahl index for regions

---

##### calculate_portfolio_statistics()
Calculate overall portfolio statistics.

```python
stats: Dict = calculate_portfolio_statistics(loans: List[LoanData])
```

**Returns Dictionary with keys:**
- `total_loans`: Count
- `total_principal`: Sum of principal
- `total_balance`: Sum of current balance
- `avg_loan_size`: Average balance
- `avg_credit_score`: Mean score
- `avg_interest_rate`: Mean rate
- `avg_dpd`: Mean days past due
- `max_balance`: Maximum balance
- `min_balance`: Minimum balance

---

## Typical Workflow

```python
from credit_risk import VintageAnalysis, RollRateAnalysis
from credit_risk.visualizer import CreditRiskVisualizer
from credit_risk.utils import calculate_portfolio_statistics

# 1. Load or generate loans
loans = load_loans_from_database()  # or generate_sample_loans()

# 2. Create analyses
vintage = VintageAnalysis(loans)
roll_rate = RollRateAnalysis(loans)

# 3. Get metrics
vintage_summary = vintage.summary_report()
roll_rate_summary = roll_rate.summary_roll_rate_report()
portfolio_stats = calculate_portfolio_statistics(loans)

# 4. Visualize
viz = CreditRiskVisualizer()
viz.plot_comprehensive_dashboard(vintage, roll_rate)

# 5. Export if needed
export_analytics_to_excel(vintage, roll_rate, 'output.xlsx')
```

