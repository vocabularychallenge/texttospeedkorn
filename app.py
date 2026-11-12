import re
from io import BytesIO

import streamlit as st
from gtts import gTTS
from pydub import AudioSegment

st.set_page_config(page_title="อ่านข้อความเป็นเสียง", page_icon="🔊", layout="centered")
st.title("🔊 อ่านข้อความเป็นเสียง")
st.caption("แปลงข้อความภาษาไทยและภาษาอังกฤษเป็นไฟล์ MP3 ด้วย Google Text-to-Speech")

MAX_CHARS = 3000
MAX_SEGMENT_CHARS = 180


def split_by_language(text: str) -> list[tuple[str, str]]:
    """Group adjacent Thai/English spans while retaining spaces and punctuation."""
    tokens = re.findall(r"[\u0E00-\u0E7F]+|[A-Za-z]+(?:['’][A-Za-z]+)*|\d+(?:[.,]\d+)*|\s+|[^\w\s]+|.", text)
    chunks: list[tuple[str, str]] = []
    current_lang = "th"
    for token in tokens:
        if re.search(r"[\u0E00-\u0E7F]", token):
            lang = "th"
        elif re.search(r"[A-Za-z]", token):
            lang = "en"
        else:
            lang = current_lang
        if chunks and chunks[-1][0] == lang:
            chunks[-1] = (lang, chunks[-1][1] + token)
        else:
            chunks.append((lang, token))
        current_lang = lang
    return [(lang, phrase.strip()) for lang, phrase in chunks if phrase.strip()]


def split_long_phrase(phrase: str, max_chars: int = MAX_SEGMENT_CHARS) -> list[str]:
    """Split without dropping characters; avoid gTTS request-size limits."""
    if len(phrase) <= max_chars:
        return [phrase]
    parts = []
    remaining = phrase
    while len(remaining) > max_chars:
        # Prefer natural breaks, but Thai may have no spaces.
        cut = max(remaining.rfind(sep, 0, max_chars + 1) for sep in (" ", "\n", ".", ",", "!", "?", "。", "，"))
        if cut < max_chars // 3:
            cut = max_chars
        else:
            cut += 1
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:]
    if remaining.strip():
        parts.append(remaining.strip())
    return [part for part in parts if part]


@st.cache_data(show_spinner=False, ttl=3600, max_entries=32)
def create_mp3(text: str, slow: bool) -> bytes:
    if not text.strip():
        raise ValueError("กรุณาใส่ข้อความก่อนสร้างเสียง")
    if len(text) > MAX_CHARS:
        raise ValueError(f"ข้อความต้องไม่เกิน {MAX_CHARS:,} ตัวอักษร")
    segments = []
    for lang, phrase in split_by_language(text):
        for part in split_long_phrase(phrase):
            buffer = BytesIO()
            gTTS(text=part, lang=lang, slow=slow).write_to_fp(buffer)
            buffer.seek(0)
            segments.append(AudioSegment.from_file(buffer, format="mp3"))
    if not segments:
        raise ValueError("ไม่มีข้อความที่สามารถอ่านได้")
    combined = AudioSegment.empty()
    for segment in segments:
        combined += segment
    result = BytesIO()
    combined.export(result, format="mp3", bitrate="128k")
    return result.getvalue()


text = st.text_area(
    "ข้อความที่ต้องการให้อ่าน",
    placeholder="ตัวอย่าง: สวัสดีค่ะ วันนี้เราจะมาแนะนำ Text to Speech",
    height=180,
    max_chars=MAX_CHARS,
)
slow = st.checkbox("อ่านช้า (Slow)", value=False)
st.caption(f"{len(text):,} / {MAX_CHARS:,} ตัวอักษร • ต้องเชื่อมต่ออินเทอร์เน็ตเพื่อสร้างเสียง")

if "mp3_data" not in st.session_state:
    st.session_state.mp3_data = None
if "last_request" not in st.session_state:
    st.session_state.last_request = None

if st.button("สร้างเสียง MP3", type="primary", disabled=not text.strip(), use_container_width=True):
    try:
        with st.spinner("กำลังสร้างไฟล์ MP3..."):
            mp3 = create_mp3(text.strip(), slow)
        st.session_state.mp3_data = mp3
        st.session_state.last_request = (text.strip(), slow)
        st.success("สร้างเสียงสำเร็จ")
    except Exception as error:
        st.session_state.mp3_data = None
        st.session_state.last_request = None
        st.error(f"สร้างเสียงไม่สำเร็จ: {error}")
        st.info("ตรวจสอบอินเทอร์เน็ตและการติดตั้ง FFmpeg แล้วลองอีกครั้ง")

if st.session_state.mp3_data and st.session_state.last_request == (text.strip(), slow):
    st.audio(st.session_state.mp3_data, format="audio/mpeg")
    st.download_button(
        "⬇️ ดาวน์โหลด MP3",
        data=st.session_state.mp3_data,
        file_name="speech.mp3",
        mime="audio/mpeg",
        use_container_width=True,
    )
