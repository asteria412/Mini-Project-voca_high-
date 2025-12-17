#------------- 필요한 도구들을 불러온다 ---------------------#
import streamlit as st

from ui.sidebar import show_sidebar
from ui.tutorial import show_tutorial
from ui.home import show_home
from features.vocab_upload import show_vocab_upload
#---------------------------------------------------------#

# 페이지의 기본설정(타이틀, 아이콘 띄우기, 레이아웃)
st.set_page_config(page_title="voca海", page_icon="🐋", layout="wide")

# 글자 크게(눈 피로 ↓)
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# 1) 페이지에 사이드바 불러라 
# 여기서 사용자가 메뉴를 고르면 session_state에 담김 
show_sidebar()

# 2) 메인 화면: 메뉴에 따라 페이지 표시 
# > sidebar에서 지정한 session_state에 담겨있는 menu를 불러오고 없으면 홈이 기본값
menu = st.session_state.get("menu", "홈")

if menu == "홈":
    show_home() 
    show_tutorial(expanded=False)                 
elif menu == "단어시험":
    st.header("단어시험")
    show_vocab_upload()
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
