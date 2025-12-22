import streamlit as st
from ui.tutorial import show_tutorial

def show_home():
    # 1. 애니메이션 규칙 정의 (CSS)
    # 여기는 파이썬 코드가 아니라 CSS 영역이라 들여쓰기해도 괜찮지만, 
    # 헷갈리니 그냥 다 왼쪽으로 붙이겠습니다.
    st.markdown("""
<style>
    @keyframes fadeInUp {
        0% { transform: translateY(30px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .ani-1 { animation: fadeInUp 0.8s ease-out forwards; }
    .ani-2 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.3s forwards; }
    .ani-3 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.6s forwards; }
    .ani-4 { opacity: 0; animation: fadeInUp 0.8s ease-out 0.9s forwards; }
</style>
""", unsafe_allow_html=True)

    # 2. 화면 구성 (레이아웃)
    _, col_center, _ = st.columns([1, 1.5, 1])

    with col_center:
        # 🚨 [가장 중요] 여기 HTML 코드들은 왼쪽 끝(벽)에 딱 붙어있어야 합니다!
        # style="..." 안에 글자 크기(px)를 강제로 넣어서 사이즈 문제도 해결했습니다.
        st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; text-align: center;">
<div class="ani-1" style="font-size: 80px; margin-bottom: 0px;">🐋</div>
<div class="ani-2">
<h1 style="font-size: 32px !important; font-weight: 800; color: #2c3e50; margin: 0; line-height: 1.2;">[voca海(hǎi) | voca high]</h1>
</div>
<div class="ani-3" style="color: #666; font-size: 16px; margin-top: 10px; margin-bottom: 20px;">
단어의 바다에서 자유로이 날다!
</div>
<div class="ani-4" style="font-size: 15px; line-height: 1.6; color: #444;">
보카하이는 <b>HSK 등 중국어 시험</b>을 준비하는 학습자를 위한<br>
<b>자료(단어장) + AI 기반</b> 단어 및 작문 학습 페이지입니다.
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🌊 자, 이제 단어의 바다로~! 🏄")
        st.info("👈 사이드바에서 **별명을 입력하고 메뉴를 선택**해 학습을 시작해보세요.")
        st.success("💡 처음이라면, 더 효과적인 학습을 위해 **하단의 튜토리얼**을 먼저 확인해보세요!")
        st.write("") 
        show_tutorial(expanded=False)

# 배포 트리거용 주석 (이 줄을 추가하고 저장하세요)        