# 경로: features/writing.py

import streamlit as st
import random
from services.llm import generate_scene_description, generate_image_from_text, evaluate_writing_v2

def show_writing_page():
    st.title("✍️ HSK 5급 실전 작문")
    
    # 데이터 체크
    vocab_ready = False
    if 'final_vocab_df' in st.session_state and st.session_state['final_vocab_df'] is not None:
        vocab_ready = True
        df = st.session_state['final_vocab_df']

    # ---------------------------------------------------------
    # 세션 초기화
    # ---------------------------------------------------------
    # [99번용]
    if 'wr_99_words' not in st.session_state: st.session_state['wr_99_words'] = [] # 랜덤 뽑힌 단어 저장
    if 'wr_99_feedback' not in st.session_state: st.session_state['wr_99_feedback'] = None
    
    # [100번용]
    if 'wr_100_scene' not in st.session_state: st.session_state['wr_100_scene'] = None
    if 'wr_100_image_url' not in st.session_state: st.session_state['wr_100_image_url'] = None
    if 'wr_100_feedback' not in st.session_state: st.session_state['wr_100_feedback'] = None

    # 탭 생성
    tab1, tab2 = st.tabs(["📝 99번 (제시어 작문)", "🖼️ 100번 (그림 작문)"])

    # =========================================================
    # TAB 1: 99번 유형 (시스템 랜덤 출제 - 실전형)
    # =========================================================
    with tab1:
        st.subheader("제시어 5개 작문 (99번)")
        
        # [요청 반영] 안내 문구 추가
        st.info("ℹ️ 99번 문제는 **첨부하신 단어장**의 단어들을 참고하여 무작위로 출제됩니다.")
        st.caption("💡 5급 시험에 응시하시는 경우 **5급 이상 단어장**을 넣으시는 것을 추천합니다.")
        
        if not vocab_ready:
            st.warning("⚠️ 단어장이 없습니다. [단어시험] 메뉴에서 파일을 업로드해주세요.")
        else:
            # 1. 문제 출제 버튼 (랜덤 뽑기)
            if st.button("🎲 실전 문제 생성 (단어 5개 뽑기)", type="primary"):
                # 전체 단어 리스트 확인
                all_words = df.to_dict('records') # [{'zh':..., 'ko':...}, ...]
                
                if len(all_words) < 5:
                    st.error(f"단어장에 단어가 너무 적습니다. (현재 {len(all_words)}개). 최소 5개 이상 필요합니다.")
                else:
                    # [핵심] 5개 무작위 추출
                    selected_sample = random.sample(all_words, 5)
                    # 세션에 저장
                    st.session_state['wr_99_words'] = selected_sample
                    st.session_state['wr_99_feedback'] = None # 새 문제니까 피드백 리셋
                    st.rerun()

            # 2. 문제 표시 및 작문 영역
            current_words_data = st.session_state['wr_99_words']
            
            if current_words_data:
                st.divider()
                st.markdown("### 📢 오늘의 제시어")
                
                # 보기 좋게 카드 형태로 나열
                cols = st.columns(5)
                target_zh_list = [] # 채점용 리스트
                
                for idx, word in enumerate(current_words_data):
                    target_zh_list.append(word['zh'])
                    with cols[idx]:
                        # [수정] 한글 뜻은 보여주지 않고, 한자만 크게 표시합니다.
                        st.markdown(f"### {idx+1}. {word['zh']}")
                
                st.markdown("---")
                
                # 작문 입력 (힌트 없음 - 스파르타)
                with st.form("form_99"):
                    st.markdown("**미션:** 위 5개 단어를 **모두 사용**하여 80자 내외로 작문하세요.")
                    user_input = st.text_area("답안 작성:", height=150, placeholder="여기에 중국어로 작문하세요...")
                    submitted = st.form_submit_button("📝 제출 및 채점")
                    
                    if submitted:
                        if not user_input.strip():
                            st.warning("내용을 입력하세요.")
                        else:
                            with st.spinner("AI 감독관이 '호응 관계'와 '논리성'을 분석 중입니다..."):
                                # services/llm.py의 함수 호출 (딥리서치 기준 적용됨)
                                feedback = evaluate_writing_v2('99', user_input, target_zh_list)
                                st.session_state['wr_99_feedback'] = feedback
                
                # 3. 피드백 표시
                fb = st.session_state['wr_99_feedback']
                if fb:
                    st.divider()
                    st.markdown(f"### 📊 예상 점수: {fb['score']}점")
                    
                    if fb['score'] >= 80: 
                        st.balloons()
                        st.success("합격권입니다! 🎉")
                    else:
                        st.warning("조금 더 분발하세요! 💪")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.info("**내 답안**")
                        st.write(user_input)
                    with c2:
                        st.success("**모범 답안 (교정)**")
                        st.markdown(f"#### {fb['correction']}")
                        # [수정] 병음 대신 한국어 해석 표시
                        st.caption(f"📝 해석: {fb.get('translation', '해석 없음')}")
                    
                    # 딥리서치 기반 상세 피드백
                    with st.expander("👩‍🏫 상세 첨삭 (호응구조 & 논리)", expanded=True):
                        st.write(fb['explanation'])
                        if fb.get('better_expression'):
                            st.markdown(f"✨ **추천 표현:** {fb['better_expression']}")

                    # [추가] 안내 및 응원 문구
                    st.divider()
                    st.warning("📢 AI 채점 기준을 엄격하게 설정하였지만 이 채점 결과는 실제 시험 채점 결과와 상이할 수 있으니 연습 용도로 참고만 하세요.")
                    st.info("💪 실제 시험에서 더 좋은 점수를 얻을 수 있도록 **voca海(hǎi)|voca high**와 열심히 연습해봅시다. 고득점을 향하여!")

    # =========================================================
    # TAB 2: 100번 유형 (그림/상황 작문)
    # =========================================================
    with tab2:
        st.caption("주어진 사진(상황)을 보고, 80자 내외로 작문하세요.")
        
        # 1. 문제 생성 버튼
        if st.button("🎲 100번 실전 문제 받기 (4대 빈출 테마)", type="primary"):
            # 1) 텍스트 상황 생성
            with st.spinner("1. 출제위원이 최근 기출 경향을 분석 중..."):
                scene_data = generate_scene_description() 
                st.session_state['wr_100_scene'] = scene_data
                st.session_state['wr_100_feedback'] = None
                st.session_state['wr_100_image_url'] = None # 이미지 초기화
            
            # 2) 이미지 생성
            if scene_data:
                with st.spinner("2. AI 화가가 그림을 그리는 중... (약 10초)"):
                    img_url = generate_image_from_text(scene_data['scene_desc'])
                    st.session_state['wr_100_image_url'] = img_url

        # 2. 문제 표시
        scene = st.session_state.get('wr_100_scene')
        img_url = st.session_state.get('wr_100_image_url')

        if scene:
            st.divider()
            st.subheader("📸 문제")
            
            if img_url:
                st.image(img_url, caption="HSK 5급 실전 문제", use_container_width=True)
                with st.expander("🔍 그림이 잘 안 보이나요? (상황 묘사 텍스트 보기)"):
                    st.write(scene['scene_desc'])
            else:
                st.info(f"**[상황 묘사]**\n\n{scene['scene_desc']}")
            
            st.caption(f"💡 추천 키워드: {', '.join(scene['keywords'])}")
            
            # 작문 입력
            with st.form("form_100"):
                user_input = st.text_area("상황에 맞는 작문 (80자 내외):", height=150, key="input_100")
                submitted = st.form_submit_button("제출 및 평가")
                
                if submitted:
                    if not user_input.strip():
                        st.warning("내용을 입력하세요.")
                    else:
                        with st.spinner("AI 채점관이 '서사'와 '테마 적합성'을 평가 중..."):
                            feedback = evaluate_writing_v2('100', user_input, scene['scene_desc'])
                            st.session_state['wr_100_feedback'] = feedback

            # 피드백 표시
            fb = st.session_state['wr_100_feedback']
            if fb:
                st.divider()
                st.markdown(f"### 📊 예상 점수: {fb['score']}점")
                
                if fb['score'] >= 80: 
                    st.balloons()
                    st.success("합격권입니다! 🎉")
                else:
                    st.warning("조금 더 분발하세요! 💪")
                
                c1, c2 = st.columns(2)
                c1.info("**내 답안**")
                c1.write(user_input)
                c2.success("**모범 답안**")
                c2.markdown(f"#### {fb['correction']}")
                # [수정] 병음 대신 한국어 해석 표시
                c2.caption(f"📝 해석: {fb.get('translation', '해석 없음')}")
                
                with st.expander("👩‍🏫 상세 첨삭 (테마 & 서사)", expanded=True):
                    st.write(fb['explanation'])
                    if fb.get('better_expression'):
                        st.markdown(f"✨ **추천 표현:** {fb['better_expression']}")
                
                # [추가] 안내 및 응원 문구
                st.divider()
                st.warning("📢 AI 채점 기준을 엄격하게 설정하였지만 이 채점 결과는 실제 시험 채점 결과와 상이할 수 있으니 연습 용도로 참고만 하세요.")
                st.info("💪 실제 시험에서 더 좋은 점수를 얻을 수 있도록 **voca海(hǎi)|voca high**와 열심히 연습해봅시다. 고득점을 향하여!")