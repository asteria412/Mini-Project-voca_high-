import streamlit as st
from ui.tutorial import show_tutorial

def show_home():
    # =================================================================
    # [스타일] 애니메이션 시퀀스 정의
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

        /* 2. 공통 애니메이션 키프레임 */
        @keyframes fadeInUp {
            0% { transform: translateY(30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        /* 3. 요소별 딜레이 설정 */
        .ani-1 { animation: fadeInUp 0.8s ease-out forwards; }           /* 고래 */
        .ani-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; } /* 제목 */
        .ani-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; } /* 캡션 */
        .ani-4 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.9s forwards; } /* 설명박스 */

        /* 4. 요소별 스타일 디테일 */
        
        /* [중요] 고래 크기: 100px로 유지 (요청하신 대로 큼직하게!) */
        .whale-emoji { 
            font-size: 100px; 
            margin-bottom: 10px; 
        }
        
        /* [수정] 제목 크기: 2.2rem으로 조절해서 부담스럽지 않게 */
        .project-title { 
            font-size: 2.2rem !important; 
            font-weight: 700; 
            color: #2c3e50; 
            margin-bottom: 5px !important; 
        }
        
        /* 캡션: 깔끔하게 */
        .caption-text { 
            color: #666; 
            font-size: 1.0rem; 
            margin-bottom: 30px; 
        }
        
        /* 설명 박스: 텍스트 위주로 심플하게 */
        .intro-box {
            font-size: 1.0rem;
            line-height: 1.7;
            color: #444;
            max-width: 700px;
            margin-top: 10px;
        }
        /* [추가] 하단 안내 박스(Info, Success) 글자 크기 조절 */
        /* 원래보다 약간 작게(0.9rem) 줄여서 한 줄에 예쁘게 넣기 */
        .stAlert p {
            font-size: 0.95rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # =================================================================
    # [화면 구성] 중앙 정렬 레이아웃
    # =================================================================
    # 가운데 비율(1.2)은 유지해서 양옆 여백을 확보합니다.
    _, col_center, _ = st.columns([1, 1.2, 1])

    with col_center:
        # 애니메이션 그룹
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

        # 하단 안내
        st.markdown("---")
        st.markdown("### 🌊 자, 이제 단어의 바다로~! 🏄")
        
        st.info("👈 사이드바에서 **별명을 입력하고 메뉴를 선택**해 학습을 시작해보세요.")
        st.success("💡 처음이라면, 더 효과적인 학습을 위해 **하단의 튜토리얼**을 먼저 확인해보세요!")
        
        st.write("") 
        show_tutorial(expanded=False)