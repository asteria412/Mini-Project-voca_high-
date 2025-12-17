# features/vocab_upload.py
import streamlit as st

def show_vocab_upload():
    st.subheader("📄 단어장 업로드")

    uploaded_file = st.file_uploader(
        "PDF 또는 TXT 단어장을 업로드하세요",
        type=["pdf", "txt"]
    )

    if uploaded_file:
        filename = uploaded_file.name

        # 1차 분기_해커스 파일이 주여서 해커스와 일반으로 나눔 
        source_type = "hackers" if "해커스" in filename else "generic"

        st.session_state["uploaded_file"] = uploaded_file
        st.session_state["source_type"] = source_type
        st.session_state["uploaded_filename"] = filename

        st.success(f"업로드 완료: {filename}")
        st.caption("이제 텍스트를 읽어 단어장을 구성할게요.")
