# 경로: features/vocab_quiz.py
# 상세 내용: 주관식 믹스 퀴즈 + [유연한 정답 채점] + 문제 제외/모수 조정

import streamlit as st
import random
import re   
from services.google_sheets import save_score

def check_answer(user_input, correct_answer):
    """
    [유연한 채점 로직]
    정답 데이터가 "넓다 광대하다" 또는 "넓다, 광대하다" 처럼 되어 있을 때,
    사용자가 쉼표나 공백으로 구분된 단어 중 하나만 입력해도 정답으로 인정합니다.
    """
    # 1. 입력값 정제
    user = str(user_input).strip()
    if not user: 
        return False # 입력 없으면 오답
    
    # 2. 정답 데이터 정제 (쉼표, 슬래시, 공백을 모두 구분자로 처리)
    # 예: "넓다 광대하다" -> ['넓다', '광대하다']
    # 예: "넓다, 광대하다" -> ['넓다', '광대하다']
    candidates = re.split(r'[,/ ]+', str(correct_answer))
    
    # 리스트 정제 (빈 문자열 제거 및 공백 제거)
    candidates = [c.strip() for c in candidates if c.strip()]

    # 3. 비교 (하나라도 일치하면 정답)
    return user in candidates

def show_quiz_page():
    # 1. 기초 데이터 유효성 검사
    if 'quiz_vocab' not in st.session_state or st.session_state['quiz_vocab'].empty:
        # (혹시 quiz_vocab이 없으면 전체 단어장에서 가져오도록 호환성 처리)
        if 'final_vocab_df' in st.session_state:
            st.session_state['quiz_vocab'] = st.session_state['final_vocab_df']
        else:
            st.warning("⚠️ 시험을 볼 단어가 없습니다. 업로드 화면에서 단어를 선택해 주세요.")
            if st.button("⬅️ 단어 선택하러 가기"):
                st.session_state['quiz_status'] = 'ready'
                st.rerun()
            return

    vocab_df = st.session_state['quiz_vocab']
    
    st.subheader("✍️ 주관식 단어 시험")
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
                    'exclude': False 
                })
            
            st.session_state['current_quiz'] = quiz_list
            st.session_state['quiz_finished'] = False
            
            # [재시험 시 저장 플래그 초기화]
            if 'saved_to_sheets' in st.session_state:
                del st.session_state['saved_to_sheets']
            
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
                    # 문제 제외 체크박스
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
    # 4. 채점 및 결과 리포트 (유연한 채점 적용)
    # ---------------------------------------------------------
    else:
        st.subheader("📊 채점 결과")
        correct_count = 0
        excluded_count = 0 
        
        for i, q in enumerate(quiz_data):
            # 제외된 문제는 채점하지 않고 건너뜀
            if q.get('exclude'):
                excluded_count += 1
                with st.expander(f"문제 {i+1}: ⏭️ 제외됨", expanded=False):
                    st.write("사용자가 '문제 제외'를 선택한 항목입니다.")
                continue

            item = q['item']
            user_ans = q['user_ans'].strip()
            
            # [수정] 정답 여부 판단 로직 개선 (check_answer 함수 사용)
            if q['type'] == 'zh_to_ko':
                target_correct = str(item['ko'])
                is_correct = check_answer(user_ans, target_correct)
                display_correct = target_correct
            else:
                target_correct = str(item['zh'])
                # 한자 문제도 혹시 동의어가 있을 수 있으니 check_answer 사용 (보통은 1개지만 유연하게)
                is_correct = check_answer(user_ans, target_correct)
                display_correct = target_correct

            # 결과 표시
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

        # 최종 스코어 계산 (모수 = 전체 문제 - 제외된 문제)
        st.divider()
        final_total = len(quiz_data) - excluded_count
        
        if final_total > 0:
            score_percent = int(correct_count / final_total * 100)
            st.metric("최종 점수", f"{correct_count} / {final_total}", f"{score_percent}점 (제외 {excluded_count}개)")
            
            # =========================================================
            # [추가] 구글 시트 자동 저장 로직
            # =========================================================
            nickname = st.session_state.get("nickname", "")
            if nickname:
                if 'saved_to_sheets' not in st.session_state:
                    with st.spinner(f"☁️ {nickname}님의 점수 저장 중..."):
                        # save_score(별명, 시험유형, 점수)
                        success = save_score(nickname, "단어시험(주관식)", score_percent)
                        
                        if success:
                            st.toast("✅ 구글 시트 저장 완료!", icon="🎉")
                            st.session_state['saved_to_sheets'] = True
                        else:
                            st.error("❌ 저장 실패")
                else:
                    st.info("✅ 이미 저장된 기록입니다.")
            else:
                st.warning("⚠️ 별명(로그인)이 없어서 점수가 저장되지 않았습니다.")
            # =========================================================
            
        else:
            st.warning("모든 문제가 제외되어 점수를 계산할 수 없습니다.")
        
        if st.button("🔄 다시 시험 보기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_finished'] = False
            # 재시험을 위해 저장 기록 삭제
            if 'saved_to_sheets' in st.session_state:
                del st.session_state['saved_to_sheets']
            st.rerun()
            
        if st.button("📁 단어 다시 선택하기", use_container_width=True):
            del st.session_state['current_quiz']
            st.session_state['quiz_status'] = 'ready'
            if 'saved_to_sheets' in st.session_state:
                del st.session_state['saved_to_sheets']
            st.rerun()