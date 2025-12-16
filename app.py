from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

# 0. 환경설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI(api_key=api_key)


st.set_page_config(
    page_title="voca海(Hǎi) | voca High",
    layout="wide"
)

st.title("voca海 🐋")
st.caption("단어의 바다에서 자유로이 날다!")

with st.sidebar:
    st.header("학습자 설정")

    nickname = st.text_input("학습자 별명", placeholder="예: voca_hae")
    menu = st.radio(
        "메뉴 선택",
        ["단어시험", "어순 연습", "작문", "단어사전", "대시보드"]
    )
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='text-align:center;'>🐋</h1>
    <h2 style='text-align:center;'>단어의 바다에서 자유로이 날다!</h2>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='text-align:center; font-size:16px;'>
    보카하이는 HSK 등 중국어 시험을 준비하는 학습자를 위한<br>
    자료 기반 + AI 활용 단어·작문 학습 페이지입니다.
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

if st.button("🌊 시작하기"):
    st.session_state["show_tutorial"] = True