import streamlit as st
import pandas as pd
from models import sbti_model, taiwan_model 
from utils import plot
from utils.model_descriptions import SBTI_DESCRIPTION, TAIWAN_DESCRIPTION, RE100_DESCRIPTION
import plotly

def main():
    # 頁面設定
    VERSION = "1.0.0"
    st.set_page_config(page_title=f"減碳路徑規劃器 v{VERSION}", layout="centered")
    
    # 標題
    st.title("企業減碳路徑規劃器 NetZero Path Planner")
    st.markdown("本工具依據國際 SBTi 與台灣政策，協助企業模擬減碳目標與路徑。")

    # ==== 使用者輸入 ====
    st.header("基準排放資料輸入")
    
    col_s1, col_s2, col_year = st.columns(3)
    with col_s1:
        s1 = st.number_input("範疇一排放量（tCO₂e）", min_value=0, value=10000)
    with col_s2:
        s2 = st.number_input("範疇二排放量（tCO₂e）", min_value=0, value=5000)
    with col_year:
        baseline_year = st.selectbox("基準年", list(range(2005, 2025)), index=15)
    
    total_emission = s1 + s2
    
    st.markdown("---")
    
    # ==== 模型選擇 ====
    st.header("減碳目標設定")
    # --- 說明按鈕 ---
    model_col, info_col = st.columns([8, 1])
    with model_col:
        model = st.radio("選擇減碳情境", ["SBTi 1.5°C", "台灣政策目標"], horizontal=True)
    with info_col:
        if 'show_sbti_desc' not in st.session_state:
            st.session_state['show_sbti_desc'] = False
        if 'show_taiwan_desc' not in st.session_state:
            st.session_state['show_taiwan_desc'] = False
        if model == "SBTi 1.5°C":
            if st.button("SBTi說明", key="sbti_info"):
                st.session_state['show_sbti_desc'] = not st.session_state['show_sbti_desc']
        else:
            if st.button("台灣政策說明", key="taiwan_info"):
                st.session_state['show_taiwan_desc'] = not st.session_state['show_taiwan_desc']
    if model == "SBTi 1.5°C" and st.session_state['show_sbti_desc']:
        with st.expander("SBTi 1.5°C 絕對收縮法說明", expanded=True):
            st.markdown(SBTI_DESCRIPTION)
    if model == "台灣政策目標" and st.session_state['show_taiwan_desc']:
        with st.expander("台灣政策目標說明", expanded=True):
            st.markdown(TAIWAN_DESCRIPTION)

    # ==== SBTi 動態三段式設定 ====
    if model == "SBTi 1.5°C":
        # --- RE100 ---
        re_col1, re_col2 = st.columns([8, 1])
        with re_col1:
            re100_enable = st.checkbox("RE100：範疇二排放歸零（100%再生電）", value=False)
            re100_year = 2030
            if re100_enable:
                re100_year = st.number_input("RE100 歸零年（預設2030，可自訂）", min_value=baseline_year+1, max_value=2050, value=2030, key="re100_year_sbti")
        with re_col2:
            if 'show_re100_desc' not in st.session_state:
                st.session_state['show_re100_desc'] = False
            if st.button("RE100說明", key="re100_info_sbti"):
                st.session_state['show_re100_desc'] = not st.session_state['show_re100_desc']
        if re100_enable and st.session_state['show_re100_desc']:
            with st.expander("什麼是 RE100？", expanded=True):
                st.markdown(RE100_DESCRIPTION)
        st.subheader("2050年殘留排放比例")
        residual = st.selectbox("2050年殘留排放比例", ["0%", "5%", "10%"], index=1)
        residual_ratio = {"0%": 0.0, "5%": 0.05, "10%": 0.10}[residual]
        total_years = 2050 - baseline_year
        st.markdown("---")
        st.subheader("近期設定（Short-term）")
        short_years = st.slider("近期年數", min_value=3, max_value=5, value=3)
        short_rate = st.slider("近期每年減碳率(%)", min_value=3.0, max_value=15.0, value=4.2, step=0.1) / 100
        # 計算近期結束後剩餘排放
        short_emission = total_emission * ((1 - short_rate) ** short_years)
        remain_years = total_years - short_years
        st.markdown(f"近期結束後剩餘年數：{remain_years} 年")
        st.markdown("---")
        st.subheader("中期設定（Mid-term）")
        mid_years = st.slider("中期年數", min_value=5, max_value=min(10, remain_years-1), value=min(7, remain_years-1))
        mid_rate_min = 1.0
        mid_rate_max = 20.0
        mid_rate = st.slider("中期每年減碳率(%)", min_value=mid_rate_min, max_value=mid_rate_max, value=3.0, step=0.1) / 100
        # 計算中期結束後剩餘排放
        mid_emission = short_emission * ((1 - mid_rate) ** mid_years)
        long_years = remain_years - mid_years
        st.markdown(f"中期結束後剩餘年數：{long_years} 年")
        st.markdown("---")
        st.subheader("長期設定（Long-term）")
        # 動態計算長期所需減碳率區間
        if long_years > 0:
            # 反推長期最低減碳率，確保2050達標
            try:
                required_long_rate = 1 - (residual_ratio * total_emission / mid_emission) ** (1 / long_years)
                required_long_rate = max(0, min(1, required_long_rate))
            except Exception:
                required_long_rate = 0.0
            long_rate_min = max(0.0, round(required_long_rate*100, 2))
            long_rate_max = 8.0
            long_rate = st.slider("長期每年減碳率(%)", min_value=long_rate_min, max_value=long_rate_max, value=long_rate_min, step=0.1) / 100
        else:
            long_rate = 0.0
        # 預測2050排放
        if long_years > 0:
            final_emission = mid_emission * ((1 - long_rate) ** long_years)
        else:
            final_emission = mid_emission
        target_emission = total_emission * residual_ratio
        st.markdown(f"**預測2050排放：{final_emission:.2f} tCO₂e** (目標：{target_emission:.2f} tCO₂e)")
        can_submit = abs(final_emission - target_emission) < 1
        if not can_submit:
            st.error("目前設定無法達到2050目標，請調整減碳率或年數！")
        st.markdown("---")
    else:
        residual = st.selectbox("2050年殘留排放比例", ["0%", "5%", "10%"], index=1)
        residual_ratio = {"0%": 0.0, "5%": 0.05, "10%": 0.10}[residual]
        re_col1, re_col2 = st.columns([8, 1])
        with re_col1:
            re100_enable = st.checkbox("RE100：範疇二排放歸零（100%再生電）", value=False)
            re100_year = st.number_input("RE100 歸零年（預設2030，可自訂）", min_value=baseline_year+1, max_value=2050, value=2030)
        with re_col2:
            if 'show_re100_desc' not in st.session_state:
                st.session_state['show_re100_desc'] = False
            if st.button("RE100說明", key="re100_info_taiwan"):
                st.session_state['show_re100_desc'] = not st.session_state['show_re100_desc']
        if re100_enable and st.session_state['show_re100_desc']:
            with st.expander("什麼是 RE100？", expanded=True):
                st.markdown(RE100_DESCRIPTION)
        can_submit = True

    # ==== 送出按鈕 ====
    submit = st.button("送出設定", disabled=not can_submit)
    
    # ==== 模型計算 ====
    if submit:
        st.markdown("---")
        st.header("模擬結果")
        start_year = baseline_year
        end_year = 2050
        # 加入資料驗證
        if total_emission == 0:
            st.warning("⚠️ 請輸入排放量數據")
            return
        try:
            if model == "SBTi 1.5°C":
                df = sbti_model.run_sbt1_5(total_emission, baseline_year, end_year, short_years, short_rate, mid_years, mid_rate, long_rate)
                # 若套用 RE100，修改 S2 路徑
                if re100_enable:
                    s2_path = []
                    for y in df['年度']:
                        if y <= re100_year:
                            ratio = max(0, 1 - (y-baseline_year)/(re100_year-baseline_year))
                            s2_path.append(s2 * ratio)
                        else:
                            s2_path.append(0)
                    df["範疇2排放"] = s2_path
                    df["合併排放"] = df["範疇1排放"] + df["範疇2排放"]
                # 計算減碳量和減碳百分比
                df["減碳量"] = df["合併排放"].shift(1) - df["合併排放"]
                df["減碳百分比"] = (df["減碳量"] / df["合併排放"].shift(1) * 100).round(2)
                df.loc[df.index[0], ["減碳量", "減碳百分比"]] = 0
                # SBTi專用圖表
                fig = plot.plot_emission_path(df, use_plotly=True, short_years=short_years, mid_years=mid_years, baseline_year=baseline_year)
                st.plotly_chart(fig, use_container_width=True)
                # SBTi分段說明
                st.markdown("---")
                st.subheader("各階段減碳說明")
                short_end = baseline_year + short_years
                mid_end = short_end + mid_years
                long_end = 2050
                short_end_emission = df[df['年度'] == short_end]['合併排放'].values[0]
                mid_end_emission = df[df['年度'] == mid_end]['合併排放'].values[0]
                long_end_emission = df[df['年度'] == long_end]['合併排放'].values[0]
                st.markdown(f"**近期（{baseline_year}~{short_end}）**：每年減碳率 {short_rate*100:.1f}%，結束時排放量 {short_end_emission:.2f} tCO₂e。這是SBTi要求企業立即啟動的高強度減碳階段，通常需靠能源效率、再生能源等措施快速見效。")
                st.markdown(f"**中期（{short_end+1}~{mid_end}）**：每年減碳率 {mid_rate*100:.1f}%，結束時排放量 {mid_end_emission:.2f} tCO₂e。這是企業持續優化、轉型的階段，需結合技術升級、流程改善等中長期策略。")
                st.markdown(f"**長期（{mid_end+1}~2050）**：每年減碳率 {long_rate*100:.1f}%，2050年排放量 {long_end_emission:.2f} tCO₂e。這是邁向淨零的最後階段，需結合創新、碳捕捉、供應鏈合作等多元手段，確保達成SBTi長期目標。")
                st.markdown(f"2050年殘留排放比例：{residual}，目標排放量：{long_end_emission:.2f} tCO₂e")
                st.subheader("每年目標排放表")
                formatted_df = df.copy()
                formatted_df = formatted_df[formatted_df['年度'] <= 2050]
                formatted_df["合併排放"] = formatted_df["合併排放"].round(2)
                formatted_df["減碳量"] = formatted_df["減碳量"].round(2)
                formatted_df["減碳百分比"] = formatted_df["減碳百分比"].map(lambda x: f"{x}%" if x != 0 else "-")
                st.dataframe(
                    formatted_df.set_index("年度")[["合併排放", "減碳量", "減碳百分比"]], 
                    use_container_width=True
                )
                st.download_button("📥 下載CSV", df.to_csv(index=False), file_name="carbon_path.csv")
                if st.button("儲存設定"):
                    config = {
                        "baseline_year": baseline_year,
                        "s1": s1,
                        "s2": s2,
                        "model": model,
                        "residual": residual,
                        "re100": re100_enable,
                        "re100_year": re100_year
                    }
                    st.session_state.saved_config = config
                    st.success("設定已儲存！")
            elif model == "台灣政策目標":
                # 取得自動換算的減碳目標百分比
                adjusted_targets = taiwan_model.get_adjusted_taiwan_targets(baseline_year)
                df = taiwan_model.run_taiwan_path(total_emission, baseline_year, end_year, residual_ratio)
                # 若套用 RE100，修改 S2 路徑
                if re100_enable:
                    s2_path = []
                    for y in df['年度']:
                        if y <= re100_year:
                            ratio = max(0, 1 - (y-baseline_year)/(re100_year-baseline_year))
                            s2_path.append(s2 * ratio)
                        else:
                            s2_path.append(0)
                    df["範疇2排放"] = s2_path
                    df["合併排放"] = df["範疇1排放"] + df["範疇2排放"]
                # 計算減碳量和減碳百分比
                df["減碳量"] = df["合併排放"].shift(1) - df["合併排放"]
                df["減碳百分比"] = (df["減碳量"] / df["合併排放"].shift(1) * 100).round(2)
                df.loc[df.index[0], ["減碳量", "減碳百分比"]] = 0
                # 台灣專用圖表（單色曲線+重點標註）
                fig = plot.plot_emission_path_simple(df)
                # 標註重點年份
                for year, label in zip([2030, 2032, 2035, 2050], ["2030目標", "2032目標", "2035目標", "2050目標"]):
                    if year in df['年度'].values:
                        yval = df[df['年度'] == year]['合併排放'].values[0]
                        fig.add_trace(plotly.graph_objects.Scatter(
                            x=[year], y=[yval],
                            mode="markers+text",
                            marker=dict(size=12, color="red" if year==2050 else "orange"),
                            text=[f"{label}<br>{yval:.0f}"],
                            textposition="top center",
                            showlegend=False
                        ))
                st.plotly_chart(fig, use_container_width=True)
                # 台灣分段說明
                st.markdown("---")
                st.subheader("重要年份減碳說明")
                for year, label in zip([2030, 2032, 2035], ["2030年目標", "2032年目標", "2035年目標"]):
                    if year in df['年度'].values:
                        emission = df[df['年度'] == year]['合併排放'].values[0]
                        reduction = total_emission - emission
                        percent = round(adjusted_targets[year]*100, 2)
                        st.markdown(f"**{label}**：排放量 {emission:.2f} tCO₂e，較基準年減少 {reduction:.2f} tCO₂e（{percent}%）")
                if 2050 in df['年度'].values:
                    emission = df[df['年度'] == 2050]['合併排放'].values[0]
                    reduction = total_emission - emission
                    percent = (reduction / total_emission * 100) if total_emission > 0 else 0
                    st.markdown(f"**2050年預估**：排放量 {emission:.2f} tCO₂e，較基準年減少 {reduction:.2f} tCO₂e（{percent:.1f}%）")
                st.subheader("每年目標排放表")
                formatted_df = df.copy()
                formatted_df = formatted_df[formatted_df['年度'] <= 2050]
                formatted_df["合併排放"] = formatted_df["合併排放"].round(2)
                formatted_df["減碳量"] = formatted_df["減碳量"].round(2)
                formatted_df["減碳百分比"] = formatted_df["減碳百分比"].map(lambda x: f"{x}%" if x != 0 else "-")
                st.dataframe(
                    formatted_df.set_index("年度")[["合併排放", "減碳量", "減碳百分比"]], 
                    use_container_width=True
                )
                st.download_button("📥 下載CSV", df.to_csv(index=False), file_name="taiwan_carbon_path.csv")
                if st.button("儲存設定"):
                    config = {
                        "baseline_year": baseline_year,
                        "s1": s1,
                        "s2": s2,
                        "model": model,
                        "residual": residual,
                        "re100": re100_enable,
                        "re100_year": re100_year
                    }
                    st.session_state.saved_config = config
                    st.success("設定已儲存！")
        except Exception as e:
            st.error(f"計算過程發生錯誤: {str(e)}")
            st.info("請檢查輸入數據是否正確，或聯繫系統管理員")

if __name__ == "__main__":
    main()