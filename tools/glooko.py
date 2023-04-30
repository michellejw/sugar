"""Tools for loading Glooko data

"""
import sys
sys.path.append("../")
from os import path
import glob
# import tools.stats as st
import stats as st
import pandas as pd
import numpy as np


def read_all(data_folder, min_target=70, max_target=180, match_date_ranges=True):
    """
    Read all of the data and return a series of pandas data frames
    
    Example usage:
    df_cgm, df_bolus, df_basal, df_insulin, df_cgm_daily = read_all(r"data")
    
    Args:
        data_folder (str): path to the root folder containing all the data files. The file names 
        and structure should be left exactly as they were in the initial download from Glooko.
    
    Keyword Args:
        min_target (number): lower bound of blood glucose range (mg/dL)
        max_target (number): upper bound of blood glucose range (mg/dL)
        match_date_ranges (bool): flag indicating whether to reduce the daily stats so that they all have the same length (default = True). This is because sometimes CGM and insulin/pump data are not the same length.
        
    Returns:
        A 4-element tuple
        
        - **df_cgm** (pandas df): pandas dataframe containing CGM time series data
        - **df_bolus** (pandas df): Bolus data
        - **df_basal** (pandas df): Basal data
        - **df_insulin** (pandas df): Insulin corrections data
        - **df_cgm_daily** (pandas df): Various daily BG stats
    
    """
    # Load and format CGM data
    cgm_file = path.normpath(data_folder + r"/cgm_data.csv")
    df_cgm_data = pd.read_csv(cgm_file, header=1,\
        names=["time", "bg", "sn_cgm"])
    df_cgm_data["time"] = pd.to_datetime(df_cgm_data["time"])
    df_cgm_data["yearday"] = st.get_yeardays(df_cgm_data)
    df_cgm_data.drop("sn_cgm", axis=1, inplace=True)


    # COMPUTE STATS PER DAY
    df_cgm_daily = df_cgm_data[["bg", "yearday"]].groupby("yearday").describe()["bg"]
    df_cgm_daily["yearday"] = df_cgm_daily.index
    df_cgm_daily["time"] = pd.to_datetime(df_cgm_daily['yearday'], format='%Y-%j')

    
    # Load and format bolus data
    bolus_file = path.normpath(data_folder + r"/Insulin data/bolus_data.csv")
    df_bolus_data = pd.read_csv(bolus_file, header=1, 
                                names=["time", "insulin_type", "bg_input", "carbs_input", "carb_ratio", 
                                       "insulin_delivered", "initial_delivery", "extended_delivery", 
                                       "sn_omni"])
    df_bolus_data.drop("sn_omni", axis=1, inplace=True)
    df_bolus_data["time"] = pd.to_datetime(df_bolus_data["time"])
    # Extract carb correction and insulin correction from bolus dataframe; add as new columns
    df_bolus_data["carb_correction"] = np.divide(df_bolus_data["carbs_input"], df_bolus_data["carb_ratio"])
    df_bolus_data["insulin_correction"] = df_bolus_data["insulin_delivered"] - df_bolus_data["carb_correction"]

    # Load and format basal data
    basal_file = path.normpath(data_folder + r"/Insulin data/basal_data.csv")
    df_basal_data = pd.read_csv(basal_file, header=1,\
        names=["time", "insulin_type", "duration", "percentage", "rate", "insulin_delivered",\
            "sn_omni"])
    df_basal_data.drop("sn_omni", axis=1, inplace=True)
    df_basal_data["time"] = pd.to_datetime(df_basal_data["time"])

    # Load and format insulin data
    insulin_file = path.normpath(data_folder + r"/Insulin data/insulin_data.csv")
    df_insulin_data = pd.read_csv(insulin_file, header=1,\
        names=["time", "total_bolus", "total_insulin", "total_basal", "sn_omni"])
    df_insulin_data.drop("sn_omni", axis=1, inplace=True)
    df_insulin_data["time"] = pd.to_datetime(df_insulin_data["time"])
    df_insulin_data["yearday"] = st.get_yeardays(df_insulin_data)

    # Compute additional daily stats
    # COMPUTE DAILY TIME IN RANGE
    min_target = 70
    max_target = 180

    unique_days = df_cgm_daily["yearday"].tolist()

    # Initialize lists
    pct_above = []
    pct_below = []
    pct_inrange = []

    # loop through each day (I'm sure there's a fancy way to do this with Pandas but I 
    # can't figure it out...)
    for day in unique_days:
        df_sub = df_cgm_data[df_cgm_data["yearday"]==day]
        this_total = len(df_sub)
        if this_total > 0:
            pct_above.append(sum(df_sub["bg"]>max_target)/this_total*100)
            pct_below.append(sum(df_sub["bg"]<=min_target)/this_total*100)
            pct_inrange.append(sum((df_sub["bg"] > min_target) & (df_sub["bg"] <= max_target))/this_total*100)
        else:
            pct_above.append(0)
            pct_below.append(0)
            pct_inrange.append(0)
            
    df_cgm_daily["pct_above"] = pct_above
    df_cgm_daily["pct_below"] = pct_below
    df_cgm_daily["pct_inrange"] = pct_inrange

    # make sure the date ranges match
    cgm_in_insulin = df_cgm_daily["yearday"].isin(df_insulin_data["yearday"])
    insulin_in_cgm = df_insulin_data["yearday"].isin(df_cgm_daily["yearday"])

    if match_date_ranges:
        df_cgm_daily = df_cgm_daily[cgm_in_insulin]
        df_insulin_data = df_insulin_data[insulin_in_cgm]

    return df_cgm_data, df_bolus_data, df_basal_data, df_insulin_data, df_cgm_daily


