import streamlit as st

from ui.sidebar import render_sidebar
from ui.tutorial import render_tutorial
from ui.home import render_home

st.set_page_config(page_title="voca海", page_icon="🐋", layout="wide")

# 글자 크게(눈 피로 ↓)
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# 1) 사이드바
render_sidebar()

# 2) 튜토리얼(원하면 보여주기)
render_tutorial(expanded=False)

# 3) 메인 화면: 메뉴에 따라 페이지 표시
menu = st.session_state.get("menu", "홈")

if menu == "홈":
    render_home()
elif menu == "단어시험":
    st.header("단어시험")
    st.info("여기에 단어시험 UI/로직이 들어갈 예정이에요.")
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
