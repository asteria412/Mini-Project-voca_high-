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

    # [수정] 제목에 PDF뿐만 아니라 TXT도 명시
    st.subheader("📄 시험 범위 설정 (PDF / TXT)")
    
    # [수정] 도움말 추가: TXT 파일 업로드 안내
    uploaded_file = st.file_uploader(
        "단어장 파일을 올려주세요.", 
        type=["pdf", "txt"], 
        key="vocab_uploader",
        help="PDF 파일이나 '단어 - 뜻' 형식으로 정리된 TXT 파일을 지원합니다."
    )

    # 1. 파일을 새로 올렸을 때만 분석 로직 실행
    if uploaded_file:
        if st.session_state.get('uploaded_filename') != uploaded_file.name:
            if 'final_vocab_df' in st.session_state:
                del st.session_state['final_vocab_df']

        if 'final_vocab_df' not in st.session_state:
            with st.spinner(f"'{uploaded_file.name}' 파일을 분석 중입니다..."):
                # core/text_change.py가 확장자에 따라 자동으로 텍스트를 추출합니다.
                text = change_text_from_upload(uploaded_file)
                parsed_df = change_text_to_vocab_df(text, level="HSK", source=uploaded_file.name)
            
            n_parsed = len(parsed_df)
            n_missing = len(parsed_df[parsed_df['flags'] != 'OK'])
            
            if n_missing > 0:
                st.info(f"📊 `{n_parsed}`개 항목 중 빈칸 `{n_missing}`개를 발견하여 AI가 수리를 시작합니다.")
                final_df = process_vocab_with_llm(parsed_df, text)
            else:
                final_df = parsed_df

            if '선택' not in final_df.columns:
                final_df.insert(0, '선택', True)

            st.session_state['final_vocab_df'] = final_df
            st.session_state['uploaded_filename'] = uploaded_file.name
            st.toast("✨ 분석 완료!")

    # ---------------------------------------------------------
    # 데이터가 있을 때 파일명과 목록 노출
    # ---------------------------------------------------------
    if st.session_state.get('final_vocab_df') is not None:
        current_fname = st.session_state.get('uploaded_filename', '알 수 없는 파일')
        st.success(f"📂 **현재 불러온 파일:** `{current_fname}`")

        st.warning("""
        **📢 이용 안내**
        * 시스템이 AI와 로직으로 반복 체크하지만, 실제 단어 수와 차이가 있을 수 있습니다.
        * 아래 **미리보기 목록을 펼쳐서** 형식이 이상하거나 잘못된 단어는 직접 수정하거나 
          체크박스 해제하여 제외가 가능합니다.
        """)

        with st.expander(f"👁️ [{current_fname}] 단어 목록 보기 및 수정 (클릭)", expanded=False):
            df_to_show = st.session_state['final_vocab_df']
            st.markdown(f"👇 **총 {len(df_to_show)}개의 항목이 검색되었습니다. 오타를 직접 클릭해서 고쳐보세요.**")
            
            edited_df = st.data_editor(
                df_to_show, 
                column_config={
                    "선택": st.column_config.CheckboxColumn(
                        "시험 포함",
                        help="시험에 포함할 단어만 체크하세요.",
                        default=True,
                    )
                },
                use_container_width=True, 
                key="vocab_editor_final", 
                height=400,
                num_rows="dynamic" 
            )
            
            st.session_state['final_vocab_df'] = edited_df

        if st.button("🚀 선택한 단어로 시험 시작하기", type="primary", use_container_width=True):
            selected_vocab = st.session_state['final_vocab_df'][st.session_state['final_vocab_df']['선택'] == True].copy()
            
            if selected_vocab.empty:
                st.error("시험을 볼 단어를 하나 이상 선택해 주세요!")
            else:
                st.session_state['quiz_vocab'] = selected_vocab
                st.session_state['quiz_status'] = 'playing' 
                st.balloons() 
                st.rerun()
    else:
        st.info("💡 단어장 파일(PDF 또는 TXT)을 먼저 업로드해 주세요.")