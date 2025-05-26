import pandas as pd

def calculate_emissions(base_emission, year, base_year):
    """
    Calculate emissions based on Taiwan's national policy reduction path.

    Args:
        base_emission (float): The baseline emission value in tCO₂e.
        year (int): The target year for emission calculation.
        base_year (int): The baseline year for comparison.

    Returns:
        float: The calculated emissions for the target year.
    """
    if year < 2030:
        return base_emission * 0.72  # 28% reduction from 2005 baseline
    elif year < 2032:
        return base_emission * 0.68  # 32% reduction from 2005 baseline
    elif year < 2035:
        return base_emission * 0.62  # 38% reduction from 2005 baseline
    else:
        return 0  # Emissions are zero after 2035

def run_taiwan_path(total_emission, baseline_year, end_year, residual_ratio):
    years = list(range(baseline_year, end_year+1))
    emissions = [calculate_emissions(total_emission, y, baseline_year) for y in years]
    s1 = [e/2 for e in emissions]
    s2 = [e/2 for e in emissions]
    df = pd.DataFrame({
        '年度': years,
        '範疇1排放': s1,
        '範疇2排放': s2,
        '合併排放': emissions
    })
    return df