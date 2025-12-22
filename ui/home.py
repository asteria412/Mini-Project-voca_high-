import streamlit as st
from ui.tutorial import show_tutorial

def show_home():
    # =================================================================
    # [스타일] CSS 정의 (확 줄인 버전)
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

        /* 2. 애니메이션 키프레임 */
        @keyframes fadeInUp {
            0% { transform: translateY(30px); opacity: 0; }
            100% { transform: translateY(0); opacity: 1; }
        }

        /* 3. 요소별 딜레이 */
        .ani-1 { animation: fadeInUp 0.8s ease-out forwards; }
        .ani-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; }
        .ani-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; }
        .ani-4 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.9s forwards; }
        
        /* 4. [수정됨] 요소별 사이즈 대폭 축소 */
        
        /* 고래: 100px 유지 (요청하신 대로 포인트!) */
        .whale-emoji { 
            font-size: 100px; 
            margin-bottom: 0px; /* 고래 밑 여백 줄임 */
        }
        
        /* [핵심 수정] 제목: 2.2rem -> 1.8rem (확 줄여서 한 줄에 나오게) */
        .project-title { 
            font-size: 1.8rem !important; 
            font-weight: 800; /* 두께는 유지해서 존재감 있게 */
            color: #2c3e50; 
            margin-bottom: 5px !important;
            line-height: 1.2; /* 줄간격 좁히기 */
        }
        
        /* 캡션: 1.0rem -> 0.9rem (작고 귀엽게) */
        .caption-text { 
            color: #666; 
            font-size: 0.9rem; 
            margin-bottom: 20px; 
        }
        
        /* 본문 박스: 1.0rem -> 0.9rem */
        .intro-box {
            font-size: 0.9rem;
            line-height: 1.6;
            color: #444;
            max-width: 700px;
            margin-top: 5px;
        }

        /* 하단 안내 박스 글자 크기 */
        .stAlert p {
            font-size: 0.9rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # =================================================================
    # [화면 구성]
    # =================================================================
    # 가운데 비율을 조금 더 넓혀서(1.2 -> 1.5) 제목이 덜 꺾이게 만듭니다.
    _, col_center, _ = st.columns([1, 1.5, 1])

    with col_center:
        # [중요] HTML 코드는 왼쪽 끝에 붙여야 함 (들여쓰기 X)
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