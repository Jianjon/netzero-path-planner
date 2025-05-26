import matplotlib.pyplot as plt
import pandas as pd

def plot_emissions(years, emissions, labels=None):
    """
    Plots the emissions data over the specified years.

    Parameters:
    - years: List of years for the x-axis.
    - emissions: List of emissions data for the y-axis.
    - labels: Optional list of labels for each emissions line.
    """
    plt.figure(figsize=(10, 6))
    
    for i, emission in enumerate(emissions):
        plt.plot(years, emission, marker='o', label=labels[i] if labels else f'Path {i+1}')
    
    plt.title('Emissions Over Time')
    plt.xlabel('Year')
    plt.ylabel('Emissions (tCO₂e)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

def compare_emissions(years, emissions_list, labels=None):
    """
    Compares multiple emissions paths on the same graph.

    Parameters:
    - years: List of years for the x-axis.
    - emissions_list: List of lists containing emissions data for each path.
    - labels: Optional list of labels for each emissions line.
    """
    plt.figure(figsize=(10, 6))
    
    for i, emissions in enumerate(emissions_list):
        plt.plot(years, emissions, marker='o', label=labels[i] if labels else f'Path {i+1}')
    
    plt.title('Comparison of Emissions Paths')
    plt.xlabel('Year')
    plt.ylabel('Emissions (tCO₂e)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_emission_path(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 繪製主要區域圖
    ax.fill_between(df['年度'], df['合併排放'], 
                   color='#1f77b4', alpha=0.3, 
                   label='排放量')
    
    # 繪製邊界線
    ax.plot(df['年度'], df['合併排放'], 
            color='#1f77b4', linewidth=2)
    
    # 設定圖表樣式
    ax.set_xlabel('年份')
    ax.set_ylabel('排放量 (tCO₂e)')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 加入標註
    max_year = df['年度'].max()
    max_emission = df['合併排放'].iloc[0]
    
    # 加入文字標籤
    ax.text(df['年度'].iloc[0], max_emission*1.1, 
            'Near-term Targets', 
            fontsize=10)
    ax.text(2035, max_emission*0.6, 
            'Emission Reduction\nPathway', 
            fontsize=10)
    ax.text(max_year-5, max_emission*0.2, 
            'Neutralization', 
            fontsize=10, color='green')
    
    plt.title('減碳路徑規劃', pad=20)
    
    return fig