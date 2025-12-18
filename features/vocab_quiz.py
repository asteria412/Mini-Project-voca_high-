# 경로: features/quiz.py
# 상세 내용: 주관식(한↔중) 믹스 퀴즈, 품사 조건부 노출, 유연한 키워드 채점 로직 포함

import streamlit as st
import random

def show_quiz_page():
    """
    [주요 로직]
    1. 설정: 유저가 문제 개수를 선택하고 시험을 시작합니다.
    2. 출제: 한->중, 중->한 유형을 50% 확률로 섞고, 품사가 있다면 함께 노출합니다.
    3. 채점: 한자는 '완전 일치', 뜻은 '핵심어 포함' 여부로 판단합니다.
    4. 결과: 정답 확인 시 성조가 포함된 병음을 함께 보여주어 학습 효과를 높입니다.
    """

    # 1. 기초 데이터 유효성 검사
    if 'quiz_vocab' not in st.session_state or st.session_state['quiz_vocab'].empty:
        st.warning("⚠️ 시험을 볼 단어가 없습니다. 업로드 화면에서 단어를 선택해 주세요.")
        if st.button("⬅️ 단어 선택하러 가기"):
            st.session_state['quiz_status'] = 'ready'
            st.rerun()
        return

    # 유저가 체크박스로 선택한 단어들만 가져옵니다.
    vocab_df = st.session_state['quiz_vocab']
    
    st.title("✍️ 주관식 단어 시험")
    st.caption("한자와 한국어 뜻을 번갈아가며 맞히는 주관식 시험입니다.")

    # ---------------------------------------------------------
    # 2. 시험 세팅 (문제 개수 인풋)
    # ---------------------------------------------------------
    if 'current_quiz' not in st.session_state:
        max_limit = len(vocab_df)
        
        st.info(f"💡 현재 선택된 단어는 총 {max_limit}개입니다.")
        
        # [회원님 요청] 문제 출제 개수를 유저가 직접 선택
        q_count = st.number_input(
            "몇 문제를 풀까요?", 
            min_value=1, 
            max_value=max_limit, 
            value=min(10, max_limit),
            step=1
        )
        
        if st.button("🚀 시험 시작하기", use_container_width=True, type="primary"):
            # 문제 무작위 추출 및 유형 섞기
            samples = vocab_df.sample(n=int(q_count)).to_dict('records')
            quiz_list = []
            for item in samples:
                # 50:50 확률로 유형 결정
                quiz_type = random.choice(['zh_to_ko', 'ko_to_zh'])
                quiz_list.append({
                    'item': item,
                    'type': quiz_type,
                    'user_ans': ""
                })
            
            # 세션에 시험 데이터 저장
            st.session_state['current_quiz'] = quiz_list
            st.session_state['quiz_finished'] = False
            st.rerun()
        return

    # ---------------------------------------------------------
    # 3. 시험 진행 (폼 형태)
    # ---------------------------------------------------------
    quiz_data = st.session_state['current_quiz']
    
    # 시험이 종료되지 않았을 때만 입력 폼을 보여줍니다.
    if not st.session_state.get('quiz_finished', False):
        with st.form("quiz_input_form"):
            for i, q in enumerate(quiz_data):
                item = q['item']
                
                # [회원님 요청] 품사가 있는 파일만 표시 (없으면 공백)
                pos_val = item.get('pos')
                pos_text = f"({pos_val})" if pos_val and str(pos_val).strip() != "" else ""

                st.write(f"**문제 {i+1}.**")
                
                if q['type'] == 'zh_to_ko':
                    # [중 -> 한]
                    st.write(f"다음 한자의 뜻을 적으세요: ### {item['zh']} {pos_text}")
                    q['user_ans'] = st.text_input("답안 입력 (한국어)", key=f"ans_{i}")
                else:
                    # [한 -> 중]
                    st.write(f"다음 뜻에 맞는 한자를 적으세요: ### {item['ko']} {pos_text}")
                    q['user_ans'] = st.text_input("답안 입력 (한자)", key=f"ans_{i}")
                
                st.write("") # 간격 조절

            submitted = st.form_submit_button("✅ 모든 답안 제출하고 채점하기", use_container_width=True)
            
            if submitted:
                st.session_state['quiz_finished'] = True
                st.rerun()

    # ---------------------------------------------------------
    # 4. 채점 및 결과 리포트
    # ---------------------------------------------------------
    else:
        st.subheader("📊 채점 결과")
        correct_count = 0
        
        for i, q in enumerate(quiz_data):
            item = q['item']
            user_ans = q['user_ans'].strip()
            
            # 채점 기준 설정
            if q['type'] == 'zh_to_ko':
                # [뜻 채점] 정답 문구 내에 쉼표나 슬래시로 구분된 핵심어가 포함되어 있는지 확인
                # 예: "선생님, 교사" -> 유저가 "선생님"만 써도 정답
                raw_correct = str(item['ko'])
                keywords = [k.strip() for k in raw_correct.replace(',', '/').split('/') if k.strip()]
                is_correct = any(k in user_ans for k in keywords) if user_ans else False
                display_correct = raw_correct
            else:
                # [한자 채점] 한자는 완벽히 일치해야 함
                display_correct = str(item['zh'])
                is_correct = (user_ans == display_correct)

            # 결과 화면 출력
            with st.expander(f"문제 {i+1}: {'✅ 정답' if is_correct else '❌ 오답'}", expanded=True):
                col_q, col_a = st.columns(2)
                with col_q:
                    st.write(f"**문제:** {item['zh'] if q['type']=='zh_to_ko' else item['ko']}")
                    st.write(f"**내 답:** {user_ans if user_ans else '(미입력)'}")
                with col_a:
                    # [회원님 요청] 병음은 채점 시 성조 포함해서 노출
                    st.write(f"**정답:** {display_correct}")
                    st.write(f"**병음:** [{item.get('pinyin', '-')}]")
                
                if is_correct:
                    correct_count += 1

        # 최종 스코어 보드
        st.divider()
        st.metric("최종 점수", f"{correct_count} / {len(quiz_data)}", f"{int(correct_count/len(quiz_data)*100)}점")
        
        if st.button("🔄 다시 시험 보기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_finished'] = False
            st.rerun()
            
        if st.button("📁 단어 다시 선택하기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_status'] = 'ready'
            st.rerun()