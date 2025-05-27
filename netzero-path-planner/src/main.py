import streamlit as st
import pandas as pd
from models import sbti_model, taiwan_model 
from utils import plot
from utils.model_descriptions import SBTI_DESCRIPTION, TAIWAN_DESCRIPTION, RE100_DESCRIPTION
import plotly

# LOGO 與聯絡資訊
LOGO_URL = "https://i.imgur.com/2yaf2wb.png"  # 可換成你的 LOGO 連結
BRAND_INFO = """
<div style='text-align:center;font-size:15px;color:#444;margin-top:32px;'>
<b>Jon</b> ｜ jonchang1980@gmail.com
<br>（LINE QR code、LinkedIn QR code 可放於下方，請見下方教學）
</div>
"""

# 主題色彩與字體統一
PRIMARY_COLOR = "#2563EB"  # 主色（科技藍）
BG_COLOR = "#FFFFFF"        # 背景色
TEXT_COLOR = "#000000"     # 標題/主文字
SUBTEXT_COLOR = "#1E293B"  # 深灰藍（說明/副文字）
CARD_BG = "#E0F2FE"        # 輔助區塊底色
FOOTER_BG = "#F3F4F6"      # Footer 輕灰底
FONT_FAMILY = "Inter, Noto Sans, sans-serif"

# 首頁內容
LANDING_TITLE = "快速產出企業減碳路徑與年度減量目標"
LANDING_SUBTITLE = "輸入範疇一與範疇二排放，即可根據SBTi與台灣政策模擬2050淨零路徑"
LANDING_TARGET = "使用對象：中小企業、顧問公司、ESG報告撰寫者"
LANDING_FEATURES = """
- 選擇國際或台灣減碳路徑模型
- 一鍵產出折線圖與年度表格
- 可下載圖＋數據表，直接放進報告
"""

# 圖片放法教學（首頁下方顯示）
IMAGE_TUTORIAL = """
---
**如何放 QR code 圖片：**

將圖片（如 QR code）放在專案 images/ 或 static/ 資料夾，然後：
```python
st.image("images/line_qr.png", width=120)
```
或用網址：
```python
st.image("https://example.com/your_qr.png", width=120)
```
"""

def calc_emission_path(total_emission, baseline_year, residual_ratio, method, years=None):
    if years is None:
        years = 2050 - baseline_year
    emissions = []
    if method == "等比（每年減固定%）":
        # 反推每年減碳率
        final = total_emission * residual_ratio
        rate = 1 - (final / total_emission) ** (1/years)
        current = total_emission
        for i in range(years+1):
            emissions.append(current)
            current *= (1 - rate)
    else:  # 線性
        final = total_emission * residual_ratio
        step = (total_emission - final) / years
        current = total_emission
        for i in range(years+1):
            emissions.append(current)
            current -= step
    return emissions

def calc_s2_path(s2, baseline_year, re50_year, re100_year):
    years = list(range(baseline_year, 2051))
    s2_path = []
    for y in years:
        if y <= re50_year:
            ratio = 1 - 0.5 * (y - baseline_year) / (re50_year - baseline_year)
            s2_path.append(s2 * ratio)
        elif y <= re100_year:
            ratio = 0.5 - 0.5 * (y - re50_year) / (re100_year - re50_year)
            s2_path.append(s2 * ratio)
        else:
            s2_path.append(0)
    return s2_path

