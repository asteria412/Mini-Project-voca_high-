# 파일명: app.py
# 수정 내용: '단어시험' 메뉴 클릭 시 업로드 상태와 시험 상태를 구분하여 화면 전환

import streamlit as st

from ui.sidebar import show_sidebar
from ui.tutorial import show_tutorial
from ui.home import show_home
from features.vocab_upload import show_vocab_upload
from features.vocab_quiz import show_quiz_page # [추가] 새로 만든 퀴즈 모듈을 불러옵니다.

# 페이지의 기본설정(타이틀, 아이콘 띄우기, 레이아웃)
st.set_page_config(page_title="voca海", page_icon="🐋", layout="wide")

# 글자 크게(눈 피로 ↓)
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# 1) 페이지에 사이드바 불러오기 
show_sidebar()

# 2) 메인 화면: 메뉴에 따라 페이지 표시 
menu = st.session_state.get("menu", "홈")

if menu == "홈":
    show_home() 
    show_tutorial(expanded=False)                  
elif menu == "단어시험":
    # [핵심 수정] 단어시험 메뉴 안에서 '상태'에 따라 화면을 갈아 끼웁니다.
    st.header("단어시험")
    
    # 세션에 상태값이 없으면 기본값 'ready'로 설정
    if 'quiz_status' not in st.session_state:
        st.session_state['quiz_status'] = 'ready'
    
    # 상태가 'playing'이면 퀴즈 화면을, 아니면 업로드 화면을 보여줌
    if st.session_state['quiz_status'] == 'playing':
        show_quiz_page() # features/quiz.py 실행
    else:
        show_vocab_upload() # features/vocab_upload.py 실행

elif menu == "어순 연습":
    st.header("어순 연습")
    st.info("여기에 어순 맞추기 UI/로직이 들어갈 예정이에요.")
elif menu == "작문":
    st.header("작문")
    st.info("여기에 작문 문제/채점 UI/로직이 들어갈 예정이에요.")
elif menu == "단어사전":
    st.header("단어사전")
    st.info("여기에 단어 검색 UI/로직이 들어갈 예정이에요.")
else:
    st.header("대시보드")
    st.info("여기에 학습 기록/그래프 UI가 들어갈 예정이에요.")