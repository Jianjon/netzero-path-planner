import pandas as pd
from utils.model_data import ghg_by_year

def calculate_emissions(base_emission, year, base_year, residual_ratio):
    """
    Calculate emissions based on Taiwan's national policy reduction path.

    Args:
        base_emission (float): The baseline emission value in tCO₂e.
        year (int): The target year for emission calculation.
        base_year (int): The baseline year for comparison.
        residual_ratio (float): The residual emission ratio after 2050.

    Returns:
        float: The calculated emissions for the target year.
    """
    if year <= 2030:
        # 線性插值到2030 (72%)
        ratio = 1 - 0.28 * (year - base_year) / (2030 - base_year)
        return base_emission * ratio
    elif year <= 2032:
        # 線性插值 2030(72%)~2032(68%)
        ratio = 0.72 - (0.72-0.68) * (year-2030)/(2032-2030)
        return base_emission * ratio
    elif year <= 2035:
        # 線性插值 2032(68%)~2035(62%)
        ratio = 0.68 - (0.68-0.62) * (year-2032)/(2035-2032)
        return base_emission * ratio
    else:
        # 2035~2050 線性遞減到 residual_ratio
        ratio = 0.62 - (0.62 - residual_ratio) * (year-2035)/(2050-2035)
        return base_emission * ratio

def run_taiwan_path(total_emission, baseline_year, end_year, residual_ratio):
    years = list(range(baseline_year, end_year+1))
    emissions = [calculate_emissions(total_emission, y, baseline_year, residual_ratio) for y in years]
    s1 = [e/2 for e in emissions]
    s2 = [e/2 for e in emissions]
    df = pd.DataFrame({
        '年度': years,
        '範疇1排放': s1,
        '範疇2排放': s2,
        '合併排放': emissions
    })
    return df

def get_adjusted_taiwan_targets(baseline_year):
    # 2005年排放量
    base_2005 = ghg_by_year[2005]
    # 目標年排放量
    base_target = ghg_by_year.get(baseline_year, base_2005)
    ratio = base_2005 / base_target if base_target > 0 else 1
    # 原始目標比例
    targets = {
        2030: 0.28,
        2032: 0.32,
        2035: 0.38
    }
    adjusted = {}
    for y, t in targets.items():
        adjusted[y] = 1 - (1-t) * ratio
    return adjusted