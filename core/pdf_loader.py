# core/pdf_loader.py
def change_file_to_text(uploaded_file) -> str:
    """
    PDF / TXT 파일을 받아서 전체 텍스트(str)로 바꾼다
    """
    if uploaded_file is None:
        return ""

    # TXT 파일
    if uploaded_file.name.lower().endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    # PDF 파일
    if uploaded_file.name.lower().endswith(".pdf"):
        try:
            import pymupdf as fitz
        except:
            import fitz

        text = ""
        pdf_bytes = uploaded_file.getvalue()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            text += page.get_text()

        return text

    return ""

