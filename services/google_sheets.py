# 경로: services/google_sheets.py
# [설명] 구글 시트 인증 및 데이터 저장 함수

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# 1. 구글 시트 인증 및 연결
def get_db_connection():
    try:
        # 인증 범위 설정
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # secrets.toml에서 정보 가져오기
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        # gspread 연결
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

# 2. 점수 저장 함수
def save_score(nickname, exam_type, score):
    """
    [기능] 학습자의 시험 결과를 구글 시트에 행(Row)으로 추가합니다.
    - nickname: 학습자 별명
    - exam_type: 시험 종류 (예: 단어시험, 작문)
    - score: 점수
    """
    client = get_db_connection()
    if not client:
        return False

    try:
        # [중요] 시트 이름이 'voca_db'여야 합니다. (다르면 수정 필요)
        sheet = client.open("voca_db").sheet1
        
        # 현재 시간 (한국 포맷)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 저장할 데이터 리스트
        row_data = [current_time, nickname, exam_type, score]
        
        # 시트에 한 줄 추가 (append_row)
        sheet.append_row(row_data)
        return True
        
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")
        return False

# 3. 데이터 불러오기 함수 (대시보드용)
def load_data_by_nickname(nickname):
    """
    [기능] 구글 시트에서 특정 별명(nickname)을 가진 사람의 기록만 싹 긁어옵니다.
    """
    client = get_db_connection()
    if not client:
        return pd.DataFrame() # 연결 실패 시 빈 표 반환

    try:
        sheet = client.open("voca_db").sheet1
        
        # 시트의 모든 데이터를 가져옴 (리스트 형태)
        all_records = sheet.get_all_records()
        
        # Pandas DataFrame(표)으로 변환
        df = pd.DataFrame(all_records)
        
        # 데이터가 비어있으면 빈 표 반환
        if df.empty:
            return pd.DataFrame()

        # [핵심 로직] 내 별명과 똑같은 행만 필터링!
        # (구글 시트 헤더가 '별명'이어야 함)
        my_data = df[df['별명'] == nickname]
        
        return my_data
        
    except Exception as e:
        print(f"데이터 불러오기 오류: {e}")
        return pd.DataFrame()    