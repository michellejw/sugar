"""Module for plotting BG and insulin data

This module contains functions for plotting both blood glucose and insulin data.

"""
import sys
sys.path.append("../")

import matplotlib.pyplot as plt
import seaborn as sns
import tools.glooko as gl


def daily_tir(data_folder, min_target=70, max_target=180):
    """
    Daily time in range, presented as a bar plot.
    Plot a bar chart of daily time in range from CGM data

    Example usage:
    fig, ax = daily_bars(df_cgm_daily)

    Args:
        data_folder (str): path to the root data folder from Glooko

    Keyword Args:
        min_target (number): lower bound of blood glucose range (mg/dL)
        max_target (number): upper bound of blood glucose range (mg/dL)
        
    Returns:
        A 2-element tuple

        - **fig** (matplotlib figure object)
        - **ax** (matplotlib axis object)
    """

    # Load daily CGM stats
    _, _, _, _, df_cgm_daily = gl.merge_data(data_folder, min_target=min_target, max_target=max_target)

    # Generate bar plot
    fig, ax = plt.subplots(1,1, figsize=(8,4))

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_below"], 
            color="tomato", alpha=1, label="% below")

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_inrange"], 
            bottom=df_cgm_daily["pct_below"],
            color="cornflowerblue", alpha=1, label="% in range")

    ax.bar(df_cgm_daily["time"], df_cgm_daily["pct_above"], 
            bottom=df_cgm_daily["pct_below"] + df_cgm_daily["pct_inrange"],
            color="lightsteelblue", alpha=0.7, label="% above")

    ax.spines[['right', 'top']].set_visible(False)

    ax.legend(ncol=1)
    sns.despine(left=False, bottom=True,ax=ax)

    ax.set_title("Target range: " + str(min_target) + " - " + str(max_target) + " mg/dL")

    return fig, ax


def plot_tir_vs_tdi():
    """Plot Time in Range vs Total Daily Insulin
    
    
    """