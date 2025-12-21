# 경로: ui/home.py
import streamlit as st
from ui.tutorial import show_tutorial

def show_home():
    # =================================================================
    # [스타일] 애니메이션 시퀀스 정의 (순차적 등장)
    # =================================================================
    st.markdown("""
    <style>
        /* 1. 전체 컨테이너 중앙 정렬 */
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        /* 2. 공통 애니메이션 키프레임 (아래에서 위로 투명도 조절) */
        @keyframes fadeInUp {
            0% { transform: translateY(30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        /* 3. 요소별 딜레이 설정 (순서대로 뿅뿅뿅 나타나게) */
        .ani-1 { animation: fadeInUp 0.8s ease-out forwards; }           /* 고래 */
        .ani-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; } /* 제목 */
        .ani-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; } /* 캡션 */
        .ani-4 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.9s forwards; } /* 설명박스 */

        /* 4. 각 요소 스타일 */
        .whale-emoji { font-size: 100px; margin-bottom: 10px; }
        .project-title { font-weight: 700; color: #2c3e50; margin-bottom: 5px !important; }
        .caption-text { color: #666; font-size: 1.1rem; margin-bottom: 30px; }
        
        /* [수정] 박스 스타일(배경, 그림자)을 제거하고 텍스트만 남김 */
        .intro-box {
            /* background-color: #f8f9fa;  <-- 삭제 (배경 제거) */
            /* padding: 25px;              <-- 삭제 (박스 패딩 제거) */
            /* border-radius: 15px;        <-- 삭제 */
            /* box-shadow: ...;            <-- 삭제 (그림자 제거) */
            
            font-size: 1.1rem;
            line-height: 1.7;
            color: #444;
            max-width: 700px; /* 너무 넓어지지 않게 */
            margin-top: 10px; /* 박스 패딩이 빠진 대신 약간의 여백 추가 */
        }
    </style>
    """, unsafe_allow_html=True)

    # =================================================================
    # [화면 구성] 중앙 정렬 레이아웃
    # =================================================================
    _, col_center, _ = st.columns([1, 2, 1])

    with col_center:
        # 1. 애니메이션 그룹 (HTML로 한 번에 묶어서 렌더링)
        # [수정] 들여쓰기 제거! 왼쪽 끝에 붙여야 코드로 인식되지 않습니다.
        st.markdown("""
<div class="main-container">
<div class="whale-emoji ani-1">🐋</div>
<div class="ani-2">
<h1 class="project-title">[voca海(hǎi) | voca high]</h1>
</div>
<div class="caption-text ani-3">
단어의 바다에서 자유로이 날다!
</div>
<div class="intro-box ani-4">
보카하이는 <b>HSK 등 중국어 시험</b>을 준비하는 학습자를 위한<br>
<b>자료(단어장) + AI 기반</b> 단어 및 작문 학습 페이지입니다.
</div>
</div>
""", unsafe_allow_html=True)

        # 하단 안내 (고정)
        st.markdown("---")
        st.markdown("### 🌊 자, 이제 단어의 바다로~! 🏄")
        
        st.info("👈 사이드바에서 **별명을 입력하고 메뉴를 선택**해 학습을 시작해보세요.")
        st.success("💡 처음이라면, 더 효과적인 학습을 위해 **하단의 튜토리얼**을 먼저 확인해보세요!")
        
        # [추가] 튜토리얼 모듈 호출
        # 컬럼 안에 넣었으므로 너비가 위쪽 콘텐츠들과 동일하게 맞춰집니다.
        st.write("") # 디자인 여백
        show_tutorial(expanded=False)