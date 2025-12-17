# features/vocab_upload.py
import streamlit as st

from core.text_change import change_text_from_upload
from core.vocab_parser import change_text_to_vocab_df


def show_vocab_upload():
    st.subheader("단어장 업로드")

    uploaded_file = st.file_uploader(
        "PDF 또는 TXT 단어장을 업로드하세요",
        type=["pdf", "txt"]
    )

    if uploaded_file is None:
        st.info("단어장 파일을 업로드해주세요.")
        return

    # ① 파일 → 텍스트
    text = change_text_from_upload(uploaded_file)

    if not text.strip():
        st.error("텍스트를 읽어오지 못했습니다.")
        return

    with st.expander("추출된 텍스트 미리보기"):
        st.text(text[:4000])

    # ② 텍스트 → 단어장 (여기서 끝)
    df = change_text_to_vocab_df(
        text,
        level="HSK",
        source=uploaded_file.name
    )

    if df.empty:
        st.warning(
            "단어를 추출하지 못했습니다.\n"
            "- PDF가 스캔본일 수 있습니다.\n"
            "- 또는 구조가 특이한 파일입니다."
        )
        return

    st.success(f"단어장 생성 완료! ({len(df)}개)")
    st.dataframe(df, use_container_width=True)
