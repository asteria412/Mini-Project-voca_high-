# 경로: features/word_order.py
# 기능: 단어를 선택하면 AI가 문장을 만들어 쪼개주고, 유저가 순서를 맞추는 학습

import streamlit as st
import random
from services.llm import generate_sentence_puzzle

def show_word_order_page():
    st.title("🧩 어순 배열 연습")
    st.caption("단어를 선택하면 AI가 문장을 만듭니다. 순서를 맞춰보세요!")

    # 1. 단어장 데이터 확인
    if 'final_vocab_df' not in st.session_state or st.session_state['final_vocab_df'] is None:
        st.warning("⚠️ 먼저 [단어시험] 메뉴에서 단어장을 업로드해주세요.")
        return

    df = st.session_state['final_vocab_df']
    
    # 2. 문제 출제용 세션 초기화
    if 'wo_current_puzzle' not in st.session_state:
        st.session_state['wo_current_puzzle'] = None # 현재 문제 데이터
    if 'wo_user_order' not in st.session_state:
        st.session_state['wo_user_order'] = []     # 유저가 클릭한 순서
    if 'wo_shuffled_pieces' not in st.session_state:
        st.session_state['wo_shuffled_pieces'] = [] # 섞인 보기 버튼들

    # 3. 사이드바 or 상단에서 연습할 단어 선택
    # "선택"된 단어 중에서만 고르게 필터링
    target_words = df[df['선택'] == True]
    if target_words.empty:
        st.error("선택된 단어가 없습니다.")
        return

    # 단어 리스트 만들기 (한자 - 뜻)
    word_options = target_words.apply(lambda x: f"{x['zh']} ({x['ko']})", axis=1).tolist()
    selected_option = st.selectbox("연습할 단어를 고르세요:", word_options)
    
    # 선택된 문자열에서 한자만 추출 (예: "老师 (선생님)" -> "老师")
    selected_word = selected_option.split('(')[0].strip()

    # ---------------------------------------------------------
    # 4. [문제 생성] 버튼
    # ---------------------------------------------------------
    if st.button("✨ 이 단어로 문장 만들기 (AI)", type="primary"):
        with st.spinner(f"'{selected_word}'(으)로 문장을 짓고 쪼개는 중..."):
            puzzle_data = generate_sentence_puzzle(selected_word)
            
            if puzzle_data:
                st.session_state['wo_current_puzzle'] = puzzle_data
                st.session_state['wo_user_order'] = [] # 정답 초기화
                
                # 조각 섞기
                pieces = puzzle_data['pieces'][:]
                random.shuffle(pieces)
                st.session_state['wo_shuffled_pieces'] = pieces
            else:
                st.error("문제 생성에 실패했습니다. 다시 시도해주세요.")

    st.divider()

    # ---------------------------------------------------------
    # 5. 게임 영역 (문제가 있을 때만 표시)
    # ---------------------------------------------------------
    puzzle = st.session_state['wo_current_puzzle']
    
    if puzzle:
        st.subheader("한국어 뜻을 보고 어순을 맞추세요.")
        st.info(f"🇰🇷 **해석:** {puzzle['korean']}")

        # (A) 유저가 맞추고 있는 답안 표시 영역
        user_ans_list = st.session_state['wo_user_order']
        st.markdown("### 🔽 완성된 문장")
        
        # 유저가 클릭한 단어들을 이쁘게 나열
        if user_ans_list:
            st.success(" ".join(user_ans_list))
        else:
            st.markdown("*(아래 버튼을 눌러서 문장을 완성하세요)*")

        st.markdown("---")

        # (B) 섞인 단어 버튼들 (클릭하면 답안으로 이동)
        st.markdown("### 🔽 단어 조각 (클릭)")
        
        # 버튼들을 여러 줄로 배치
        shuffled = st.session_state['wo_shuffled_pieces']
        
        # 아직 답안에 들어가지 않은(남은) 조각만 보여주기
        # (중복 단어가 있을 수 있으니 개수를 카운트해서 처리하는 게 정석이지만, 
        #  간단하게 구현하기 위해 '남은 리스트'를 관리하는 방식 사용)
        
        # 화면에 그릴 컬럼 계산
        cols = st.columns(len(shuffled)) if len(shuffled) > 0 else [st.container()]
        
        # enumerate를 쓰지 않고, 리스트 복사본을 만들어 처리
        remaining_pieces = shuffled.copy()
        for p in user_ans_list:
            if p in remaining_pieces:
                remaining_pieces.remove(p)
        
        # 남은 조각만 버튼으로 생성
        if remaining_pieces:
            cols = st.columns(len(remaining_pieces))
            for idx, piece in enumerate(remaining_pieces):
                if cols[idx].button(piece, key=f"btn_{piece}_{idx}"):
                    # 버튼 누르면 유저 답안 리스트에 추가
                    st.session_state['wo_user_order'].append(piece)
                    st.rerun() # 화면 갱신
        else:
            st.markdown("*(모든 조각을 사용했습니다)*")

        st.markdown("---")

        # (C) 컨트롤 버튼 (초기화 / 정답확인)
        c1, c2 = st.columns(2)
        if c1.button("🔄 다시 하기"):
            st.session_state['wo_user_order'] = []
            st.rerun()
            
        if c2.button("✅ 정답 확인"):
            # 정답 판별
            user_sentence = "".join(st.session_state['wo_user_order']).replace(" ", "")
            correct_sentence = puzzle['chinese'].replace(" ", "")
            
            # 띄어쓰기/문장부호 무시하고 글자만 비교
            import re
            user_clean = re.sub(r'[^\w]', '', user_sentence)
            corr_clean = re.sub(r'[^\w]', '', correct_sentence)

            if user_clean == corr_clean:
                st.balloons()
                st.success("🎉 정답입니다! 완벽해요.")
                st.markdown(f"**병음:** {puzzle['pinyin']}")
            else:
                st.error("앗! 틀렸습니다.")
                with st.expander("정답 보기"):
                    st.write(f"**정답 문장:** {puzzle['chinese']}")
                    st.write(f"**병음:** {puzzle['pinyin']}")