def main():
    st.set_page_config(page_title="減碳路徑規劃器 NetZero Path Planner", layout="centered")
    # 首頁邏輯
    if "page" not in st.session_state:
        st.session_state["page"] = "landing"
    if st.session_state["page"] == "landing":
        st.title("Path2Zero 淨零目標模擬器")
        st.markdown("快速產出企業減碳路徑與年度減量目標")
        st.markdown("輸入範疇一與範疇二排放，即可根據 SBTi 與台灣政策模擬 2050 淨零路徑")

        st.markdown("##### 適用對象：中小企業・顧問公司・ESG 報告撰寫者")

        with st.expander("點我查看減碳模擬流程"):
            st.markdown("""
            1. 🔢 **輸入排放資料**：輸入公司範疇一與範疇二的年排放量
            2. 📅 **設定基準年**：選擇排放基準年份
            3. 🎯 **選擇減碳目標**：SBTi 1.5°C or 台灣減碳政策
            4. 🧮 **設定殘留排放比例**：選擇 2050 是否完全淨零
            5. ⚡ **整合再生能源設定**：可選擇 RE50 / RE100
            6. 📈 **產出路徑圖 + 年度表格**：即時生成，可匯出報告使用
            """)

        st.markdown("---")
        st.markdown("### 工具特色")

        st.markdown("""
        <style>
        .feature-container {
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 1em;
            margin-bottom: 2em;
        }
        .feature-box {
            flex: 1;
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            text-align: left;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .feature-box h4 {
            font-size: 1.1rem;
            margin-bottom: 0.6em;
            color: #1E293B;
        }
        .feature-box p {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.4;
        }
        </style>

        <div class="feature-container">
            <div class="feature-box">
                <h4>📘 支援國際 / 台灣減碳模型</h4>
                <p>依據 SBTi 與台灣法規模擬企業減碳路徑</p>
            </div>
            <div class="feature-box">
                <h4>📊 一鍵產出折線圖 + 年度表格</h4>
                <p>可產出 Excel + 圖表資料，一目了然</p>
            </div>
            <div class="feature-box">
                <h4>📥 可下載圖 + 表格直接引用</h4>
                <p>支援報告撰寫、內部簡報直接套用</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚀 開始模擬", use_container_width=True):
            st.session_state["page"] = "tool"

        st.markdown("---")
        st.markdown("#### 聯絡資訊")
        st.markdown("📬 Jon｜Email: jonchang1980@gmail.com ｜ [LinkedIn](https://www.linkedin.com/in/chang-jon-293a72326/) ｜ LINE ID: jianjon")
        st.caption("本工具為 ESG 減碳教育用途，不作為法定查驗依據")
        return
    # 內頁主標題同步風格
    st.markdown(f"""
    <div style='padding:32px 5vw 0 5vw;'>
        <h1 style='color:{TEXT_COLOR};font-family:{FONT_FAMILY};font-size:2.2rem;font-weight:700;margin-bottom:8px;'>Path2Zero - 淨零目標模擬器</h1>
        <div style='color:{SUBTEXT_COLOR};font-size:1.1rem;font-family:{FONT_FAMILY};margin-bottom:18px;'>依據國際 SBTi 與台灣政策，協助企業模擬減碳目標與路徑</div>
    </div>
    """, unsafe_allow_html=True)

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
        # ==== 計算方式選擇 ====
        calc_method = st.radio("減碳路徑計算方式", ["等比（每年減固定%）", "線性（每年減固定量）"], horizontal=True)

        # ==== 2050殘留排放 ====
        residual = st.selectbox("2050年殘留排放比例", ["0%", "5%", "10%"], index=1)
        residual_ratio = {"0%": 0.0, "5%": 0.05, "10%": 0.10}[residual]

        # ==== RE50/RE100設定 ====
        re_option = st.radio("再生能源目標：", ["不採用再生能源目標", "RE50（50%再生電）", "RE100（100%再生電）"], horizontal=True)
        re50_year, re100_year = baseline_year, 2050
        if re_option == "RE50（50%再生電）":
            re50_year = st.number_input("RE50 達成年", min_value=baseline_year+1, max_value=2050, value=2030, key="re50_year")
            re100_enable = True
        elif re_option == "RE100（100%再生電）":
            re100_year = st.number_input("RE100 達成年", min_value=baseline_year+1, max_value=2050, value=2040, key="re100_year")
            re100_enable = True
        else:
            re100_enable = False
        re_col1, re_col2 = st.columns([8, 1])
        with re_col2:
            if 'show_re100_desc' not in st.session_state:
                st.session_state['show_re100_desc'] = False
            if st.button("RE100說明", key="re100_info_sbti"):
                st.session_state['show_re100_desc'] = not st.session_state['show_re100_desc']
        if re100_enable and st.session_state['show_re100_desc']:
            with st.expander("什麼是 RE100？", expanded=True):
                st.markdown(RE100_DESCRIPTION)
        st.subheader("2050年殘留排放比例")
        st.markdown("---")
        st.subheader("近期設定（Short-term）")
        short_years = st.slider("近期年數", min_value=3, max_value=5, value=3)
        short_rate = st.slider("近期每年減碳率(%)", min_value=3.0, max_value=15.0, value=4.2, step=0.1) / 100
        # 計算近期結束後剩餘排放
        short_emission = total_emission * ((1 - short_rate) ** short_years)
        remain_years = 2050 - baseline_year - short_years
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
        # 台灣政策目標路徑
        residual = st.selectbox("2050年殘留排放比例", ["0%", "5%", "10%"], index=1)
        residual_ratio = {"0%": 0.0, "5%": 0.05, "10%": 0.10}[residual]
        # 再生能源目標三選一
        re_option = st.radio("再生能源目標：", ["不採用再生能源目標", "RE50（50%再生電）", "RE100（100%再生電）"], horizontal=True, key="re_radio_tw")
        re50_year, re100_year = baseline_year, 2050
        if re_option == "RE50（50%再生電）":
            re50_year = st.number_input("RE50 達成年", min_value=baseline_year+1, max_value=2050, value=2030, key="re50_year_tw")
            re100_enable = True
        elif re_option == "RE100（100%再生電）":
            re100_year = st.number_input("RE100 達成年", min_value=baseline_year+1, max_value=2050, value=2040, key="re100_year_tw")
            re100_enable = True
        else:
            re100_enable = False
        re_col1, re_col2 = st.columns([8, 1])
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
    show_advanced = st.checkbox("顯示進階解讀（累積減碳、相對基準年減碳%、路徑說明）", value=False)
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
                if calc_method == "線性（每年減固定量）":
                    years = list(range(baseline_year, end_year+1))
                    emissions = calc_emission_path(total_emission, baseline_year, residual_ratio, "線性（每年減固定量）", years=end_year-baseline_year)
                    df = pd.DataFrame({
                        "年度": years,
                        "合併排放": emissions,
                        "範疇1排放": [e/2 for e in emissions],
                        "範疇2排放": [e/2 for e in emissions]
                    })
                else:
                    df = sbti_model.run_sbt1_5(total_emission, baseline_year, end_year, short_years, short_rate, mid_years, mid_rate, long_rate)
                # 若套用 RE100，修改 S2 路徑
                if re100_enable:
                    years = list(df['年度'])
                    s2_path = calc_s2_path(s2, baseline_year, re50_year, re100_year)
                    # 修正長度不符
                    if len(s2_path) > len(years):
                        s2_path = s2_path[:len(years)]
                    elif len(s2_path) < len(years):
                        s2_path += [0] * (len(years) - len(s2_path))
                    df["範疇2排放"] = s2_path
                    df["合併排放"] = df["範疇1排放"] + df["範疇2排放"]
                # 計算減碳量和減碳百分比
                df["減碳量"] = df["合併排放"].shift(1) - df["合併排放"]
                df["減碳百分比"] = (df["減碳量"] / df["合併排放"].shift(1) * 100).round(2)
                df.loc[df.index[0], ["減碳量", "減碳百分比"]] = 0
                # 進階欄位
                if show_advanced:
                    df["累積減碳量"] = (total_emission - df["合併排放"]).round(2)
                    df["相對基準年減碳%"] = ((df["累積減碳量"] / total_emission) * 100).round(2)
                # SBTi專用圖表
                fig = plot.plot_emission_path(df, use_plotly=True, short_years=short_years, mid_years=mid_years, baseline_year=baseline_year)
                st.plotly_chart(fig, use_container_width=True)
                # 進階圖表：年度減碳量
                if show_advanced:
                    import plotly.graph_objects as go
                    bar_fig = go.Figure()
                    bar_fig.add_trace(go.Bar(x=df["年度"], y=df["減碳量"], name="年度減碳量", marker_color="#7ec8e3"))
                    bar_fig.update_layout(title="年度減碳量", xaxis_title="年度", yaxis_title="減碳量 (tCO₂e)", template="plotly_white")
                    st.plotly_chart(bar_fig, use_container_width=True)
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
                # 路徑說明
                if show_advanced:
                    if calc_method == "線性（每年減固定量）":
                        st.markdown(f"""
                        <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                        <b>您選擇的是線性減碳路徑</b>，每年減少固定的排放量，適合有明確年度減碳計畫的企業。<span style='color:{SUBTEXT_COLOR}'>此路徑早期減碳壓力較大，後期壓力較小。</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                        <b>您選擇的是等比減碳路徑</b>，每年減少固定百分比，適合技術進步或政策逐步加嚴的情境。<span style='color:{SUBTEXT_COLOR}'>此路徑早期壓力較小，後期壓力較大。</span>
                        </div>
                        """, unsafe_allow_html=True)
                st.subheader("每年目標排放表")
                formatted_df = df.copy()
                formatted_df = formatted_df[formatted_df['年度'] <= 2050]
                formatted_df["合併排放"] = formatted_df["合併排放"].round(2)
                formatted_df["減碳量"] = formatted_df["減碳量"].round(2)
                formatted_df["減碳百分比"] = formatted_df["減碳百分比"].map(lambda x: f"{x}%" if x != 0 else "-")
                # 進階表格欄位
                if show_advanced:
                    st.dataframe(
                        formatted_df.set_index("年度")[["合併排放", "減碳量", "減碳百分比", "累積減碳量", "相對基準年減碳%"]], 
                        use_container_width=True
                    )
                    # 進階解釋（根據選項顯示對應說明，且只顯示一次）
                    if model == "SBTi 1.5°C":
                        if calc_method == "線性（每年減固定量）":
                            st.markdown(f"""
                            <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                            <b>您選擇的是線性減碳路徑</b>，每年減少固定的排放量，適合有明確年度減碳計畫的企業。<span style='color:{SUBTEXT_COLOR}'>此路徑早期減碳壓力較大，後期壓力較小。</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                            <b>您選擇的是等比減碳路徑</b>，每年減少固定百分比，適合技術進步或政策逐步加嚴的情境。<span style='color:{SUBTEXT_COLOR}'>此路徑早期壓力較小，後期壓力較大。</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                        <b>您選擇的是線性減碳路徑</b>，每年減少固定的排放量，適合有明確年度減碳計畫的企業。<span style='color:{SUBTEXT_COLOR}'>此路徑早期減碳壓力較大，後期較小。</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.dataframe(
                        formatted_df.set_index("年度")[["合併排放", "減碳量", "減碳百分比"]], 
                        use_container_width=True
                    )
                st.download_button("📥 下載CSV", df.to_csv(index=False), file_name="carbon_path.csv")
                st.markdown("<div style='font-size:13px;color:#888;margin-top:8px;'>此路徑模擬由 Path2Zero 工具產出，若需客製化路徑規劃、顧問協助或報告撰寫指導，歡迎聯絡我：your@email.com</div>", unsafe_allow_html=True)
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
                # 若套用 RE50/RE100，修改 S2 路徑
                if re100_enable:
                    years = list(df['年度'])
                    s2_path = calc_s2_path(s2, baseline_year, re50_year, re100_year)
                    # 修正長度不符
                    if len(s2_path) > len(years):
                        s2_path = s2_path[:len(years)]
                    elif len(s2_path) < len(years):
                        s2_path += [0] * (len(years) - len(s2_path))
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
                # 進階表格欄位
                if show_advanced:
                    formatted_df["累積減碳量"] = (total_emission - formatted_df["合併排放"]).round(2)
                    formatted_df["相對基準年減碳%"] = ((formatted_df["累積減碳量"] / total_emission) * 100).round(2)
                    st.dataframe(
                        formatted_df.set_index("年度")["合併排放 減碳量 減碳百分比 累積減碳量 相對基準年減碳%".split()], 
                        use_container_width=True
                    )
                    st.markdown(f"""
                    <div style='background:{CARD_BG};padding:18px 24px;border-radius:8px;color:{TEXT_COLOR};font-size:16px;margin:18px 0;'>
                    <b>您選擇的是線性減碳路徑</b>，每年減少固定的排放量，適合有明確年度減碳計畫的企業。<span style='color:{SUBTEXT_COLOR}'>此路徑早期減碳壓力較大，後期較小。</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.dataframe(
                        formatted_df.set_index("年度")["合併排放 減碳量 減碳百分比".split()], 
                        use_container_width=True
                    )
                st.download_button("📥 下載CSV", df.to_csv(index=False), file_name="taiwan_carbon_path.csv")
                st.markdown("<div style='font-size:13px;color:#888;margin-top:8px;'>此路徑模擬由 Path2Zero 工具產出，若需客製化路徑規劃、顧問協助或報告撰寫指導，歡迎聯絡我：your@email.com</div>", unsafe_allow_html=True)
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