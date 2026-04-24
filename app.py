import streamlit as st
import pandas as pd
import datetime

# --- 頁面與全域設定 ---
st.set_page_config(page_title="神經內科 DAPT 臨床決策調查", layout="centered", initial_sidebar_state="collapsed")

# 自定義 CSS 優化平板觸控體驗
st.markdown("""
    <style>
    .stRadio > label { font-size: 18px; font-weight: bold; }
    .stRadio > div { gap: 15px; }
    .big-font { font-size:22px !important; font-weight: bold; color: #1f77b4; margin-bottom: 10px;}
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 狀態管理 (Session State) ---
# 控制頁面跳轉與紀錄答案
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {'q1': [], 'q2': '', 'q3': '', 'q3_other': '', 'q4': ''}
if 'db' not in st.session_state:
    st.session_state.db = [] # 用來暫存多位醫師的資料

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_survey():
    st.session_state.step = 0
    st.session_state.answers = {'q1': [], 'q2': '', 'q3': '', 'q3_other': '', 'q4': ''}

# --- 主程式 ---
def main():
    # 顯示進度條 (除了首頁和完成頁)
    if 0 < st.session_state.step < 5:
        st.progress(st.session_state.step / 4)
        st.caption(f"進度 {st.session_state.step} / 4")

    # [Step 0] 歡迎頁
    if st.session_state.step == 0:
        st.title("📊 神經內科 DAPT 臨床決策調查")
        st.info("醫師您好，感謝您撥冗 **30秒** 協助我們了解最新的臨床實務現況。您的寶貴意見將幫助我們提供更符合需求的醫藥服務。")
        st.write("")
        if st.button("開始調查 👉", type="primary", use_container_width=True):
            next_step()
            st.rerun()
            
        st.divider()
        with st.expander("⚙️ MR 資料中心 (內部專用)"):
            st.write(f"目前已收集: **{len(st.session_state.db)}** 筆資料")
            if len(st.session_state.db) > 0:
                df = pd.DataFrame(st.session_state.db)
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8-sig') # utf-8-sig 確保 Excel 開啟中文不亂碼
                st.download_button("📥 下載 CSV", data=csv, file_name="dapt_survey.csv", mime="text/csv", use_container_width=True)

    # [Step 1] Q1
    elif st.session_state.step == 1:
        st.markdown('<p class="big-font">Q1. 針對急性缺血性腦中風，您最常啟動 DAPT 的情境是？(可複選)</p>', unsafe_allow_html=True)
        q1_opts = ["輕度中風 (Minor Stroke)", "高風險 TIA", "顱內大血管狹窄", "其他特定高風險族群"]
        st.session_state.answers['q1'] = st.multiselect("請點選符合的情境：", options=q1_opts, default=st.session_state.answers['q1'])
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=len(st.session_state.answers['q1'])==0): next_step(); st.rerun()

    # [Step 2] Q2
    elif st.session_state.step == 2:
        st.markdown('<p class="big-font">Q2. 您最常開立的 DAPT 組合為何？(單選)</p>', unsafe_allow_html=True)
        q2_opts = ["Aspirin + Clopidogrel (傳統經典)", "Aspirin + Ticagrelor (針對高風險/抗藥性)", "Aspirin + Cilostazol (考量出血/亞裔)"]
        
        # 預設選取邏輯
        idx = q2_opts.index(st.session_state.answers['q2']) if st.session_state.answers['q2'] in q2_opts else None
        st.session_state.answers['q2'] = st.radio("請選擇：", options=q2_opts, index=idx)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not st.session_state.answers['q2']): next_step(); st.rerun()

    # [Step 3] Q3
    elif st.session_state.step == 3:
        st.markdown('<p class="big-font">Q3. 在 DAPT 療程中，您通常何時會降階為 SAPT？(單選)</p>', unsafe_allow_html=True)
        q3_opts = ["21 天 (依循 CHANCE/POINT)", "30 天 (依循 THALES)", "90 天", "其他 (請自行輸入)"]
        
        idx = q3_opts.index(st.session_state.answers['q3']) if st.session_state.answers['q3'] in q3_opts else None
        st.session_state.answers['q3'] = st.radio("請選擇：", options=q3_opts, index=idx)
        
        # 如果選擇其他，跳出輸入框
        if st.session_state.answers['q3'] == "其他 (請自行輸入)":
            st.session_state.answers['q3_other'] = st.text_input("請輸入您的考量或天數：", value=st.session_state.answers['q3_other'])
            can_proceed = bool(st.session_state.answers['q3_other'].strip())
        else:
            can_proceed = bool(st.session_state.answers['q3'])

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not can_proceed): next_step(); st.rerun()

    # [Step 4] Q4
    elif st.session_state.step == 4:
        st.markdown('<p class="big-font">Q4. 影響您提早停用 DAPT 的最大顧慮是？(單選)</p>', unsafe_allow_html=True)
        q4_opts = ["嚴重出血風險 (Major Bleeding/ICH)", "微小出血 / 瘀青 / 腸胃不適", "病人順從性不佳 (BID 劑型)", "健保給付考量 / 審查"]
        
        idx = q4_opts.index(st.session_state.answers['q4']) if st.session_state.answers['q4'] in q4_opts else None
        st.session_state.answers['q4'] = st.radio("請選擇：", options=q4_opts, index=idx)

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("送出調查！", type="primary", disabled=not st.session_state.answers['q4']): 
                next_step()
                st.rerun()

    # [Step 5] 完成頁
    elif st.session_state.step == 5:
        st.success("✅ 感謝醫師的寶貴意見！資料已成功送出。")
        st.balloons()
        
        # 整理最終答案
        final_q3 = st.session_state.answers['q3_other'] if st.session_state.answers['q3'] == "其他 (請自行輸入)" else st.session_state.answers['q3']
        
        # 確保不要重複存入 (利用 Session 狀態防呆)
        if 'saved' not in st.session_state:
            record = {
                "時間": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Q1_情境": ", ".join(st.session_state.answers['q1']),
                "Q2_藥物": st.session_state.answers['q2'],
                "Q3_療程": final_q3,
                "Q4_顧慮": st.session_state.answers['q4']
            }
            st.session_state.db.append(record)
            st.session_state.saved = True # 標記為已存

        st.write("---")
        st.caption("MR 紀錄區 (可截圖)")
        st.write(f"**Q1:** {', '.join(st.session_state.answers['q1'])}")
        st.write(f"**Q2:** {st.session_state.answers['q2']}")
        st.write(f"**Q3:** {final_q3}")
        st.write(f"**Q4:** {st.session_state.answers['q4']}")
        
        st.write("---")
        if st.button("🔄 返回首頁 (準備下一位)", type="primary"):
            del st.session_state['saved'] # 清除儲存標記
            reset_survey()
            st.rerun()

if __name__ == "__main__":
    main()
