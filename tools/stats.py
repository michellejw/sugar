"""stats.py

A module for extracting and computing statistics for insulin or CGM data
"""
#import numpy as np


def get_yeardays(df):
    """
    Read the time column and extract unique days

    Args:
    df (dataframe): Pandas dataframe constructed from glooko data. Time column must be in Pandas datetime format.

    Returns:
    pandas series: year-day

    """
    df["dayofyear"] = df["time"].dt.dayofyear
    df["year"] = df["time"].dt.year
    # df["yearday"] = df["year"].astype(str) + '-' + df["dayofyear"].map('{:03.0f}'.format)
    #return np.unique(df["yearday"])

    return df["year"].astype(str) + '-' + df["dayofyear"].map('{:03.0f}'.format)
