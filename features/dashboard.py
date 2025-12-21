# 경로: features/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from services.google_sheets import load_data_by_nickname

def show_dashboard_page():
    st.title("📊 학습 대시보드")
    st.caption("나의 학습 기록과 성장 추이를 한눈에 확인하세요.")

    # 1. 사용자 별명 확인
    nickname = st.session_state.get("nickname", "")
    if not nickname:
        st.warning("⚠️ 사이드바에서 **별명**을 입력해야 기록을 볼 수 있습니다.")
        return

    # 2. 데이터 불러오기
    with st.spinner(f"cloud: {nickname}님의 기록을 가져오는 중..."):
        df = load_data_by_nickname(nickname)

    # 3. 데이터가 없을 때 처리
    if df.empty:
        st.info(f"👋 **{nickname}**님, 아직 학습 기록이 없습니다. 단어시험이나 작문을 시작해보세요!")
        return

    # 4. 데이터 전처리 (날짜 변환 등)
    try:
        # 구글 시트에서 가져온 데이터는 다 문자열일 수 있으므로 형변환
        df['날짜'] = pd.to_datetime(df['날짜'])
        df['점수'] = pd.to_numeric(df['점수'])
        # 날짜순 정렬
        df = df.sort_values(by='날짜')
    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        st.write(df) # 디버깅용 원본 출력
        return

    # =========================================================
    # [섹션 1] 핵심 요약 (Metric)
    # =========================================================
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    total_tests = len(df)
    avg_score = df['점수'].mean()
    last_exam = df.iloc[-1]['시험유형']
    
    col1.metric("총 학습 횟수", f"{total_tests}회")
    col2.metric("전체 평균 점수", f"{avg_score:.1f}점")
    col3.metric("최근 응시 과목", last_exam)

    # =========================================================
    # [섹션 2] 그래프 시각화 (Plotly)
    # =========================================================
    st.subheader("📈 성적 변화 추이")
    
    # [추가] 그래프 사용 가이드 (회원님 요청 반영)
    st.caption("💡 **Tip:** 그래프 오른쪽의 **항목(범례)**들을 클릭하시면, 해당 데이터의 포함 여부를 변경(On/Off)할 수 있습니다.")
    
    tab1, tab2 = st.tabs(["시간별 추세", "유형별 분석"])
    
    with tab1:
        # 꺾은선 그래프: 날짜별 점수 변화 (유형별 색상 구분)
        fig_line = px.line(
            df, 
            x='날짜', 
            y='점수', 
            color='시험유형', 
            markers=True,
            title=f"{nickname}님의 점수 성장 그래프"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        # 막대 그래프: 시험 유형별 평균 점수
        avg_by_type = df.groupby('시험유형')['점수'].mean().reset_index()
        fig_bar = px.bar(
            avg_by_type, 
            x='시험유형', 
            y='점수', 
            text_auto='.1f',
            color='시험유형',
            title="유형별 평균 점수 비교"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # =========================================================
    # [섹션 3] 최근 상세 기록 (Table)
    # =========================================================
    with st.expander("📋 최근 학습 기록 자세히 보기", expanded=True):
        # 최신순으로 정렬해서 보여주기
        display_df = df.sort_values(by='날짜', ascending=False)
        
        # 날짜 포맷 깔끔하게 정리 (문자열 변환)
        display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_df[['날짜', '시험유형', '점수']], 
            use_container_width=True,
            hide_index=True
        )