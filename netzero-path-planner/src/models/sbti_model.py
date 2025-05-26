import pandas as pd

def calculate_emissions(base_emission, year, base_year, user_selected_ratio):
    """
    Calculate emissions based on the SBTi absolute contraction method.

    Parameters:
    - base_emission (float): The initial emission value in tCO₂e.
    - year (int): The target year for the emission calculation.
    - base_year (int): The baseline year for the emission calculation.
    - user_selected_ratio (float): The desired end ratio of emissions (0%, 5%, or 10%).

    Returns:
    - float: The calculated emissions for the target year.
    """
    return base_emission * (1 - 0.042) ** (year - base_year)

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

def run_sbt1_5(total_emission, baseline_year, end_year, residual_ratio):
    years = list(range(baseline_year, end_year+1))
    emissions = [calculate_emissions(total_emission, y, baseline_year, residual_ratio) for y in years]
    # 預設範疇1/2各半，主程式可再覆蓋
    s1 = [e/2 for e in emissions]
    s2 = [e/2 for e in emissions]
    df = pd.DataFrame({
        '年度': years,
        '範疇1排放': s1,
        '範疇2排放': s2,
        '合併排放': emissions
    })
    return df