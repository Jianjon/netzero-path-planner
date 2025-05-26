import streamlit as st
import pandas as pd
from models import sbti_model, taiwan_model 
from utils import plot
from utils.model_descriptions import SBTI_DESCRIPTION, TAIWAN_DESCRIPTION, RE100_DESCRIPTION

def main():
    # 頁面設定
    VERSION = "1.0.0"
    st.set_page_config(page_title=f"減碳路徑規劃器 v{VERSION}", layout="centered")
    
    # 標題
    st.title("🌿 企業減碳路徑規劃器 NetZero Path Planner")
    st.markdown("根據國際 SBTi 與台灣政策，模擬您企業的減碳目標與路徑")

    # ==== 使用者輸入 ====
    st.header("📥 基準排放資料輸入")
    
    s1 = st.number_input("輸入範疇一排放量（tCO₂e）", min_value=0, value=10000)
    s2 = st.number_input("輸入範疇二排放量（tCO₂e）", min_value=0, value=5000)
    baseline_year = st.selectbox("基準年", list(range(2005, 2025)), index=15)
    
    total_emission = s1 + s2
    
    st.markdown("---")
    
    # ==== 模型選擇 ====
    st.header("🎯 減碳目標設定")
    model = st.radio("選擇減碳情境", ["SBTi 1.5°C", "台灣政策目標"], horizontal=True)

    # --- 說明區塊狀態控制 ---
    if 'show_sbti_desc' not in st.session_state:
        st.session_state['show_sbti_desc'] = False
    if 'show_taiwan_desc' not in st.session_state:
        st.session_state['show_taiwan_desc'] = False
    if 'show_re100_desc' not in st.session_state:
        st.session_state['show_re100_desc'] = False

    # --- SBTi/台灣說明按鈕 ---
    col1, col2 = st.columns([8,1])
    with col1:
        pass
    with col2:
        if model == "SBTi 1.5°C":
            if st.button("說明", key="sbti_btn"):
                st.session_state['show_sbti_desc'] = not st.session_state['show_sbti_desc']
        else:
            if st.button("說明", key="taiwan_btn"):
                st.session_state['show_taiwan_desc'] = not st.session_state['show_taiwan_desc']

    if model == "SBTi 1.5°C" and st.session_state['show_sbti_desc']:
        with st.expander("📘 SBTi 1.5°C 絕對收縮法說明", expanded=True):
            st.markdown(SBTI_DESCRIPTION)
    if model == "台灣政策目標" and st.session_state['show_taiwan_desc']:
        with st.expander("📘 台灣國家政策目標路徑說明", expanded=True):
            st.markdown(TAIWAN_DESCRIPTION)

    residual = st.selectbox("2050年殘留排放比例", ["0%", "5%", "10%"], index=1)
    residual_ratio = {"0%": 0.0, "5%": 0.05, "10%": 0.10}[residual]
    
    re100_enable = st.checkbox("RE100：範疇二排放歸零（100%再生電）", value=False)
    re100_year = 2030
    if re100_enable:
        colr1, colr2 = st.columns([8,1])
        with colr1:
            pass
        with colr2:
            if st.button("說明", key="re100_btn"):
                st.session_state['show_re100_desc'] = not st.session_state['show_re100_desc']
        if st.session_state['show_re100_desc']:
            with st.expander("✅ 什麼是 RE100？", expanded=True):
                st.markdown(RE100_DESCRIPTION)
        re100_year = st.number_input("請輸入 RE100 歸零年（預設2030，可自訂）", min_value=baseline_year+1, max_value=2050, value=2030)

    # ==== 送出按鈕 ====
    submit = st.button("🚀 送出設定")
    
    # ==== 模型計算 ====
    if submit:
        st.markdown("---")
        st.header("📊 模擬結果")
        start_year = baseline_year
        end_year = 2050
        # 加入資料驗證
        if total_emission == 0:
            st.warning("⚠️ 請輸入排放量數據")
            return
        try:
            if model == "SBTi 1.5°C":
                df = sbti_model.run_sbt1_5(total_emission, baseline_year, end_year, residual_ratio)
            elif model == "台灣政策目標":
                df = taiwan_model.run_taiwan_path(total_emission, baseline_year, end_year, residual_ratio)
            # 若套用 RE100，修改 S2 路徑
            if re100_enable:
                years = list(range(baseline_year, end_year+1))
                s2_path = []
                for y in years:
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
            # 第一年的減碳量和百分比設為0
            df.loc[df.index[0], ["減碳量", "減碳百分比"]] = 0
            # ==== 顯示結果 ====
            st.subheader("📈 減碳曲線圖")
            fig = plot.plot_emission_path(df)
            st.pyplot(fig)
            st.subheader("📋 每年目標排放表")
            # 設定表格顯示格式
            formatted_df = df.copy()
            formatted_df["合併排放"] = formatted_df["合併排放"].round(2)
            formatted_df["減碳量"] = formatted_df["減碳量"].round(2)
            formatted_df["減碳百分比"] = formatted_df["減碳百分比"].map(lambda x: f"{x}%" if x != 0 else "-")
            st.dataframe(
                formatted_df.set_index("年度")[["合併排放", "減碳量", "減碳百分比"]], 
                use_container_width=True
            )
            st.download_button("📥 下載CSV", df.to_csv(index=False), file_name="carbon_path.csv")
            if st.button("💾 儲存設定"):
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