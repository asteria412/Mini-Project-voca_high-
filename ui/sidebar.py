import streamlit as st

MENU = ["홈", "단어시험", "어순 연습", "작문", "단어사전", "대시보드"]

def show_sidebar():
    st.sidebar.header("voca海 설정")
    
# 입력창을 만들어서 입력이 되면(입력값有), 전체에서 쓰게 session state "nickname에 저장해라"
    nickname = st.sidebar.text_input("학습자 별명", placeholder="예: voca_hai")
    if nickname:
        st.session_state["nickname"] = nickname

    st.sidebar.subheader("메뉴")
    menu = st.sidebar.radio(" ", MENU, label_visibility="collapsed")
    st.session_state["menu"] = menu

    st.sidebar.divider()
    
