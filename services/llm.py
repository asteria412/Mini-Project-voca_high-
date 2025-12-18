# services/llm.py
import os, json
import pandas as pd
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# [프롬프트 수정] 채우기가 아닌 '존재 증거 찾기'에 집중
SYSTEM_PROMPT = """
당신은 '단어장 무결성 검수자'입니다. 
파서가 추출한 항목이 원본 텍스트 내에서 실제 '단어'로서 유효한지 검증하세요.

[임무]
1. 제시된 한자가 원본 조각 내에서 단어-병음-뜻의 구조를 가진 '진짜 단어'인지 확인하세요.
2. 진짜라면 원본에 적힌 병음과 뜻을 정확히 추출하세요.
3. 만약 한자가 단어가 아닌 단순 텍스트(페이지 번호, 섹션 제목, 예문 파편 등)라면 반드시 is_noise: true로 응답하세요.

반드시 JSON으로 응답: {"zh": "한자", "pinyin": "병음", "ko": "뜻", "is_noise": false/true}
"""

def process_vocab_with_llm(df, raw_text):
    """
    df: 1차 파싱된 데이터 (개수 상관 없음)
    raw_text: PDF 전체 원본
    """
    if df.empty: return df
    
    # 1. 수리가 필요한 '빈칸 행'들만 핀포인트로 추출
    repair_targets = df[df['flags'] != 'OK'].copy()
    if repair_targets.empty: return df

    progress_bar = st.progress(0)
    indices_to_drop = [] # 노이즈(가짜 단어)로 판명된 행 보관함

    # 2. 유기적 대조 시작
    for i, (idx, row) in enumerate(repair_targets.iterrows()):
        target_zh = row['zh']
        
        # [원리] find()로 원본 내 '좌표' 확보하여 잽싸게 이동
        char_pos = raw_text.find(target_zh)
        
        if char_pos != -1:
            # 해당 단어 앞뒤 500자 조각(Context) 슬라이싱
            snippet = raw_text[max(0, char_pos-100) : min(len(raw_text), char_pos+400)]
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"검수 단어: {target_zh}\n원본 조각: {snippet}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                res = json.loads(response.choices[0].message.content)
                
                # AI가 노이즈로 판별하면 삭제 리스트에 등록
                if res.get('is_noise') is True:
                    indices_to_drop.append(idx)
                else:
                    # 진짜 단어면 정보 업데이트 및 OK 부여
                    df.at[idx, 'pinyin'] = res.get('pinyin', row['pinyin'])
                    df.at[idx, 'ko'] = res.get('ko', row['ko'])
                    df.at[idx, 'flags'] = 'OK'
            except:
                pass
        else:
            # 원본에 한자 자체가 없으면 유령 데이터이므로 삭제
            indices_to_drop.append(idx)
        
        progress_bar.progress((i + 1) / len(repair_targets))

    # 3. [최종 정제] 가짜 단어들을 쳐내어 개수를 원본에 맞게 수렴시킴
    if indices_to_drop:
        df = df.drop(indices_to_drop)
        df = df.reset_index(drop=True)

    return df