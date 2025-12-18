# 경로: features/vocab_quiz.py
# 상세 내용: 주관식 믹스 퀴즈 + [추가] 이상한 문제 제외 및 모수 조정 로직

import streamlit as st
import random

def show_quiz_page():
    # 1. 기초 데이터 유효성 검사
    if 'quiz_vocab' not in st.session_state or st.session_state['quiz_vocab'].empty:
        st.warning("⚠️ 시험을 볼 단어가 없습니다. 업로드 화면에서 단어를 선택해 주세요.")
        if st.button("⬅️ 단어 선택하러 가기"):
            st.session_state['quiz_status'] = 'ready'
            st.rerun()
        return

    vocab_df = st.session_state['quiz_vocab']
    
    st.title("✍️ 주관식 단어 시험")
    st.caption("한자와 한국어 뜻을 번갈아가며 맞히는 주관식 시험입니다.")

    # ---------------------------------------------------------
    # 2. 시험 세팅
    # ---------------------------------------------------------
    if 'current_quiz' not in st.session_state:
        max_limit = len(vocab_df)
        st.info(f"💡 현재 선택된 단어는 총 {max_limit}개입니다.")
        
        q_count = st.number_input(
            "몇 문제를 풀까요?", 
            min_value=1, 
            max_value=max_limit, 
            value=min(10, max_limit),
            step=1
        )
        
        if st.button("🚀 시험 시작하기", use_container_width=True, type="primary"):
            samples = vocab_df.sample(n=int(q_count)).to_dict('records')
            quiz_list = []
            for item in samples:
                quiz_type = random.choice(['zh_to_ko', 'ko_to_zh'])
                quiz_list.append({
                    'item': item,
                    'type': quiz_type,
                    'user_ans': "",
                    'exclude': False # [추가] 제외 여부 초기값
                })
            
            st.session_state['current_quiz'] = quiz_list
            st.session_state['quiz_finished'] = False
            st.rerun()
        return

    # ---------------------------------------------------------
    # 3. 시험 진행 (폼 형태)
    # ---------------------------------------------------------
    quiz_data = st.session_state['current_quiz']
    
    if not st.session_state.get('quiz_finished', False):
        with st.form("quiz_input_form"):
            for i, q in enumerate(quiz_data):
                item = q['item']
                pos_val = item.get('pos')
                pos_text = f"({pos_val})" if pos_val and str(pos_val).strip() != "" else ""

                col_text, col_opt = st.columns([4, 1])
                with col_text:
                    st.write(f"**문제 {i+1}.**")
                with col_opt:
                    # [추가] 문제 제외 체크박스
                    q['exclude'] = st.checkbox("문제 제외", key=f"ex_{i}", help="데이터가 이상하면 체크하세요. 점수 계산에서 빠집니다.")
                
                if q['type'] == 'zh_to_ko':
                    st.write(f"다음 한자의 뜻을 적으세요: ### {item['zh']} {pos_text}")
                    q['user_ans'] = st.text_input("답안 입력 (한국어)", key=f"ans_{i}")
                else:
                    st.write(f"다음 뜻에 맞는 한자를 적으세요: ### {item['ko']} {pos_text}")
                    q['user_ans'] = st.text_input("답안 입력 (한자)", key=f"ans_{i}")
                
                st.write("") 

            submitted = st.form_submit_button("✅ 모든 답안 제출하고 채점하기", use_container_width=True)
            
            if submitted:
                st.session_state['quiz_finished'] = True
                st.rerun()

    # ---------------------------------------------------------
    # 4. 채점 및 결과 리포트 (모수 조정 로직 포함)
    # ---------------------------------------------------------
    else:
        st.subheader("📊 채점 결과")
        correct_count = 0
        excluded_count = 0 # [추가] 제외된 문제 수 카운트
        
        for i, q in enumerate(quiz_data):
            # [추가] 제외된 문제는 채점하지 않고 건너뜀
            if q.get('exclude'):
                excluded_count += 1
                with st.expander(f"문제 {i+1}: ⏭️ 제외됨", expanded=False):
                    st.write("사용자가 '문제 제외'를 선택한 항목입니다.")
                continue

            item = q['item']
            user_ans = q['user_ans'].strip()
            
            if q['type'] == 'zh_to_ko':
                raw_correct = str(item['ko'])
                keywords = [k.strip() for k in raw_correct.replace(',', '/').split('/') if k.strip()]
                is_correct = any(k in user_ans for k in keywords) if user_ans else False
                display_correct = raw_correct
            else:
                display_correct = str(item['zh'])
                is_correct = (user_ans == display_correct)

            with st.expander(f"문제 {i+1}: {'✅ 정답' if is_correct else '❌ 오답'}", expanded=True):
                col_q, col_a = st.columns(2)
                with col_q:
                    st.write(f"**문제:** {item['zh'] if q['type']=='zh_to_ko' else item['ko']}")
                    st.write(f"**내 답:** {user_ans if user_ans else '(미입력)'}")
                with col_a:
                    st.write(f"**정답:** {display_correct}")
                    st.write(f"**병음:** [{item.get('pinyin', '-')}]")
                
                if is_correct:
                    correct_count += 1

        # [수정] 최종 스코어 계산 (모수 = 전체 문제 - 제외된 문제)
        st.divider()
        final_total = len(quiz_data) - excluded_count
        
        if final_total > 0:
            score_percent = int(correct_count / final_total * 100)
            st.metric("최종 점수", f"{correct_count} / {final_total}", f"{score_percent}점 (제외 {excluded_count}개)")
        else:
            st.warning("모든 문제가 제외되어 점수를 계산할 수 없습니다.")
        
        if st.button("🔄 다시 시험 보기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_finished'] = False
            st.rerun()
            
        if st.button("📁 단어 다시 선택하기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_status'] = 'ready'
            st.rerun()