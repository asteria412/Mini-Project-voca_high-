import streamlit as st
from ui.tutorial import show_tutorial

def show_home():
    # 1. 스타일 정의 (CSS)
    # [중요] <style> 태그부터 왼쪽 끝에 붙입니다.
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
    
    .home-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

    # =================================================================
    # 2. 메인 콘텐츠 (컬럼 사용 X -> 화면 전체 사용)
    # =================================================================
    # [중요] 여기 HTML 코드는 무조건 왼쪽 벽에 붙어있어야 합니다!!!
    st.markdown("""
<div class="home-container">

<div class="ani-1" style="font-size: 80px; margin-bottom: 0px;">🐋</div>

<div class="ani-2">
<h1 style="font-size: 3rem !important; font-weight: 800; color: #2c3e50; margin: 0; line-height: 1.2; white-space: nowrap;">
[voca海(hǎi) | voca high]
</h1>
</div>

<div class="ani-3" style="color: #666; font-size: 1.1rem; margin-top: 10px; margin-bottom: 20px;">
단어의 바다에서 자유로이 날다!
</div>

<div class="ani-4" style="font-size: 1rem; line-height: 1.6; color: #444; max-width: 800px;">
보카하이는 <b>HSK 등 중국어 시험</b>을 준비하는 학습자를 위한<br>
<b>자료(단어장) + AI 기반</b> 단어 및 작문 학습 페이지입니다.
</div>

</div>
""", unsafe_allow_html=True)

    # 3. 하단 안내 및 튜토리얼 (여기는 파이썬 코드라 들여쓰기 됨)
    # 아래쪽은 너무 퍼지면 보기 싫으니 살짝 모아줍니다.
    _, col_bottom, _ = st.columns([1, 4, 1])
    with col_bottom:
        st.markdown("---")
        # [중요] 여기도 마크다운 텍스트는 왼쪽에 붙여야 안전합니다.
        st.markdown("### 🌊 자, 이제 단어의 바다로~! 🏄") 
        
        st.info("👈 사이드바에서 **별명을 입력하고 메뉴를 선택**해 학습을 시작해보세요.")
        st.success("💡 처음이라면, 더 효과적인 학습을 위해 **하단의 튜토리얼**을 먼저 확인해보세요!")
        
        st.write("") 
        show_tutorial(expanded=False)