# 경로: features/word_order.py
# 상세 내용: 단어 다중 선택(최대 3개) 후 AI가 문장을 생성하고, 유저가 어순을 맞추는 학습
# [수정] max_selections 경고창 대신 부드러운 버튼 제어 방식 적용

import streamlit as st
import random
from services.llm import generate_sentence_puzzle

def show_word_order_page():
    # ---------------------------------------------------------
    # 1. 페이지 제목 및 기본 안내
    # ---------------------------------------------------------
    st.title("🧩 어순 배열 연습")
    st.caption("단어를 1~3개 선택하면, AI가 그 단어들을 모두 넣은 문장을 만듭니다.")

    # ---------------------------------------------------------
    # 2. 데이터 유효성 검사 (단어장이 업로드되었는지 확인)
    # ---------------------------------------------------------
    # 세션에 'final_vocab_df'가 없으면 아직 단어장을 올리지 않은 상태입니다.
    if 'final_vocab_df' not in st.session_state or st.session_state['final_vocab_df'] is None:
        st.warning("⚠️ 먼저 [단어시험] 메뉴에서 단어장을 업로드해주세요.")
        return # 더 이상 진행하지 않고 함수 종료

    df = st.session_state['final_vocab_df']
    
    # ---------------------------------------------------------
    # 3. 세션 상태 초기화 (문제 풀이 도중 데이터 유지용)
    # ---------------------------------------------------------
    # 현재 생성된 문제 데이터 (문장, 해석, 병음, 조각들)
    if 'wo_current_puzzle' not in st.session_state:
        st.session_state['wo_current_puzzle'] = None
    # 유저가 순서대로 클릭한 단어 조각 리스트
    if 'wo_user_order' not in st.session_state:
        st.session_state['wo_user_order'] = []
    # AI가 쪼개준 조각들을 무작위로 섞은 리스트 (보기 버튼용)
    if 'wo_shuffled_pieces' not in st.session_state:
        st.session_state['wo_shuffled_pieces'] = []

    # ---------------------------------------------------------
    # 4. 연습할 단어 선택 (Multi-Select)
    # ---------------------------------------------------------
    # 업로드된 단어장 중 유저가 '선택(체크)'한 단어만 필터링해서 가져옵니다.
    target_words = df[df['선택'] == True]
    
    if target_words.empty:
        st.error("업로드된 단어장에서 '선택'된 단어가 없습니다.")
        return

    # 드롭다운에 보여줄 문자열 생성: "한자 (뜻)" 형태
    word_options = target_words.apply(lambda x: f"{x['zh']} ({x['ko']})", axis=1).tolist()
    
    # [수정] max_selections 옵션 제거 (시스템 기본 경고창 숨김)
    selected_options = st.multiselect(
        "연습할 단어를 선택하세요 (최대 3개):", 
        word_options,
        placeholder="단어를 검색하거나 선택하세요"
    )
    
    # 선택된 항목("한자 (뜻)")에서 실제 AI에게 넘길 "한자"만 추출
    selected_words_zh = [opt.split('(')[0].strip() for opt in selected_options]

    # ---------------------------------------------------------
    # 5. [문제 생성] 버튼 로직 (제한 개수 초과 시 제어)
    # ---------------------------------------------------------
    # [수정] 3개 초과 시 경고 문구 출력 및 버튼 비활성화
    if len(selected_words_zh) > 3:
        st.error(f"🖐️ 욕심쟁이! 단어는 **최대 3개**까지만 선택할 수 있어요. (현재 {len(selected_words_zh)}개)")
        # 버튼을 보여주되 누를 수 없게(disabled) 처리
        st.button("✨ 선택한 단어들로 문장 만들기 (AI)", disabled=True)
    
    # [수정] 0개일 때는 안내 문구만 표시 (버튼 숨김)
    elif len(selected_words_zh) == 0:
        st.info("👆 위 박스에서 단어를 선택하면 문장 생성 버튼이 나타납니다.")
        
    # [수정] 정상 범위(1~3개)일 때만 버튼 활성화 및 동작
    else:
        if st.button("✨ 선택한 단어들로 문장 만들기 (AI)", type="primary"):
            # 유저에게 로딩 중임을 알림
            display_words = ", ".join(selected_words_zh)
            with st.spinner(f"'{display_words}'를 모두 넣은 문장을 짓는 중..."):
                
                # services/llm.py의 함수를 호출하여 AI로부터 문제 데이터를 받아옴
                puzzle_data = generate_sentence_puzzle(selected_words_zh)
                
                if puzzle_data:
                    # 받아온 데이터를 세션에 저장 (화면이 새로고침돼도 유지)
                    st.session_state['wo_current_puzzle'] = puzzle_data
                    st.session_state['wo_user_order'] = [] # 정답 입력칸 초기화
                    
                    # 조각(pieces)을 복사해서 섞음 (원본 순서 노출 방지)
                    pieces = puzzle_data['pieces'][:]
                    random.shuffle(pieces)
                    st.session_state['wo_shuffled_pieces'] = pieces
                else:
                    st.error("AI가 문장을 생성하지 못했습니다. 다시 시도해주세요.")

    st.divider()

    # ---------------------------------------------------------
    # 6. 게임 플레이 영역 (문제가 생성되었을 때만 표시)
    # ---------------------------------------------------------
    puzzle = st.session_state['wo_current_puzzle']
    
    if puzzle:
        st.subheader("한국어 뜻을 보고 어순을 맞추세요.")
        st.info(f"🇰🇷 **해석:** {puzzle['korean']}")

        # (A) 유저가 조립 중인 문장 표시
        user_ans_list = st.session_state['wo_user_order']
        st.markdown("### 🔽 완성된 문장")
        
        if user_ans_list:
            # 리스트에 있는 단어들을 공백으로 연결해서 문장처럼 보여줌
            st.success(" ".join(user_ans_list))
        else:
            st.markdown("*(아래 단어 조각을 클릭하여 문장을 완성하세요)*")

        st.markdown("---")

        # (B) 섞여있는 단어 조각 버튼들
        st.markdown("### 🔽 단어 조각 (클릭)")
        shuffled = st.session_state['wo_shuffled_pieces']
        
        # [중요 로직] 이미 유저가 클릭해서 답안으로 올라간 조각은 보기에서 사라져야 함
        # 남은 조각(remaining_pieces) 리스트를 계산
        remaining_pieces = shuffled.copy()
        for p in user_ans_list:
            if p in remaining_pieces:
                remaining_pieces.remove(p) # 답안에 있는 건 삭제
        
        # 남은 조각이 있다면 버튼으로 그려줌
        if remaining_pieces:
            cols = st.columns(len(remaining_pieces))
            for idx, piece in enumerate(remaining_pieces):
                # 각 버튼에 고유한 key를 줘야 에러가 안 남 (f"btn_{piece}_{idx}")
                if cols[idx].button(piece, key=f"btn_{piece}_{idx}"):
                    # 버튼 클릭 시 유저 답안 리스트에 추가하고 화면 갱신(rerun)
                    st.session_state['wo_user_order'].append(piece)
                    st.rerun()
        else:
            st.markdown("*(모든 조각을 사용했습니다)*")

        st.markdown("---")

        # (C) 하단 컨트롤 버튼 (초기화 / 채점)
        c1, c2 = st.columns(2)
        
        # [다시 하기]: 유저가 입력한 답안만 싹 비움
        if c1.button("🔄 다시 하기"):
            st.session_state['wo_user_order'] = []
            st.rerun()
            
        # [정답 확인]: 유저 답안과 AI 정답을 비교
        if c2.button("✅ 정답 확인"):
            # 공백을 없애고 문장부호까지 제거해서 '글자'만 비교 (유연한 채점)
            user_sentence = "".join(st.session_state['wo_user_order'])
            correct_sentence = puzzle['chinese']
            
            import re
            # 정규식으로 알파벳, 숫자, 한자 외 특수문자 제거
            user_clean = re.sub(r'[^\w]', '', user_sentence)
            corr_clean = re.sub(r'[^\w]', '', correct_sentence)

            if user_clean == corr_clean:
                st.balloons() # 축하 효과
                st.success("🎉 정답입니다! 완벽해요.")
                st.markdown(f"**문장:** {puzzle['chinese']}")
                st.markdown(f"**병음:** {puzzle['pinyin']}")
            else:
                st.error("앗! 틀렸습니다.")
                # 틀렸을 때는 정답을 Expander 안에 숨겨서 보여줌 (바로 스포일러 안 되게)
                with st.expander("정답 보기"):
                    st.write(f"**정답 문장:** {puzzle['chinese']}")
                    st.write(f"**병음:** {puzzle['pinyin']}")