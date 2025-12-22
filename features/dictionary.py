# 경로: features/dictionary.py
# [업그레이드] 
# 1. 한국어 뜻(ko) 부분 일치 검색 지원 (예: '아끼다' -> '爱惜', '爱护' 모두 검색)
# 2. 내 단어장 결과가 있어도, 추가로 AI에게 물어볼 수 있는 버튼 배치

import streamlit as st
import pandas as pd
from services.llm import search_word_info

def show_dictionary_page():
    st.subheader("📚 AI 단어사전")
    st.caption("내 단어장과 AI 지식을 동시에 활용하세요.")

    # 1. 내 단어장 데이터 준비
    my_vocab = []
    if 'final_vocab_df' in st.session_state and st.session_state['final_vocab_df'] is not None:
        my_vocab = st.session_state['final_vocab_df'].to_dict('records')

    # 2. 검색 인터페이스
    col1, col2 = st.columns([4, 1])
    with col1:
        keyword = st.text_input("검색할 단어 (한자 or 한국어 뜻)", placeholder="예: 아끼다 / 节约", label_visibility="collapsed").strip()
    with col2:
        search_btn = st.button("검색", use_container_width=True)

    # 엔터를 치거나 검색 버튼을 눌렀을 때 실행
    if keyword:
        st.divider()
        
        # ---------------------------------------------------------
        # [Step 1] 내 단어장에서 찾기 (부분 일치 검색)
        # ---------------------------------------------------------
        # 한자(zh)에 포함되거나 OR 한국어 뜻(ko)에 포함되면 다 가져옴
        local_matches = [
            item for item in my_vocab 
            if keyword in item.get('zh', '') or keyword in str(item.get('ko', ''))
        ]
        
        if local_matches:
            st.success(f"✅ **내 단어장**에서 {len(local_matches)}개를 찾았습니다!")
            
            for item in local_matches:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.subheader(item['zh'])
                        if item.get('pinyin'):
                            st.markdown(f"**[{item['pinyin']}]**")
                    with c2:
                         if item.get('pos'):
                            st.caption(f"🏷️ {item['pos']}")
                    
                    st.markdown(f"💡 **뜻:** {item['ko']}")
        else:
            st.info("내 단어장에는 일치하는 단어가 없습니다.")

        # ---------------------------------------------------------
        # [Step 2] AI 검색 (결과 유무와 상관없이 항상 표시)
        # ---------------------------------------------------------
        st.markdown("---")
        st.caption("찾으시는 단어가 아니거나 더 자세한 정보가 필요하신가요?")
        
        # 버튼을 누르면 AI 검색 시작
        if st.button(f"🤖 AI에게 '{keyword}' 상세 검색 요청", type="primary", use_container_width=True):
            with st.spinner(f"AI가 '{keyword}'의 최신 용례와 뜻을 분석 중입니다..."):
                ai_result = search_word_info(keyword)
                
                if ai_result:
                    st.divider()
                    st.markdown(f"## {ai_result['word']}")
                    
                    # 병음과 품사 표시
                    c1, c2 = st.columns([1, 4])
                    with c1:
                         st.markdown(f"**[{ai_result['pinyin']}]**")
                    with c2:
                         st.caption(f"🏷️ 품사: **{ai_result.get('pos', '미상')}**")
                    
                    st.markdown(f"### 💡 뜻: {ai_result['meaning']}")
                    
                    st.info("📝 **AI 추천 예문**")
                    st.write(ai_result['example_cn'])
                    st.caption(ai_result['example_kr'])
                else:
                    st.error("AI 검색 결과를 가져오지 못했습니다. 다시 시도해주세요.")