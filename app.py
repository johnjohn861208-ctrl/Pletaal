```python
import streamlit as st
import pandas as pd
import datetime

# --- 頁面與全域設定 ---
st.set_page_config(page_title="神經內科 DAPT 臨床決策調查", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stRadio > label { font-size: 18px; font-weight: bold; }
    .stRadio > div { gap: 15px; }
    .big-font { font-size:22px !important; font-weight: bold; color: #1f77b4; margin-bottom: 15px;}
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* 新增：為突破題加上微微的背景色，吸引注意力 */
    .highlight-q { background-color: #f0f7ff; padding: 20px; border-radius: 15px; border-left: 5px solid #1f77b4;}
    </style>
""", unsafe_allow_html=True)

# --- 狀態管理 ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {'q1': [], 'q2': '', 'q3': '', 'q3_other': '', 'q4': '', 'q5': '', 'q6': ''}
if 'db' not in st.session_state: st.session_state.db = []
if 'current_saved' not in st.session_state: st.session_state.current_saved = False

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1
def reset_survey():
    st.session_state.step = 0
    st.session_state.answers = {'q1': [], 'q2': '', 'q3': '', 'q3_other': '', 'q4': '', 'q5': '', 'q6': ''}
    st.session_state.current_saved = False

# --- 主程式 ---
def main():
    total_steps = 6 # 總共 6 題
    if 0 < st.session_state.step <= total_steps:
        st.progress(st.session_state.step / total_steps)
        st.caption(f"進度 {st.session_state.step} / {total_steps}")

    # [Step 0] 歡迎頁
    if st.session_state.step == 0:
        st.title("📊 神經內科 DAPT 臨床決策調查")
        st.info("醫師您好，感謝您撥冗 **1分鐘** 協助我們了解最新的臨床實務現況。您的寶貴意見將幫助我們提供更符合需求的醫藥服務。")
        st.write("")
        if st.button("開始調查 👉", type="primary", use_container_width=True):
            next_step(); st.rerun()

    # [Step 1] Q1: 啟動情境
    elif st.session_state.step == 1:
        st.markdown('<p class="big-font">Q1. 針對急性缺血性腦中風，您最常啟動 DAPT 的情境是？(可複選)</p>', unsafe_allow_html=True)
        q1_opts = ["輕度中風 (Minor Stroke)", "高風險 TIA", "顱內大血管狹窄", "合併周邊動脈阻塞 (PAOD)", "小血管疾病 (SVD) / 腔隙性腦梗塞", "其他"]
        st.session_state.answers['q1'] = st.pills("請點選符合的情境：", options=q1_opts, default=st.session_state.answers['q1'], selection_mode="multi")
        
        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not st.session_state.answers['q1']): next_step(); st.rerun()

    # [Step 2] Q2: 藥物選擇
    elif st.session_state.step == 2:
        st.markdown('<p class="big-font">Q2. 您最常開立的 DAPT 組合為何？(單選)</p>', unsafe_allow_html=True)
        q2_opts = ["Aspirin + Clopidogrel (傳統經典)", "Aspirin + Ticagrelor (針對高風險/抗藥性)", "Aspirin + Cilostazol (考量出血/亞裔/SVD)"]
        idx = q2_opts.index(st.session_state.answers['q2']) if st.session_state.answers['q2'] in q2_opts else None
        st.session_state.answers['q2'] = st.radio("請點選：", options=q2_opts, index=idx)
        
        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not st.session_state.answers['q2']): next_step(); st.rerun()

    # [Step 3] Q3: 降階時機
    elif st.session_state.step == 3:
        st.markdown('<p class="big-font">Q3. 在 DAPT 療程中，您通常何時會降階為 SAPT？(單選)</p>', unsafe_allow_html=True)
        q3_opts = ["21 天 (依循 CHANCE/POINT)", "30 天 (依循 THALES)", "90 天", "其他情況 (請自行輸入)"]
        idx = q3_opts.index(st.session_state.answers['q3']) if st.session_state.answers['q3'] in q3_opts else None
        st.session_state.answers['q3'] = st.radio("請點選：", options=q3_opts, index=idx)
        
        if st.session_state.answers['q3'] == "其他情況 (請自行輸入)":
            st.session_state.answers['q3_other'] = st.text_input("請輸入您的考量或天數：", value=st.session_state.answers['q3_other'])
            can_proceed = bool(st.session_state.answers['q3_other'].strip())
        else:
            can_proceed = bool(st.session_state.answers['q3'])

        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not can_proceed): next_step(); st.rerun()

    # [Step 4] Q4: 停藥顧慮
    elif st.session_state.step == 4:
        st.markdown('<p class="big-font">Q4. 影響您提早停用 DAPT 的最大顧慮是？(單選)</p>', unsafe_allow_html=True)
        q4_opts = ["嚴重出血風險 (Major Bleeding/ICH)", "微小出血 / 瘀青 / 腸胃不適", "病人順從性不佳 (BID 劑型)", "健保給付考量 / 審查"]
        idx = q4_opts.index(st.session_state.answers['q4']) if st.session_state.answers['q4'] in q4_opts else None
        st.session_state.answers['q4'] = st.radio("請點選：", options=q4_opts, index=idx)

        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not st.session_state.answers['q4']): next_step(); st.rerun()

    # [Step 5] Q5: 突破題 1 (挑戰單抗極限與長期雙抗契機)
    elif st.session_state.step == 5:
        st.markdown('<div class="highlight-q"><p class="big-font" style="margin-bottom:0;">Q5. 若病人在急性期後已「降階為單抗 (SAPT)」，但在追蹤時影像學發現『新的無症狀性腦梗塞 (SBI)』或『血管狹窄加劇』，您的處置傾向為？</p></div>', unsafe_allow_html=True)
        st.write("") 
        q5_opts = [
            "維持 SAPT，但加強血壓與血脂的控制", 
            "換另一種 SAPT (例如：Aspirin 換 Clopidogrel)", 
            "重啟為「長期 DAPT」，並選擇出血風險較低的組合", 
            "考慮轉介介入治療 (如：血管內支架)"
        ]
        idx = q5_opts.index(st.session_state.answers['q5']) if st.session_state.answers['q5'] in q5_opts else None
        st.session_state.answers['q5'] = st.radio("請點選您的實務經驗：", options=q5_opts, index=idx)

        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("下一題", type="primary", disabled=not st.session_state.answers['q5']): next_step(); st.rerun()

    # [Step 6] Q6: 突破題 2 (安全性與療程延長)
    elif st.session_state.step == 6:
        st.markdown('<div class="highlight-q"><p class="big-font" style="margin-bottom:0;">Q6. 對於「極高復發風險」的病人，若有一種 DAPT 組合證實『不增加嚴重出血風險』，您是否考慮延長療程 (超過 30 天)？</p></div>', unsafe_allow_html=True)
        st.write("")
        q6_opts = ["會，安全無虞下願意延長，以降低復發", "不會，仍會嚴格遵守 21/30 天的 Guideline", "視病人回診時的影像學變化決定"]
        idx = q6_opts.index(st.session_state.answers['q6']) if st.session_state.answers['q6'] in q6_opts else None
        st.session_state.answers['q6'] = st.radio("請點選您的意願：", options=q6_opts, index=idx)

        st.write("")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("返回"): prev_step(); st.rerun()
        with col2:
            if st.button("送出調查！", type="primary", disabled=not st.session_state.answers['q6']): 
                next_step(); st.rerun()

    # [Step 7] 完成頁與 MR 後台
    elif st.session_state.step == 7:
        st.success("✅ 感謝醫師的寶貴意見！資料已成功送出。")
        st.balloons()
        st.write("---")
        
        # === 🔒 MR 專屬操作區 ===
        with st.expander("🔒 MR 內部紀錄 (請自行填寫客戶資料)", expanded=True):
            hcp_name = st.text_input("醫師姓名 (必填)", placeholder="例如：林主任")
            hcp_hospital = st.text_input("醫院/診所名稱", placeholder="例如：台大醫院")
            
            if st.button("💾 儲存這筆紀錄", type="primary", disabled=not hcp_name):
                if not st.session_state.current_saved:
                    final_q3 = st.session_state.answers['q3_other'] if st.session_state.answers['q3'] == "其他情況 (請自行輸入)" else st.session_state.answers['q3']
                    
                    record = {
                        "時間": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "醫院": hcp_hospital,
                        "醫師": hcp_name,
                        "Q1_情境": ", ".join(st.session_state.answers['q1']),
                        "Q2_藥物": st.session_state.answers['q2'],
                        "Q3_療程": final_q3,
                        "Q4_停藥顧慮": st.session_state.answers['q4'],
                        "Q5_SAPT盲區處置": st.session_state.answers['q5'],
                        "Q6_延長意願": st.session_state.answers['q6']
                    }
                    st.session_state.db.append(record)
                    st.session_state.current_saved = True
                    st.success(f"已成功儲存 {hcp_name} 醫師的資料！")
                else:
                    st.warning("這筆資料剛剛已經存過囉！請返回首頁準備下一位。")
            
            st.divider()
            if st.button("🔄 準備下一位 (回到首頁)"):
                reset_survey(); st.rerun()
                
            st.divider()
            st.markdown("### 📊 資料中心")
            st.write(f"目前總共收集: **{len(st.session_state.db)}** 筆資料")
            if len(st.session_state.db) > 0:
                df = pd.DataFrame(st.session_state.db)
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下載所有資料 (CSV)", data=csv, file_name="dapt_survey_data.csv", mime="text/csv", use_container_width=True)

if __name__ == "__main__":
    main()


```
