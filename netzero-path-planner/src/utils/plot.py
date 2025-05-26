import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

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

def plot_emission_path(df, use_plotly=True, short_years=3, mid_years=7, baseline_year=2020):
    if use_plotly:
        # 主線：淡藍色，連續
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["年度"], y=df["合併排放"],
            mode="lines+markers",
            fill="tozeroy",
            name="碳排放路徑",
            line=dict(color="#7ec8e3", width=3),
            fillcolor="rgba(126,200,227,0.2)"
        ))
        # 標註重點時間點
        short_end = baseline_year + short_years
        mid_end = short_end + mid_years
        long_end = 2050
        for year, label, color in zip(
            [short_end, mid_end, long_end],
            ["近期結束", "中期結束", "2050目標"],
            ["#ffb347", "#ffb347", "#ff6961"]):
            yval = df[df['年度'] == year]['合併排放'].values[0]
            fig.add_trace(go.Scatter(
                x=[year], y=[yval],
                mode="markers+text",
                marker=dict(size=12, color=color),
                text=[f"{label}<br>{int(yval)}"],
                textposition="top center",
                showlegend=False
            ))
        fig.update_layout(
            title="碳排放路徑模擬",
            xaxis_title="年度",
            yaxis_title="排放量（tCO₂e）",
            template="plotly_white",
            xaxis=dict(range=[df["年度"].min(), 2060]),
            showlegend=False
        )
        return fig
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["年度"], df["合併排放"], color="#7ec8e3", linewidth=2, label="合併排放量")
        ax.fill_between(df["年度"], df["合併排放"], color="#7ec8e3", alpha=0.2)
        ax.set_title("碳排放路徑模擬", fontsize=16)
        ax.set_xlabel("年度", fontsize=12)
        ax.set_ylabel("排放量（tCO₂e）", fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.set_xlim(df["年度"].min(), 2060)
        return fig

def plot_emission_path_simple(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["年度"], y=df["合併排放"],
        mode="lines+markers",
        fill="tozeroy",
        name="合併排放",
        line=dict(color="royalblue", width=3)
    ))
    fig.update_layout(
        title="碳排放路徑模擬",
        xaxis_title="年度",
        yaxis_title="排放量（tCO₂e）",
        template="plotly_white",
        xaxis=dict(range=[df["年度"].min(), 2060])
    )
    return fig