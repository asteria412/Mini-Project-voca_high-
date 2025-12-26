# 경로: features/word_order.py
# 상세 내용: 단어 다중 선택(최대 3개) 후 AI가 문장을 생성하고, 유저가 어순을 맞추는 학습

import streamlit as st
import random
from services.llm import generate_sentence_puzzle
# [중요] 점수 저장을 위한 함수 불러오기
from services.google_sheets import save_score

def show_word_order_page():
    # ---------------------------------------------------------
    # [스타일] 단어 조각 버튼을 '카드'처럼 크고 예쁘게 만들기
    # ---------------------------------------------------------
    st.markdown("""
    <style>
        /* 단어 조각 버튼 공통 스타일 */
        div.stButton > button {
            font-size: 1.1rem !important;
            padding: 0.6rem 0.5rem !important; /* 좌우 여백 줄임 (공간 확보) */
            border-radius: 10px !important;
            margin: 4px 0px;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. 페이지 제목 및 기본 안내
    # ---------------------------------------------------------
    st.subheader("🧩 어순 배열 연습")
    st.caption("단어를 1~3개 선택하면, AI가 그 단어들을 모두 넣은 문장을 만듭니다.")

    # ---------------------------------------------------------
    # 2. 데이터 유효성 검사 (단어장이 업로드되었는지 확인)
    # ---------------------------------------------------------
    if 'final_vocab_df' not in st.session_state or st.session_state['final_vocab_df'] is None:
        st.warning("⚠️ 먼저 [단어시험] 메뉴에서 단어장을 업로드해주세요.")
        return

    df = st.session_state['final_vocab_df']
    
    # ---------------------------------------------------------
    # 3. 세션 상태 초기화
    # ---------------------------------------------------------
    if 'wo_current_puzzle' not in st.session_state:
        st.session_state['wo_current_puzzle'] = None
    if 'wo_user_order' not in st.session_state:
        st.session_state['wo_user_order'] = []
    if 'wo_shuffled_pieces' not in st.session_state:
        st.session_state['wo_shuffled_pieces'] = []

    # ---------------------------------------------------------
    # 4. 연습할 단어 선택 (Multi-Select)
    # ---------------------------------------------------------
    target_words = df[df['선택'] == True]
    
    if target_words.empty:
        st.error("업로드된 단어장에서 '선택'된 단어가 없습니다.")
        return

    word_options = target_words.apply(lambda x: f"{x['zh']} ({x['ko']})", axis=1).tolist()
    
    selected_options = st.multiselect(
        "연습할 단어를 선택하세요 (최대 3개):", 
        word_options,
        placeholder="단어를 검색하거나 선택하세요"
    )
    
    selected_words_zh = [opt.split('(')[0].strip() for opt in selected_options]

    # ---------------------------------------------------------
    # 5. [문제 생성] 버튼 로직
    # ---------------------------------------------------------
    if len(selected_words_zh) > 3:
        st.error(f"🖐️ 욕심쟁이! 단어는 **최대 3개**까지만 선택할 수 있어요. (현재 {len(selected_words_zh)}개)")
        st.button("✨ 선택한 단어들로 문장 만들기 (AI)", disabled=True)
    
    elif len(selected_words_zh) == 0:
        st.info("👆 위 박스에서 단어를 선택하면 문장 생성 버튼이 나타납니다.")
        
    else:
        if st.button("✨ 선택한 단어들로 문장 만들기 (AI)", type="primary"):
            display_words = ", ".join(selected_words_zh)
            with st.spinner(f"'{display_words}'를 모두 넣은 문장을 짓는 중..."):
                
                puzzle_data = generate_sentence_puzzle(selected_words_zh)
                
                if puzzle_data:
                    st.session_state['wo_current_puzzle'] = puzzle_data
                    st.session_state['wo_user_order'] = []
                    
                    pieces = puzzle_data['pieces'][:]
                    random.shuffle(pieces)
                    st.session_state['wo_shuffled_pieces'] = pieces
                else:
                    st.error("AI가 문장을 생성하지 못했습니다. 다시 시도해주세요.")

    st.divider()

    # ---------------------------------------------------------
    # 6. 게임 플레이 영역
    # ---------------------------------------------------------
    puzzle = st.session_state['wo_current_puzzle']
    
    if puzzle:
        st.subheader("한국어 뜻을 보고 어순을 맞추세요.")
        st.info(f"🇰🇷 **해석:** {puzzle['korean']}")

        # =========================================================
        # (A) [수정됨] 유저가 조립 중인 문장 (클릭 시 취소 기능)
        # =========================================================
        st.markdown("### 🔽 완성된 문장 (클릭하면 취소)")
        
        user_ans_list = st.session_state['wo_user_order']
        
        if user_ans_list:
            # 버튼들을 가로로 나열하기 위해 columns 사용
            cols = st.columns(len(user_ans_list))
            for i, word in enumerate(user_ans_list):
                # type="primary"를 줘서 '선택된 상태'임을 시각적으로 강조
                # 클릭 시 리스트에서 해당 인덱스의 단어를 제거(pop)
                if cols[i].button(word, key=f"remove_{i}_{word}", type="primary"):
                    st.session_state['wo_user_order'].pop(i)
                    st.rerun() # 화면 갱신하여 아래쪽 보기로 단어 복귀시킴
        else:
            # 비어있을 때 공간 유지용 텍스트
            st.markdown("""
            <div style='padding: 20px; border: 2px dashed #ddd; border-radius: 10px; text-align: center; color: #aaa;'>
                아래 단어 조각을 클릭하여 문장을 완성하세요
            </div>
            """, unsafe_allow_html=True)

        st.write("") # 여백

        # =========================================================
        # (B) 섞여있는 단어 조각 버튼들 (클릭 시 추가)
        # =========================================================
        st.markdown("### 🔽 단어 조각 (클릭)")
        shuffled = st.session_state['wo_shuffled_pieces']
        
        # 남은 조각 계산: (전체 조각) - (이미 선택된 조각)
        # 단순히 remove로 하면 중복 단어가 있을 때 꼬일 수 있으므로 카운팅 방식이 안전하지만,
        # 여기서는 리스트 복사본에서 하나씩 지워가는 방식으로 구현
        remaining_pieces = shuffled.copy()
        for p in user_ans_list:
            if p in remaining_pieces:
                remaining_pieces.remove(p) 
        
        if remaining_pieces:
            cols = st.columns(len(remaining_pieces))
            for idx, piece in enumerate(remaining_pieces):
                # 기본 스타일(회색) 버튼
                if cols[idx].button(piece, key=f"add_{idx}_{piece}"):
                    st.session_state['wo_user_order'].append(piece)
                    st.rerun()
        else:
            st.markdown("*(모든 조각을 사용했습니다)*")

        st.markdown("---")

        # (C) 하단 컨트롤 버튼
        c1, c2 = st.columns(2)
        
        # [다시 하기]
        if c1.button("🔄 전체 초기화"):
            st.session_state['wo_user_order'] = []
            st.rerun()
            
        # [정답 확인]
        if c2.button("✅ 정답 확인"):
            user_sentence = "".join(st.session_state['wo_user_order'])
            correct_sentence = puzzle['chinese']
            
            import re
            user_clean = re.sub(r'[^\w]', '', user_sentence)
            corr_clean = re.sub(r'[^\w]', '', correct_sentence)

            if user_clean == corr_clean:
                st.balloons()
                st.success("🎉 정답입니다! 완벽해요.")
                st.markdown(f"**문장:** {puzzle['chinese']}")
                st.markdown(f"**병음:** {puzzle['pinyin']}")
                
                # [점수 저장]
                nickname = st.session_state.get("nickname", "")
                if nickname:
                    save_score(nickname, "어순 연습", 100)
                    st.toast(f"💾 {nickname}님의 점수(100점)가 저장되었습니다!", icon="✅")
                else:
                    st.warning("⚠️ 별명이 입력되지 않아 점수가 저장되지 않았습니다. (사이드바에서 별명을 설정하세요)")
                
            else:
                st.error("앗! 틀렸습니다.")
                with st.expander("정답 보기"):
                    st.write(f"**정답 문장:** {puzzle['chinese']}")
                    st.write(f"**병음:** {puzzle['pinyin']}")