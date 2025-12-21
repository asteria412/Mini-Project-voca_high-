# 경로: ui/sidebar.py

import streamlit as st

MENU = ["홈", "단어시험", "어순 연습", "작문", "단어사전", "대시보드"]
# [수정] 아이콘 매핑을 위한 리스트
MENU_ICONS = ["🏠", "📝", "🧩", "✍️", "📚", "📊"]

def show_sidebar():
    # =================================================================
    # [긴급 수정] app.py의 전역 설정(padding 2rem)이 사이드바까지 영향을 줘서
    # 상단이 잘리는 문제를 해결하기 위해, 사이드바만 단독으로 여백을 강제 조정합니다.
    # + [최종 수정] 메뉴 버튼 크기 강제 확대 (Nuclear Option CSS)
    # =================================================================
    st.markdown("""
    <style>
        /* 1. 사이드바 상단 여백 확보 */
        [data-testid="stSidebar"] .block-container {
            padding-top: 5rem !important;
        }

        /* 2. [최종] 메뉴 버튼(pills) 무조건 키우기 */
        /* =================================================================
           [재수정] 메뉴가 메인 영역에 표시되므로, 사이드바 선택자 제거!
           기존: [data-testid="stSidebar"] [data-testid="stPills"]
           변경: [data-testid="stPills"] (메인 영역 타겟팅)
           ================================================================= */
        
        /* (1) 버튼 껍데기(틀) 자체를 키움 */
        /* [재수정] 사이드바 선택자 제거 - 메인 영역의 pills 적용 */
        [data-testid="stPills"] button {
            background-color: #f0f2f6 !important; /* 배경색 살짝 */
            border: 1px solid #dcdcdc !important; /* 테두리 */
            border-radius: 12px !important;       /* 둥글게 */
            margin-bottom: 8px !important;        /* 버튼 사이 간격 */
            padding-top: 15px !important;         /* 위아래 여백 확보 */
            padding-bottom: 15px !important;
        }

        /* (2) [핵심] 버튼 안에 있는 '모든 것(*)'의 폰트 사이즈 강제 주입 */
        /* p태그든 div든 span이든 상관없이 다 20px로 커져라! */
        /* [재수정] 메인 영역이므로 폭 여유 있음 -> 20px 유지 */
        [data-testid="stPills"] button * {
            font-size: 20px !important;  /* 글자 크기 (원하는대로 조절 가능) */
            font-weight: 700 !important; /* 굵게 */
            line-height: 1.5 !important; /* 줄 간격 넉넉히 */
        }
        
        /* (3) 마우스 올렸을 때 효과 */
        [data-testid="stPills"] button:hover {
            border-color: #FF4B4B !important;
            background-color: #ffecec !important;
            color: #FF4B4B !important;
        }
        
        /* (4) 선택된 버튼 스타일 (강조) */
        [data-testid="stPills"] button[aria-selected="true"] {
            background-color: #FF4B4B !important;
            color: white !important;
        }
        /* 선택된 버튼 안의 글자도 흰색으로 */
        [data-testid="stPills"] button[aria-selected="true"] * {
            color: white !important;
        }

    </style>
    """, unsafe_allow_html=True)

    st.sidebar.header("voca海 설정")
    
    # ---------------------------------------------------------
    # 1. 학습자 정보 입력 (체크리스트 수행)
    # ---------------------------------------------------------
    st.sidebar.markdown("### 🔑 학습자 설정")
    
    # 세션에 별명이 없으면 초기화
    if "nickname" not in st.session_state:
        st.session_state["nickname"] = ""
        
    # 입력창 생성
    nickname = st.sidebar.text_input(
        "별명을 입력하세요", 
        value=st.session_state["nickname"],
        placeholder="예: voca_hai",
        help="시험 결과가 이 별명으로 저장됩니다."
    )
    
    # 입력값이 있으면 세션에 저장
    if nickname:
        st.session_state["nickname"] = nickname
        # (선택 사항) 입력 확인 메시지
        st.sidebar.success(f"✅ 접속 중: **{nickname}**님")
        st.sidebar.warning("⚠️ 입력창의 기존 별명을 지우고 다시 입력 시 변경 가능.")
    else:
        st.sidebar.warning("⚠️ 기록 저장을 위해 별명을 입력해주세요.")
        
    st.sidebar.divider()

    # ---------------------------------------------------------
    # 2. 메뉴 선택
    # ---------------------------------------------------------
    
    # [디자인] 상단 잘림 방지를 위해 투명 박스로 공간 확보
    st.sidebar.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # 현재 선택된 메뉴가 없으면 기본값 설정
    if "menu" not in st.session_state:
        st.session_state["menu"] = MENU[0]

    # 현재 메뉴의 인덱스 찾기
    current_menu = st.session_state.get("menu", "홈")
    try:
        default_index = MENU.index(current_menu)
    except ValueError:
        default_index = 0

    # 아이콘 매핑
    icon_map = dict(zip(MENU, MENU_ICONS))
    
    # [잘림 방지 2차] pills 위쪽 여백
    st.sidebar.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # =================================================================
    # [재수정] st.pills 유지 (메인 영역에 메뉴 표시)
    # 현재 스크린샷처럼 메인 영역 상단에 메뉴가 표시되는 디자인 유지.
    # st.sidebar.pills가 아닌 st.pills를 사용해야 메인 영역에 렌더링됨.
    # CSS도 사이드바 선택자 없이 [data-testid="stPills"]만 사용.
    # =================================================================
    selected_menu = st.pills(
        "메뉴 선택", 
        options=MENU,
        # [중요] format_func를 이용해 아이콘을 보여줍니다.
        format_func=lambda x: f"{icon_map[x]} {x}", 
        default=MENU[default_index],
        selection_mode="single",
        label_visibility="collapsed"
    )
    
    # =================================================================
    # [핵심 수정] 더블 클릭 문제 해결 로직 (st.rerun 추가)
    # =================================================================
    
    # 1. 사용자가 선택을 취소(클릭 해제)해서 None이 된 경우 -> 기존 메뉴 유지
    if not selected_menu:
        selected_menu = st.session_state["menu"]

    # 2. 메뉴 변경 감지 -> 즉시 업데이트 및 리런
    if selected_menu != st.session_state["menu"]:
        st.session_state["menu"] = selected_menu
        st.rerun()

    return selected_menu
