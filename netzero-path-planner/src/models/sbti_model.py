import pandas as pd
import math

def calculate_emissions(base_emission, year, base_year, annual_reduction):
    """
    Calculate emissions based on the SBTi absolute contraction method.

    Parameters:
    - base_emission (float): The initial emission value in tCO₂e.
    - year (int): The target year for the emission calculation.
    - base_year (int): The baseline year for the emission calculation.
    - annual_reduction (float): The annual reduction rate.

    Returns:
    - float: The calculated emissions for the target year.
    """
    return base_emission * ((1 - annual_reduction) ** (year - base_year))

def get_final_emission(user_selected_ratio):
    """
    Get the final emission target based on the user-selected ratio.

    Parameters:
    - user_selected_ratio (float): The desired end ratio of emissions (0%, 5%, or 10%).

    Returns:
    - float: The final emission target.
    """
    if user_selected_ratio == 0:
        return 0
    elif user_selected_ratio == 5:
        return 0.05
    elif user_selected_ratio == 10:
        return 0.1
    else:
        raise ValueError("Invalid user selected ratio. Choose from 0, 5, or 10.")

def run_sbt1_5(total_emission, baseline_year, end_year, short_years=3, short_rate=0.042, mid_years=7, mid_rate=0.03, long_rate=0.02):
    """
    Calculate the emissions for the SBTi 1.5°C scenario.

    Parameters:
    - total_emission (float): The initial emission value in tCO₂e.
    - baseline_year (int): The baseline year for the emission calculation.
    - end_year (int): The target year for the emission calculation.
    - short_years (int): The number of years for the short-term reduction.
    - short_rate (float): The annual reduction rate for the short-term.
    - mid_years (int): The number of years for the mid-term reduction.
    - mid_rate (float): The annual reduction rate for the mid-term.
    - long_rate (float): The annual reduction rate for the long-term.

    Returns:
    - DataFrame: A DataFrame containing the emissions for each year.
    """
    years = list(range(baseline_year, 2061))  # 延伸到2060
    emissions = []
    current = total_emission
    for i, y in enumerate(years):
        if i == 0:
            emissions.append(current)
        elif y <= baseline_year + short_years:
            current = current * (1 - short_rate)
            emissions.append(current)
        elif y <= baseline_year + short_years + mid_years:
            current = current * (1 - mid_rate)
            emissions.append(current)
        elif y <= 2050:
            current = current * (1 - long_rate)
            emissions.append(current)
        else:
            emissions.append(emissions[-1])  # 2050~2060維持不變
    s1 = [e/2 for e in emissions]
    s2 = [e/2 for e in emissions]
    df = pd.DataFrame({
        '年度': years,
        '範疇1排放': s1,
        '範疇2排放': s2,
        '合併排放': emissions
    })
    return df