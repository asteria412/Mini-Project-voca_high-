# 경로: features/vocab_upload.py
import streamlit as st
import pandas as pd
from core.text_change import change_text_from_upload
from core.vocab_parser import change_text_to_vocab_df
from services.llm import process_vocab_with_llm

def show_vocab_upload():
    if st.session_state.get('quiz_status') == 'playing':
        st.info("🎯 단어장 준비가 완료되었습니다!")
        if st.button("새로운 단어장 만들기"):
            st.session_state['quiz_status'] = 'ready'
            st.rerun()
        return

    st.subheader("📄 시험 범위 설정 (PDF)")
    uploaded_file = st.file_uploader("단어장 파일을 올려주세요.", type=["pdf", "txt"], key="vocab_uploader")

    if uploaded_file:
        if st.session_state.get('uploaded_filename') != uploaded_file.name:
            if 'final_vocab_df' in st.session_state:
                del st.session_state['final_vocab_df']

        if 'final_vocab_df' not in st.session_state:
            with st.spinner("단어장을 분석 중입니다..."):
                text = change_text_from_upload(uploaded_file)
                parsed_df = change_text_to_vocab_df(text, level="HSK", source=uploaded_file.name)
            
            n_parsed = len(parsed_df)
            n_missing = len(parsed_df[parsed_df['flags'] != 'OK'])
            
            # 빈칸이 있으면 AI가 1차 수리를 진행
            if n_missing > 0:
                st.info(f"📊 `{n_parsed}`개 항목 중 빈칸 `{n_missing}`개를 발견하여 AI가 1차 수리를 시작합니다.")
                final_df = process_vocab_with_llm(parsed_df, text)
            else:
                final_df = parsed_df

            # [핵심] 유저가 직접 선택할 수 있도록 '선택' 컬럼 추가
            if '선택' not in final_df.columns:
                final_df.insert(0, '선택', True) # 기본값은 모두 체크됨

            st.session_state['final_vocab_df'] = final_df
            st.session_state['uploaded_filename'] = uploaded_file.name
            st.toast("✨ 분석 완료!")

        # ---------------------------------------------------------
        # ⚠️ [회원님 요청] 현실적인 안내 문구 추가
        # ---------------------------------------------------------
        st.warning("""
        **📢 이용 안내**
        * 시스템이 AI와 로직으로 두세 번 체크하지만, 파일 형식에 따라 실제 단어 수와 차이가 있을 수 있습니다.
        * 아래 미리보기에서 형식이 이상한 단어는 **'선택' 체크박스를 해제**해 주세요.
        * 단어장 형식에 따라 **품사(pos) 분류**가 지원되지 않을 수 있습니다.
        """)

        df_to_show = st.session_state['final_vocab_df']
        st.markdown(f"👇 **총 {len(df_to_show)}개의 항목이 검색되었습니다.**")
        
        # [구조 변경] 유저가 체크박스로 시험 볼 단어만 선택하는 에디터
        edited_df = st.data_editor(
            df_to_show, 
            column_config={
                "선택": st.column_config.CheckboxColumn(
                    "시험 포함",
                    help="시험에 포함할 단어만 체크하세요.",
                    default=True,
                )
            },
            disabled=["flags"], # flags는 유저가 수정할 필요 없음
            use_container_width=True, 
            key="vocab_editor_final", 
            height=400
        )
        
        # ---------------------------------------------------------
        # 🚀 시험 시작 로직 (선택된 단어만 필터링)
        # ---------------------------------------------------------
        if st.button("🚀 선택한 단어로 시험 시작하기", type="primary", use_container_width=True):
            # '선택' 컬럼이 True인 단어만 골라냄
            selected_vocab = edited_df[edited_df['선택'] == True].copy()
            
            if selected_vocab.empty:
                st.error("시험을 볼 단어를 하나 이상 선택해 주세요!")
            else:
                st.session_state['quiz_vocab'] = selected_vocab
                st.session_state['quiz_status'] = 'playing' 
                st.balloons() 
                st.rerun()