# 파일명: app.py
import streamlit as st
from ui.sidebar import show_sidebar
from ui.home import show_home
from features.vocab_upload import show_vocab_upload
from features.vocab_quiz import show_quiz_page
from features.word_order import show_word_order_page
from features.writing import show_writing_page 
from features.dictionary import show_dictionary_page
from features.dashboard import show_dashboard_page
# 임시호출 #
from services.google_sheets import save_score, get_db_connection
import random 
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="voca海", page_icon="🐋", layout="wide")

# [수정] 글자 크기 최적화 (PC는 시원하게, 모바일은 안 잘리게)
st.markdown("""
<style>
    /* 1. PC 기본값: 18px (기존 20px보다 살짝 줄임) */
    html, body, [class*="css"] { 
        font-size: 18px; 
    }

    /* 2. 모바일(화면 좁을 때): 15px로 자동 축소 */
    @media (max-width: 600px) {
        html, body, [class*="css"] { 
            font-size: 12px; 
        }
    }

    /* 여백 설정은 그대로 유지 */
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
        # 체크하고 있으므로, 홈에 갔다 와도 파일만 다시 안 올리면 목록유지
        show_vocab_upload()

elif menu == "어순 연습":
    st.header("어순 연습")
    # show_word_order_page() 함수 실행
    show_word_order_page()

elif menu == "작문":
    st.header("작문")
    show_writing_page()

elif menu == "단어사전":
    st.header("단어사전")
    show_dictionary_page()
else:
    st.header("대시보드")
    show_dashboard_page()
     
        
# [임시 코드] 추후 삭제 예정

if st.sidebar.button("🧪 테스트 데이터 20개 생성 (개발용)"):
    nickname = st.session_state.get("nickname", "TestUser")
    if not nickname:
        st.error("별명을 먼저 입력하세요.")
    else:
        types = ["단어시험(주관식)", "작문-99번", "작문-100번", "어순배열"]
        client = get_db_connection() # services.google_sheets에 있는 함수 필요
        if client:
            sheet = client.open("voca_db").sheet1
            rows = []
            for _ in range(20):
                # 랜덤 날짜 (최근 7일)
                rand_date = datetime.now() - timedelta(days=random.randint(0, 7))
                date_str = rand_date.strftime("%Y-%m-%d %H:%M:%S")
                exam = random.choice(types)
                score = random.randint(50, 100)
                rows.append([date_str, nickname, exam, score])
            
            # 한 번에 추가
            sheet.append_rows(rows)
            st.success(f"✅ {nickname}님의 가짜 데이터 20개가 생성되었습니다!")        