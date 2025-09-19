import streamlit as st
import os
from zipfile import ZipFile
import io

# try to import normalize (urduhack); fallback to identity
try:
    from urduhack.normalization import normalize as uh_normalize
    def normalize_text(t): return uh_normalize(t)
except Exception:
    def normalize_text(t): return t

ROMAN_MAP = {
    "ا":"a","آ":"aa","ب":"b","پ":"p","ت":"t","ٹ":"t","ث":"s","ج":"j","چ":"ch",
    "ح":"h","خ":"kh","د":"d","ڈ":"d","ر":"r","ڑ":"r","ز":"z","ژ":"zh","س":"s",
    "ش":"sh","ص":"s","ض":"z","ط":"t","ظ":"z","ع":"'","غ":"gh","ف":"f","ق":"q",
    "ک":"k","گ":"g","ل":"l","م":"m","ن":"n","ں":"n","و":"w","ی":"y","ئ":"'","ء":"'","ہ":"h","ھ":"h",
    "َ":"a","ِ":"i","ُ":"u","ٰ":"a"
}

def urdu_to_roman(text: str) -> str:
    return "".join(ROMAN_MAP.get(ch, ch) for ch in text)

def gather_txt_files_from_zip(zip_path, target_dir):
    with ZipFile(zip_path, 'r') as z:
        z.extractall(target_dir)
    out = []
    for root, _, files in os.walk(target_dir):
        for fname in files:
            if fname.lower().endswith('.txt'):
                out.append(os.path.join(root, fname))
    return out

def read_all_lines_from_files(file_list):
    lines = []
    for p in file_list:
        try:
            with open(p, "r", encoding="utf-8") as f:
                for l in f:
                    s = l.strip()
                    if s:
                        lines.append(s)
        except Exception:
            with open(p, "rb") as f:
                try:
                    text = f.read().decode("utf-8", errors="ignore")
                    for l in text.splitlines():
                        s = l.strip()
                        if s:
                            lines.append(s)
                except Exception:
                    pass
    return lines

st.set_page_config(page_title="Urdu Ghazal Processor", layout="wide")
st.title(" Urdu Ghazal Processor (Colab)")

st.markdown("Choose input: type/paste text or upload (.txt or .zip containing .txt files).")

col1, col2 = st.columns([2,1])

with col1:
    option = st.radio("Input method:", [" Type / Paste", "📁 Upload file (.txt or .zip)"])
    text = ""
    uploaded = None
    if option == " Type / Paste":
        text = st.text_area("Paste or type Urdu ghazal here", height=250)
    else:
        uploaded = st.file_uploader("Upload .txt or .zip (zip should contain .txt files)", type=['txt','zip'])
    process_btn = st.button("Process")

with col2:
    st.write("Outputs")
    st.write("- Shows samples (first 5 lines)")
    st.write("- Download buttons for Clean Urdu and Roman Urdu")

if process_btn:
    all_lines = []
    if option != " Type / Paste" and uploaded is not None:
        saved = "/content/uploaded_input"
        os.makedirs(saved, exist_ok=True)
        p = os.path.join(saved, uploaded.name)
        with open(p, "wb") as f:
            f.write(uploaded.getbuffer())
        if uploaded.name.lower().endswith(".zip"):
            txts = gather_txt_files_from_zip(p, os.path.join(saved, "extracted"))
            all_lines = read_all_lines_from_files(txts)
        else:
            all_lines = read_all_lines_from_files([p])
    else:
        for l in text.splitlines():
            s = l.strip()
            if s:
                all_lines.append(s)

    if not all_lines:
        st.warning("No text found. Type/paste or upload a file first.")
    else:
        normalized = [normalize_text(l) for l in all_lines]
        romanized = [urdu_to_roman(l) for l in normalized]

        st.success(f"Processed {len(normalized)} lines.")

        st.subheader("Sample (first 5 lines)")
        for u, r in zip(normalized[:5], romanized[:5]):
            st.markdown(f"<p style='font-size:20px; direction: rtl;'>{u}</p>", unsafe_allow_html=True)
            st.write("Roman:", r)

        clean_path = "/content/all_poems_clean.txt"
        roman_path = "/content/all_poems_roman.txt"
        with open(clean_path, "w", encoding="utf-8") as f:
            f.write("\n".join(normalized))
        with open(roman_path, "w", encoding="utf-8") as f:
            f.write("\n".join(romanized))

        with open(clean_path, "rb") as f:
            st.download_button("⬇ Download Clean Urdu", f.read(), file_name="all_poems_clean.txt", mime="text/plain")
        with open(roman_path, "rb") as f:
            st.download_button("⬇ Download Roman Urdu", f.read(), file_name="all_poems_roman.txt", mime="text/plain")
