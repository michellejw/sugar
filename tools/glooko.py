"""Tools for loading Glooko data

"""

import pandas as pd
import numpy as np

def read_all(data_folder):
    """
    Read all of the data and return a series of pandas data frames
    
    Example usage:
    df_cgm, df_bolus, df_basal, df_insulin = read_all(r"data")
    
    Args:
        data_folder (str): path to the root folder containing all the data files. The file names 
        and structure should be left exactly as they were in the initial download from Glooko.
        
    Returns:
        A 4-element tuple
        
        - **df_cgm** (pandas df): pandas dataframe containing CGM time series data
        - **df_bolus** (pandas df): Bolus data
        - **df_basal** (pandas df): Basal data
        - **df_insulin** (pandas df): Insulin corrections data
    
    """
    # Load and format CGM data
    df_cgm_data = pd.read_csv(data_folder + r"/cgm_data.csv", header=1,\
        names=["time", "bg", "sn_cgm"])
    df_cgm_data["time"] = pd.to_datetime(df_cgm_data["time"])
    
    # Load and format bolus data
    df_bolus_data = pd.read_csv(data_folder + r"/Insulin data/bolus_data.csv", header=1, \
        names=["time", "insulin_type", "bg_input", "carbs_input", "carb_ratio",\
            "insulin_delivered", "initial_delivery", "extended_delivery", "sn_omni"])
    df_bolus_data["time"] = pd.to_datetime(df_bolus_data["time"])
    # Extract carb correction and insulin correction from bolus dataframe; add as new columns
    df_bolus_data["carb_correction"] = np.divide(df_bolus_data["carbs_input"], df_bolus_data["carb_ratio"])
    df_bolus_data["insulin_correction"] = df_bolus_data["insulin_delivered"] - df_bolus_data["carb_correction"]

    # Load and format basal data
    df_basal_data = pd.read_csv(data_folder + r"/Insulin data/basal_data.csv", header=1,\
        names=["time", "insulin_type", "duration", "percentage", "rate", "insulin_delivered",\
            "sn_omni"])
    df_basal_data["time"] = pd.to_datetime(df_basal_data["time"])

    # Load and format insulin data
    df_insulin_data = pd.read_csv(data_folder + r"/Insulin data/insulin_data.csv", header=1,\
        names=["time", "total_bolus", "total_insulin", "total_basal", "sn_omni"])
    df_insulin_data["time"] = pd.to_datetime(df_insulin_data["time"])

    return df_cgm_data, df_bolus_data, df_basal_data, df_insulin_data


if __name__ == "__main__":
    # Demonstrate usage
    DATA_FOLDER = r"data"
    df_cgm, df_bolus, df_basal, df_insulin = read_all(DATA_FOLDER)
