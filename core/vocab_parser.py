# core/vocab_parser.py
# 목표:
# - 파일을 해커스/비해커스로 "단정"하지 않고, 줄(line) 단위로 패턴을 감지해서 best-effort 파싱
# - 해커스(단어+병음+품사+뜻) / 해커스(예문 포함) / 비해커스(괄호병음-뜻) / 혼합형 모두 대응
# - 예문 문장(긴 한자 + 문장부호)은 단어로 잡지 않도록 방지
# - ko 칸에 들어오는 □3급 같은 노이즈 제거

import re
import unicodedata
import pandas as pd


# -----------------------------
# 기본 설정
# -----------------------------
POS_SET = {
    "명사", "동사", "형용사", "부사",
    "개사", "접속사", "조사", "양사", "대명사",
    "명", "동", "형", "부", "개", "접", "조", "양", "대",
}

PUNCT_ZH = set(["。", "，", "？", "！", "；", "：", "、", "…", "．", ".", ",", "?", "!", ";", ":"])

HANZI_RE = re.compile(r"^[\u4e00-\u9fff]+$")
HANZI_BLOCK_RE = re.compile(r"([\u4e00-\u9fff]{1,12})")

# 병음: 알파벳+성조(ü 포함), 공백/하이픈/중점 허용
PINYIN_ALLOWED_RE = re.compile(r"^[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ\s\-·]+$", re.I)

# 해커스 표(한 줄)에 종종 나오는:  汉字  pinyin  품사  뜻
ROW_ZH_PINYIN_POS_KO = re.compile(
    r"^(?P<zh>[\u4e00-\u9fff]{1,6})\s+"
    r"(?P<pinyin>[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ·\-\s]+?)\s+"
    r"(?P<pos>명사|동사|형용사|부사|개사|접속사|조사|양사|대명사|명|동|형|부|개|접|조|양|대)\s+"
    r"(?P<ko>.+)$"
)

# 해커스 변형: 汉字  pinyin  뜻 (품사 없음)
ROW_ZH_PINYIN_KO = re.compile(
    r"^(?P<zh>[\u4e00-\u9fff]{1,6})\s+"
    r"(?P<pinyin>[a-züāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ·\-\s]+?)\s+"
    r"(?P<ko>.+)$"
)

# 비해커스: 汉字 (pinyin) - 뜻
ROW_BRACKET = re.compile(
    r"^(?P<zh>[\u4e00-\u9fff]{1,10})\s*"
    r"\((?P<pinyin>[^)]+)\)\s*[-–]\s*(?P<ko>.+)$"
)

# 비해커스 변형: ko에 (pinyin) - 뜻이 같이 박혀오는 케이스도 있음 (앞에 번호 붙기도 함)
ROW_KO_WITH_PINYIN = re.compile(
    r"^(?P<num>\d+[\.\)]\s*)?(?P<pinyin>\([^)]+\))\s*[-–]\s*(?P<ko>.+)$"
)

# 체크박스/레벨 노이즈
CHECKBOX_RE = re.compile(r"[□■○●]")
LEVEL_NOISE_RE = re.compile(r"(HSK\s*\d+급|\d+\s*급|[1-6]\s*급)")

# 번호 라인
INDEX_RE = re.compile(r"^\d{2,4}$")


