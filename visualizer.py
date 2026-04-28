"""
Visualization module for credit risk analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List
from .vintage import VintageAnalysis
from .roll_rate import RollRateAnalysis


class CreditRiskVisualizer:
    """
    Create visualizations for credit risk analysis.
    """

    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize visualizer.
        
        Args:
            style: Matplotlib style to use
        """
        sns.set_style("whitegrid")
        self.colors = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db', '#9b59b6']

    def plot_vintage_delinquency_rates(self, vintage_analysis: VintageAnalysis, 
                                       figsize: tuple = (12, 6)) -> None:
        """
        Plot delinquency rates by vintage.
        
        Args:
            vintage_analysis: VintageAnalysis instance
            figsize: Figure size
        """
        df = vintage_analysis.get_cumulative_loss_evolution()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Delinquency rate
        ax1.plot(df['vintage_month'], df['delinquency_rate'] * 100, 
                marker='o', linewidth=2, markersize=8, color='#e74c3c')
        ax1.fill_between(df['vintage_month'], df['delinquency_rate'] * 100, 
                         alpha=0.3, color='#e74c3c')
        ax1.set_xlabel('Vintage Month', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Delinquency Rate (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Delinquency Rate by Vintage', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Charge-off rate
        ax2.plot(df['vintage_month'], df['charge_off_rate'] * 100, 
                marker='s', linewidth=2, markersize=8, color='#c0392b')
        ax2.fill_between(df['vintage_month'], df['charge_off_rate'] * 100, 
                         alpha=0.3, color='#c0392b')
        ax2.set_xlabel('Vintage Month', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Charge-off Rate (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Charge-off Rate by Vintage', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    def plot_vintage_status_distribution(self, vintage_analysis: VintageAnalysis,
                                        figsize: tuple = (14, 6)) -> None:
        """
        Plot status distribution by vintage as stacked area.
        
        Args:
            vintage_analysis: VintageAnalysis instance
            figsize: Figure size
        """
        df = vintage_analysis.get_status_distribution()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        status_cols = ['current_pct', 'dpd_30_pct', 'dpd_60_pct', 'dpd_90_pct', 
                       'charged_off_pct', 'paid_off_pct', 'default_pct']
        labels = ['Current', '30+ DPD', '60+ DPD', '90+ DPD', 'Charged Off', 'Paid Off', 'Default']
        
        ax.stackplot(df['vintage_month'], 
                    *[df[col] for col in status_cols],
                    labels=labels, alpha=0.8)
        
        ax.set_xlabel('Vintage Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
        ax.set_title('Loan Status Distribution by Vintage (Stacked Area)', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()

    def plot_default_probability_curve(self, vintage_analysis: VintageAnalysis,
                                      figsize: tuple = (10, 6)) -> None:
        """
        Plot default probability curve by vintage.
        
        Args:
            vintage_analysis: VintageAnalysis instance
            figsize: Figure size
        """
        df = vintage_analysis.get_default_probability_curve()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(df['vintage_month'], df['pd_percentage'], 
               marker='D', linewidth=2.5, markersize=8, color='#8e44ad', label='PD')
        ax.fill_between(df['vintage_month'], df['pd_percentage'], 
                        alpha=0.2, color='#8e44ad')
        
        ax.set_xlabel('Vintage Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Probability of Default (%)', fontsize=11, fontweight='bold')
        ax.set_title('Probability of Default by Vintage', fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    def plot_roll_rate_heatmap(self, roll_rate_analysis: RollRateAnalysis,
                               figsize: tuple = (10, 8)) -> None:
        """
        Plot roll rate transition matrix as heatmap.
        
        Args:
            roll_rate_analysis: RollRateAnalysis instance
            figsize: Figure size
        """
        transition_probs = roll_rate_analysis.calculate_roll_rates_matrix()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.heatmap(transition_probs, annot=True, fmt='.2%', cmap='RdYlGn_r', 
                   cbar_kws={'label': 'Transition Probability'}, ax=ax, 
                   linewidths=0.5, linecolor='gray')
        
        ax.set_title('Roll Rate Transition Matrix', fontsize=12, fontweight='bold')
        ax.set_xlabel('To Status', fontsize=11, fontweight='bold')
        ax.set_ylabel('From Status', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.show()

    def plot_forward_roll_rates(self, roll_rate_analysis: RollRateAnalysis,
                               figsize: tuple = (10, 6)) -> None:
        """
        Plot forward roll rates (deterioration).
        
        Args:
            roll_rate_analysis: RollRateAnalysis instance
            figsize: Figure size
        """
        forward_rates = roll_rate_analysis.get_roll_forward_rates()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        labels = list(forward_rates.keys())
        values = [v * 100 for v in forward_rates.values()]
        
        bars = ax.barh(labels, values, color='#e74c3c', alpha=0.8, edgecolor='#c0392b', linewidth=1.5)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 0.5, i, f'{val:.2f}%', va='center', fontweight='bold')
        
        ax.set_xlabel('Roll Forward Rate (%)', fontsize=11, fontweight='bold')
        ax.set_title('Forward Roll Rates by Status', fontsize=12, fontweight='bold')
        ax.set_xlim(0, max(values) * 1.15)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()

    def plot_cure_rates(self, roll_rate_analysis: RollRateAnalysis,
                       figsize: tuple = (10, 6)) -> None:
        """
        Plot cure rates (improvement from delinquency).
        
        Args:
            roll_rate_analysis: RollRateAnalysis instance
            figsize: Figure size
        """
        cure_rates = roll_rate_analysis.get_cure_rates()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        labels = list(cure_rates.keys())
        values = [v * 100 for v in cure_rates.values()]
        
        bars = ax.barh(labels, values, color='#2ecc71', alpha=0.8, edgecolor='#27ae60', linewidth=1.5)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 0.5, i, f'{val:.2f}%', va='center', fontweight='bold')
        
        ax.set_xlabel('Cure Rate (%)', fontsize=11, fontweight='bold')
        ax.set_title('Cure Rates by Delinquency Status', fontsize=12, fontweight='bold')
        ax.set_xlim(0, max(values) * 1.15)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()

    def plot_default_rates_by_status(self, roll_rate_analysis: RollRateAnalysis,
                                    figsize: tuple = (10, 6)) -> None:
        """
        Plot default rates by delinquency status.
        
        Args:
            roll_rate_analysis: RollRateAnalysis instance
            figsize: Figure size
        """
        default_rates = roll_rate_analysis.get_default_rates_by_status()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        labels = list(default_rates.keys())
        values = [v * 100 for v in default_rates.values()]
        
        bars = ax.barh(labels, values, color=['#c0392b', '#e74c3c', '#f39c12'], 
                      alpha=0.8, edgecolor='#95a5a6', linewidth=1.5)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 0.5, i, f'{val:.2f}%', va='center', fontweight='bold')
        
        ax.set_xlabel('Default Rate (%)', fontsize=11, fontweight='bold')
        ax.set_title('Default Rates by Delinquency Status', fontsize=12, fontweight='bold')
        ax.set_xlim(0, max(values) * 1.15)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()

    def plot_comprehensive_dashboard(self, vintage_analysis: VintageAnalysis,
                                     roll_rate_analysis: RollRateAnalysis) -> None:
        """
        Plot comprehensive dashboard with multiple metrics.
        
        Args:
            vintage_analysis: VintageAnalysis instance
            roll_rate_analysis: RollRateAnalysis instance
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Vintage delinquency
        ax1 = fig.add_subplot(gs[0, 0])
        vintage_df = vintage_analysis.get_cumulative_loss_evolution()
        ax1.plot(vintage_df['vintage_month'], vintage_df['delinquency_rate'] * 100, 
                marker='o', color='#e74c3c', linewidth=2)
        ax1.set_title('Delinquency Rate by Vintage', fontweight='bold')
        ax1.set_ylabel('Rate (%)')
        ax1.grid(True, alpha=0.3)
        
        # Vintage charge-off
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(vintage_df['vintage_month'], vintage_df['charge_off_rate'] * 100, 
                marker='s', color='#c0392b', linewidth=2)
        ax2.set_title('Charge-off Rate by Vintage', fontweight='bold')
        ax2.set_ylabel('Rate (%)')
        ax2.grid(True, alpha=0.3)
        
        # Vintage loan count
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.bar(vintage_df['vintage_month'], vintage_df['total_loans'], 
               color='#3498db', alpha=0.7, edgecolor='#2980b9')
        ax3.set_title('Loans Issued by Vintage', fontweight='bold')
        ax3.set_ylabel('Count')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Status distribution
        ax4 = fig.add_subplot(gs[1, :])
        status_df = vintage_analysis.get_status_distribution()
        status_cols = ['current_pct', 'dpd_30_pct', 'dpd_60_pct', 'dpd_90_pct']
        labels = ['Current', '30+ DPD', '60+ DPD', '90+ DPD']
        ax4.stackplot(status_df['vintage_month'], 
                     *[status_df[col] for col in status_cols],
                     labels=labels, alpha=0.7)
        ax4.set_title('Loan Status Distribution', fontweight='bold')
        ax4.set_xlabel('Vintage Month')
        ax4.set_ylabel('Percentage (%)')
        ax4.legend(loc='upper right')
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Forward roll rates
        ax5 = fig.add_subplot(gs[2, 0])
        forward_rates = roll_rate_analysis.get_roll_forward_rates()
        forward_labels = [k.replace(' to ', '\nto ') for k in forward_rates.keys()]
        forward_vals = [v * 100 for v in forward_rates.values()]
        ax5.bar(range(len(forward_vals)), forward_vals, color='#e74c3c', alpha=0.7)
        ax5.set_xticks(range(len(forward_vals)))
        ax5.set_xticklabels(forward_labels, fontsize=8)
        ax5.set_title('Forward Roll Rates', fontweight='bold')
        ax5.set_ylabel('Rate (%)')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Cure rates
        ax6 = fig.add_subplot(gs[2, 1])
        cure_rates = roll_rate_analysis.get_cure_rates()
        cure_labels = [k.replace(' Cure Rate', '') for k in cure_rates.keys()]
        cure_vals = [v * 100 for v in cure_rates.values()]
        ax6.bar(range(len(cure_vals)), cure_vals, color='#2ecc71', alpha=0.7)
        ax6.set_xticks(range(len(cure_vals)))
        ax6.set_xticklabels(cure_labels, fontsize=8)
        ax6.set_title('Cure Rates', fontweight='bold')
        ax6.set_ylabel('Rate (%)')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Default rates
        ax7 = fig.add_subplot(gs[2, 2])
        default_rates = roll_rate_analysis.get_default_rates_by_status()
        default_labels = [k.replace(' Default Rate', '') for k in default_rates.keys()]
        default_vals = [v * 100 for v in default_rates.values()]
        ax7.bar(range(len(default_vals)), default_vals, color='#f39c12', alpha=0.7)
        ax7.set_xticks(range(len(default_vals)))
        ax7.set_xticklabels(default_labels, fontsize=8)
        ax7.set_title('Default Rates', fontweight='bold')
        ax7.set_ylabel('Rate (%)')
        ax7.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle('Credit Risk Analysis Dashboard', fontsize=14, fontweight='bold', y=0.995)
        plt.show()
