# 파일명: app.py
import streamlit as st
from ui.sidebar import show_sidebar
from ui.tutorial import show_tutorial
from ui.home import show_home
from features.vocab_upload import show_vocab_upload
from features.vocab_quiz import show_quiz_page # 파일명 vocab_quiz 확인!

# 페이지 설정
st.set_page_config(page_title="voca海", page_icon="🐋", layout="wide")

# [복구] 글자 크게 및 레이아웃 패딩 설정 (눈 피로 ↓)
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# 사이드바 호출 (menu 값을 session_state에 저장함)
show_sidebar()
menu = st.session_state.get("menu", "홈")

# ---------------------------------------------------------
# [수정 포인트] 메뉴가 바뀌어도 '단어 데이터'는 삭제하지 않음
# ---------------------------------------------------------

if menu == "홈":
    show_home() 
    show_tutorial(expanded=False)                  

elif menu == "단어시험":
    st.header("단어시험")
    
    # 1. 퀴즈 상태 초기화
    if 'quiz_status' not in st.session_state:
        st.session_state['quiz_status'] = 'ready'
    
    # 2. 화면 전환 (시험 중이면 시험지, 아니면 업로드/리스트 화면)
    if st.session_state['quiz_status'] == 'playing':
        show_quiz_page()
    else:
        # [중요] show_vocab_upload 내부에서 이미 session_state['final_vocab_df']를 
        # 체크하고 있으므로, 홈에 갔다 와도 파일만 다시 안 올리면 목록이 유지됩니다.
        show_vocab_upload()

elif menu == "어순 연습":
    st.header("어순 연습")
    st.info("여기에 어순 맞추기 UI/로직이 들어갈 예정이에요.")
# ... (이하 동일)