# -----------------------------
# 유틸
# -----------------------------
def norm(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u00a0", " ").replace("\u200b", " ").replace("\ufeff", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def looks_like_pinyin(s: str) -> bool:
    s = norm(s).lower()
    if not s or len(s) > 180:
        return False
    return bool(PINYIN_ALLOWED_RE.fullmatch(s))


def extract_hanzi_block(line: str) -> str | None:
    line = norm(line)
    m = HANZI_BLOCK_RE.search(line)
    return m.group(1) if m else None


def is_example_zh_line(line: str, zh_block: str) -> bool:
    # 문장부호 있으면 거의 예문
    if any(p in line for p in PUNCT_ZH):
        return True
    # 한자 덩어리가 너무 길면 예문 확률 ↑
    if len(zh_block) >= 8:
        return True
    return False


def clean_ko(s: str) -> str:
    s = norm(s)
    s = CHECKBOX_RE.sub("", s)
    # □3급 같은 레벨 노이즈 제거
    s = LEVEL_NOISE_RE.sub("", s)
    s = s.replace("·", ", ")
    s = re.sub(r"\s*,\s*", ", ", s)
    s = re.sub(r"\s+", " ", s).strip(" ,")
    return s


def split_pos_prefix_ko(line: str):
    # "동 뛰다" / "명 사람" / "동사 ..." 형태 제거
    s = norm(line)
    parts = s.split(maxsplit=1)
    if len(parts) == 2 and parts[0] in POS_SET:
        return parts[0], parts[1].strip()
    return None, s


# -----------------------------
# 메인 파서: text -> df
# -----------------------------
def change_text_to_vocab_df(extracted_text: str, level="HSK", source="generic") -> pd.DataFrame:
    text = extracted_text or ""
    lines = [norm(ln) for ln in text.splitlines()]

    rows = []

    # 상태(멀티라인 구조 대응)
    current_pos = None
    pending_zh = None
    pending_pinyin = None
    pending_ko = None

    def flush():
        nonlocal pending_zh, pending_pinyin, pending_ko, current_pos
        if pending_zh:
            rows.append({
                "zh": pending_zh,
                "pinyin": pending_pinyin,
                "ko": pending_ko,
                "pos": current_pos,
                "level": level,
                "source": source,
            })
        pending_zh = None
        pending_pinyin = None
        pending_ko = None

    for raw in lines:
        if not raw:
            continue

        # 번호 라인 나오면 단어 경계로 flush
        if INDEX_RE.fullmatch(raw):
            flush()
            continue

        # 0) 한 줄 완성형 먼저 처리 (가장 정확)
        m = ROW_ZH_PINYIN_POS_KO.match(raw)
        if m:
            flush()
            pending_zh = norm(m.group("zh"))
            pending_pinyin = norm(m.group("pinyin"))
            current_pos = norm(m.group("pos"))
            pending_ko = clean_ko(m.group("ko"))
            flush()
            continue

        m = ROW_BRACKET.match(raw)
        if m:
            flush()
            pending_zh = norm(m.group("zh"))
            pending_pinyin = norm(m.group("pinyin"))
            pending_ko = clean_ko(m.group("ko"))
            current_pos = None
            flush()
            continue

        # 1) "품사 + 내용" 한 줄 (해커스 품사별 헤쳐모여에서 자주 등장)
        pos_prefix, rest = split_pos_prefix_ko(raw)
        if pos_prefix and rest:
            # pos는 업데이트
            current_pos = pos_prefix

            # rest가 한자면 단어 후보
            zh = extract_hanzi_block(rest)
            if zh:
                # 예문이면 무시 (이미 단어 잡고 있는 상태면 특히)
                if pending_zh and is_example_zh_line(rest, zh):
                    continue
                flush()
                pending_zh = zh
                continue

            # rest가 뜻이면 ko로
            if pending_zh and pending_ko is None and re.search(r"[가-힣]", rest):
                pending_ko = clean_ko(rest)
                continue

            # rest가 병음이면 pinyin으로
            if pending_zh and pending_pinyin is None and looks_like_pinyin(rest):
                pending_pinyin = norm(rest)
                continue

        # 2) 단독 품사 라인
        if raw in POS_SET:
            current_pos = raw
            continue

        # 3) 이미 단어를 잡은 상태에서 병음 줄
        if pending_zh and pending_pinyin is None and looks_like_pinyin(raw):
            pending_pinyin = raw
            continue

        # 4) 이미 단어를 잡은 상태에서 뜻 줄
        if pending_zh and pending_ko is None and re.search(r"[가-힣]", raw):
            # ko 줄 내부에 "(pinyin) - 뜻"이 들어오면 분리해서 pinyin 채우기
            km = ROW_KO_WITH_PINYIN.match(raw)
            if km and pending_pinyin is None:
                pending_pinyin = km.group("pinyin").strip("() ").strip()
                pending_ko = clean_ko(km.group("ko"))
            else:
                pending_ko = clean_ko(raw)
            continue

        # 5) 한자 덩어리 등장: 단어/예문 후보
        zh = extract_hanzi_block(raw)
        if zh:
            # 예문이면 단어로 갈아타지 않음
            if pending_zh and is_example_zh_line(raw, zh):
                continue

            # 해커스 변형: "汉字 pinyin 뜻" (품사 없음)도 여기서 한 번 더 잡아줌
            m2 = ROW_ZH_PINYIN_KO.match(raw)
            if m2 and looks_like_pinyin(m2.group("pinyin")):
                flush()
                pending_zh = norm(m2.group("zh"))
                pending_pinyin = norm(m2.group("pinyin"))
                pending_ko = clean_ko(m2.group("ko"))
                # pos는 유지(품사별 파트면 위에서 잡힘), 아니면 None로 두고 싶으면 아래 줄 주석 해제
                # current_pos = None
                flush()
                continue

            # 그냥 단어 후보
            flush()
            pending_zh = zh
            continue

        # 6) 그 외: 아무 것도 못 붙이면 넘어감

    flush()
    return pd.DataFrame(rows)
