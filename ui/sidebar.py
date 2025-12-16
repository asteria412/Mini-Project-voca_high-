import streamlit as st

MENU = ["홈", "단어시험", "어순 연습", "작문", "단어사전", "대시보드"]

def render_sidebar():
    st.sidebar.header("voca海 설정")

    nickname = st.sidebar.text_input("학습자 별명", placeholder="예: voca_hae")
    if nickname:
        st.session_state["nickname"] = nickname

    st.sidebar.subheader("메뉴")
    menu = st.sidebar.radio(" ", MENU, label_visibility="collapsed")
    st.session_state["menu"] = menu

    st.sidebar.divider()
    
