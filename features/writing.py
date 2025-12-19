# 경로: features/writing.py
# -----------------------------------------------------------------------------
# [작문 UI 모듈] 
# 1. 99번: 내 단어장 + 2025 트렌드 단어 믹스 출제 (Hybrid Generation)
# 2. 100번: 4대 빈출 테마 기반 상황 묘사 및 이미지 생성 (Theme Strategy)
# -----------------------------------------------------------------------------

import streamlit as st
import random
# [중요] services.llm에서 필요한 출제/채점 함수들을 모두 가져옵니다.
from services.llm import (
    generate_scene_description,   # 100번 문제 출제 (4대 테마)
    generate_image_from_text,     # 100번 이미지 생성
    evaluate_writing_v2,          # 통합 채점 (가점제 로직)
    generate_hybrid_question_99   # [NEW] 99번 하이브리드 출제
)

def show_writing_page():
    st.title("✍️ HSK 5급 실전 작문")
    
    # ---------------------------------------------------------
    # 1. 데이터 유효성 체크
    # ---------------------------------------------------------
    vocab_ready = False
    if 'final_vocab_df' in st.session_state and st.session_state['final_vocab_df'] is not None:
        vocab_ready = True
        df = st.session_state['final_vocab_df']

    # ---------------------------------------------------------
    # 2. 세션 상태(Session State) 초기화
    # ---------------------------------------------------------
    # [99번용 변수]
    if 'wr_99_words' not in st.session_state: st.session_state['wr_99_words'] = [] # 출제된 단어 리스트
    if 'wr_99_feedback' not in st.session_state: st.session_state['wr_99_feedback'] = None # 채점 결과
    if 'wr_99_theme' not in st.session_state: st.session_state['wr_99_theme'] = "" # [NEW] 출제 테마 저장

    # [100번용 변수]
    if 'wr_100_scene' not in st.session_state: st.session_state['wr_100_scene'] = None # 상황 텍스트
    if 'wr_100_image_url' not in st.session_state: st.session_state['wr_100_image_url'] = None # 생성된 이미지 URL
    if 'wr_100_feedback' not in st.session_state: st.session_state['wr_100_feedback'] = None # 채점 결과

    # 탭 구성
    tab1, tab2 = st.tabs(["📝 99번 (제시어 작문)", "🖼️ 100번 (그림 작문)"])

    # =========================================================================
    # TAB 1: 99번 유형 (하이브리드 믹스 출제) - [수정됨]
    # =========================================================================
    with tab1:
        st.subheader("제시어 5개 작문 (99번)")
        
        # [안내] 변경된 출제 로직 설명
        st.info("ℹ️ **[황금 비율 믹스]**로 문제를 생성합니다. (내 단어 60% + 최신 트렌드 40%)")
        st.caption("💡 2025년 출제 경향(명사 중심, 비즈니스/디지털 테마)을 반영하여 AI가 출제합니다.")
        
        # 1. 문제 출제 버튼
        if vocab_ready:
            # 내 단어장을 딕셔너리 리스트로 변환
            all_words = df.to_dict('records')
            
            # [버튼] 하이브리드 문제 생성
            if st.button("🔀 실전 문제 생성 (내 단어 + 트렌드 믹스)", type="primary", use_container_width=True):
                # 단어가 너무 적으면 믹스 불가 (최소 3개 필요)
                if len(all_words) < 3:
                     st.error(f"⚠️ 단어장에 최소 3개 이상의 단어가 있어야 믹스 출제가 가능합니다. (현재 {len(all_words)}개)")
                else:
                    with st.spinner("AI 출제위원이 회원님 단어와 2025 트렌드를 조합 중입니다..."):
                        # [핵심] services/llm.py의 하이브리드 함수 호출
                        hybrid_data = generate_hybrid_question_99(all_words)
                        
                        if hybrid_data:
                            # 결과 세션에 저장
                            st.session_state['wr_99_words'] = hybrid_data['words']
                            st.session_state['wr_99_theme'] = hybrid_data.get('theme', '알 수 없음')
                            st.session_state['wr_99_feedback'] = None # 새 문제이므로 피드백 리셋
                            st.rerun()
                        else:
                            st.error("문제 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")
        else:
            st.warning("⚠️ 단어장이 없습니다. [단어시험] 메뉴에서 파일을 먼저 업로드해주세요.")

        # 2. 문제 표시 및 작문 영역
        current_words_data = st.session_state['wr_99_words']
        
        if current_words_data:
            st.divider()
            # 테마 정보 표시
            st.caption(f"📌 출제 테마: **{st.session_state['wr_99_theme']}**")
            
            st.markdown("### 📢 오늘의 제시어")
            
            # 카드 형태로 5개 나열
            cols = st.columns(5)
            target_zh_list = [] # 채점 시 정답 데이터로 사용
            
            for idx, word in enumerate(current_words_data):
                target_zh_list.append(word['zh'])
                with cols[idx]:
                    # [UI 개선] 출처에 따라 뱃지 색상 다르게 표시
                    source = word.get('source', '기타')
                    if source == '내단어장':
                        st.markdown(":blue-background[📂내단어]")
                    else:
                        st.markdown(":red-background[🔥트렌드]")
                    
                    # 한자만 크게 표시 (뜻은 숨김 - 실전 훈련용)
                    st.markdown(f"### {idx+1}. {word['zh']}")
            
            st.markdown("---")
            
            # 3. 답안 입력 폼
            with st.form("form_99"):
                st.markdown("**미션:** 위 5개 단어를 **모두 사용**하여 80자 이상 작문하세요.")
                st.caption("💡 팁: [🔥트렌드] 단어는 최신 경향이므로 문맥(비즈니스/디지털 등)을 잘 살려야 합니다.")
                
                user_input = st.text_area("답안 작성:", height=150, placeholder="여기에 중국어로 작문하세요...")
                submitted = st.form_submit_button("📝 제출 및 채점")
                
                if submitted:
                    if not user_input.strip():
                        st.warning("내용을 입력하세요.")
                    else:
                        with st.spinner("AI 감독관이 꼼꼼하게 평가 중입니다..."):
                            # 통합 채점 함수 호출
                            feedback = evaluate_writing_v2('99', user_input, target_zh_list)
                            st.session_state['wr_99_feedback'] = feedback
            
            # 4. 피드백 표시 (기존 유지)
            fb = st.session_state['wr_99_feedback']
            if fb:
                st.divider()
                st.markdown(f"### 📊 등급/점수: {fb['score']}점")
                
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
                    st.write(fb['correction']) # 마크다운 대신 write 사용 (깔끔하게)
                    st.caption(f"📝 해석: {fb.get('translation', '해석 없음')}")
                
                # 상세 피드백 확장 패널
                with st.expander("👩‍🏫 상세 첨삭 (공식 기준 + 가점 요인)", expanded=True):
                    st.write(fb['explanation'])
                    if fb.get('better_expression'):
                        st.markdown(f"✨ **추천 표현:** {fb['better_expression']}")

                st.divider()
                st.warning("📢 AI 채점 기준을 엄격하게 설정하였지만 이 채점 결과는 실제 시험 채점 결과와 상이할 수 있으니 연습 용도로 참고만 하세요.")
                st.info("💪 실제 시험에서 더 좋은 점수를 얻을 수 있도록 **voca海(hǎi)|voca high**와 열심히 연습해봅시다. 고득점을 향하여!")

    # =========================================================================
    # TAB 2: 100번 유형 (4대 빈출 테마 전략) - [기존 로직 유지]
    # =========================================================================
    with tab2:
        st.subheader("그림 작문 (100번)")
        st.caption("4대 빈출 테마(비즈니스/일상/스포츠/학습) 중 랜덤으로 출제됩니다.")
        
        # 1. 문제 생성 버튼
        if st.button("🎲 100번 실전 문제 받기 (4대 빈출 테마)", type="primary"):
            # 1) 텍스트 상황 생성 (기존 generate_scene_description 사용)
            with st.spinner("1. 출제위원이 최근 기출 경향을 분석 중..."):
                scene_data = generate_scene_description() 
                st.session_state['wr_100_scene'] = scene_data
                st.session_state['wr_100_feedback'] = None
                st.session_state['wr_100_image_url'] = None 
            
            # 2) 이미지 생성 (DALL-E)
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
            
            # 3. 작문 입력
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

            # 4. 피드백 표시 (99번과 동일한 스타일)
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
                c2.caption(f"📝 해석: {fb.get('translation', '해석 없음')}")
                
                with st.expander("👩‍🏫 상세 첨삭 (테마 & 서사)", expanded=True):
                    st.write(fb['explanation'])
                    if fb.get('better_expression'):
                        st.markdown(f"✨ **추천 표현:** {fb['better_expression']}")
                
                st.divider()
                st.warning("📢 AI 채점 기준을 엄격하게 설정하였지만 이 채점 결과는 실제 시험 채점 결과와 상이할 수 있으니 연습 용도로 참고만 하세요.")
                st.info("💪 실제 시험에서 더 좋은 점수를 얻을 수 있도록 **voca海(hǎi)|voca high**와 열심히 연습해봅시다. 고득점을 향하여!")