def merge_data(folder_list, out_folder):
    """
    Combine multiple downloaded glooko folders and save the non-overlapping time series.

    Example usage:
    merge_data(["../data/glooko01", "../data/glooko02"], "../)

    Args:
        folder_list (list): list of strings, which are paths to folders each containing downloaded Glooko data.
        output_file (str): Path and file name for the output pickle file

    """
    # Create empty dataframes
    df_cgm0 = pd.DataFrame(columns=['time', 'bg', 'dayofyear', 'year', 'yearday'])
    df_bolus0 = pd.DataFrame(columns=['time', 'insulin_type', 'bg_input', 'carbs_input', 'carb_ratio',
                                      'insulin_delivered', 'initial_delivery', 'extended_delivery', 'carb_correction', 'insulin_correction'])
    df_basal0 = pd.DataFrame(columns=['time', 'insulin_type', 'duration', 'percentage', 'rate',
                                     'insulin_delivered'])
    df_insulin0 = pd.DataFrame(columns=['time', 'total_bolus', 'total_insulin', 'total_basal', 'dayofyear',
                                        'year', 'yearday'])
    df_cgm_daily0 = pd.DataFrame(columns=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'yearday',
                                          'time', 'pct_above', 'pct_below', 'pct_inrange'])

    for folder in folder_list:
        # Read files and create dataframes
        df_cgm, df_bolus, df_basal, df_insulin, df_cgm_daily = read_all(folder)

        # Concatenate the new data
        df_cgm0 = pd.concat((df_cgm0, df_cgm))
        df_bolus0 = pd.concat((df_bolus0, df_bolus))
        df_basal0 = pd.concat((df_basal0, df_basal))
        df_insulin = pd.concat((df_insulin0, df_insulin))
        df_cgm_daily0 = pd.concat((df_cgm_daily0, df_cgm_daily))
    
    # Remove duplicate rows
    df_cgm_daily0.drop_duplicates(inplace=True)
    df_bolus0.drop_duplicates(inplace=True)
    df_basal0.drop_duplicates(inplace=True)
    df_insulin0.drop_duplicates(inplace=True)
    df_cgm_daily0.drop_duplicates(inplace=True)


    return df_cgm_daily0, df_bolus0, df_basal0, df_insulin0, df_cgm_daily0


if __name__ == "__main__":
    # Demonstrate usage
    DATA_FOLDER = r"data/glooko"
    # df_cgm, df_bolus, df_basal, df_insulin, df_cgm_daily = read_all(DATA_FOLDER)

    folders = glob.glob("data/*/")
    outfolder = "data/"
    merge_data(folders, outfolder)

    print('breakpoint here...')


