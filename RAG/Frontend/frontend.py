import html
import io
import streamlit as st
import requests
import xml.etree.ElementTree as ET
import zipfile

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from chunking import split_text

st.set_page_config(
    page_title="RAG | Knowledge Workspace",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000"

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">

<style>
:root {
    --bg: #090b12;
    --sidebar: #0e111a;
    --panel: rgba(20, 24, 37, .82);
    --border: rgba(151, 164, 196, .14);
    --primary: #a78bfa;
    --text: #f3f4fb;
    --muted: #9aa3b8;
}

.stApp {
    background:
        radial-gradient(ellipse at 82% 4%, rgba(107, 75, 235, .16), transparent 34rem),
        radial-gradient(ellipse at 12% 38%, rgba(30, 144, 188, .08), transparent 30rem),
        var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #10131d 0%, #0c0f17 100%);
    border-right: 1px solid var(--border);
}

.block-container {
    max-width: 1160px;
    padding-top: 2rem;
    padding-bottom: 4rem;
    animation: page-enter .65s cubic-bezier(.2, .7, .2, 1) both;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f5f6ff;
}

.brand span {
    color: #818cf8;
}

.brand-icon {
    display: inline-flex;
    width: 39px;
    height: 39px;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #5c6cf5, #a855f7);
    border-radius: 12px;
    color: white;
    margin-right: 10px;
    box-shadow: 0 7px 22px rgba(120, 91, 246, .28);
    animation: icon-float 4s ease-in-out infinite;
}

.sidebar-label {
    color: #788397;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin: 26px 0 12px 2px;
}

.status {
    background: linear-gradient(120deg, rgba(20, 83, 61, .24), rgba(15, 30, 29, .72));
    border: 1px solid rgba(74, 222, 128, .19);
    color: #86efac;
    border-radius: 9px;
    padding: 11px 12px;
    font-size: 12px;
}

.hero-panel {
    position: relative;
    overflow: hidden;
    padding: 32px 34px 30px;
    border: 1px solid rgba(170, 155, 255, .18);
    border-radius: 24px;
    background:
        radial-gradient(ellipse at 88% 8%, rgba(131, 94, 255, .25), transparent 25rem),
        linear-gradient(120deg, rgba(24, 28, 44, .96), rgba(15, 19, 31, .9));
    box-shadow: 0 22px 65px rgba(0, 0, 0, .2), inset 0 1px rgba(255, 255, 255, .045);
    margin-bottom: 28px;
}

.hero-panel::after {
    content: "";
    position: absolute;
    width: 280px;
    height: 280px;
    right: -80px;
    top: -165px;
    border: 1px solid rgba(196, 181, 253, .17);
    border-radius: 50%;
    box-shadow: 0 0 0 28px rgba(167, 139, 250, .035), 0 0 0 58px rgba(167, 139, 250, .025);
    pointer-events: none;
    animation: orbit-drift 12s ease-in-out infinite alternate;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border: 1px solid rgba(196, 181, 253, .19);
    border-radius: 999px;
    background: rgba(139, 92, 246, .1);
    color: #c4b5fd;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.35px;
    text-transform: uppercase;
}

.hero-eyebrow i {
    font-size: 11px;
    animation: sparkle 2.2s ease-in-out infinite;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(30px, 4vw, 43px);
    font-weight: 800;
    letter-spacing: -1.8px;
    line-height: 1.13;
    color: #f7f7ff;
    margin: 17px 0 9px;
    position: relative;
    z-index: 1;
}

.hero-subtitle {
    max-width: 620px;
    color: #a6aec2;
    font-size: 14px;
    line-height: 1.7;
    position: relative;
    z-index: 1;
}

.hero-accent {
    color: #c4b5fd;
}

.feature-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(145deg, rgba(25, 30, 46, .94), rgba(16, 20, 31, .9));
    border: 1px solid var(--border);
    padding: 21px;
    border-radius: 17px;
    min-height: 142px;
    transition: transform .24s ease, border-color .24s ease, box-shadow .24s ease;
    animation: card-enter .55s both;
}

.feature-card::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(115deg, transparent 20%, rgba(255, 255, 255, .055) 48%, transparent 72%);
    transform: translateX(-120%);
    transition: transform .65s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    border-color: rgba(167, 139, 250, .45);
    box-shadow: 0 16px 36px rgba(0, 0, 0, .23), 0 0 24px rgba(139, 92, 246, .08);
}

.feature-card:hover::before {
    transform: translateX(120%);
}

.feature-card:nth-child(2) {
    animation-delay: .08s;
}

.feature-card:nth-child(3) {
    animation-delay: .16s;
}

.feature-icon {
    display: inline-flex;
    width: 38px;
    height: 38px;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(167, 139, 250, .2);
    border-radius: 12px;
    background: linear-gradient(145deg, rgba(139, 92, 246, .2), rgba(59, 130, 246, .1));
    color: #c4b5fd;
    font-size: 19px;
    margin-bottom: 15px;
    transition: transform .24s ease, color .24s ease;
}

.feature-card:hover .feature-icon {
    transform: rotate(-7deg) scale(1.08);
    color: #e9d5ff;
}

.feature-title {
    font-weight: 700;
    font-size: 14px;
    color: #e8eaf4;
}

.feature-desc {
    font-size: 12px;
    color: #929bad;
    line-height: 1.6;
    margin-top: 6px;
}

div[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, rgba(23, 28, 42, .94), rgba(17, 21, 32, .94));
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 16px;
    margin-bottom: 15px;
    animation: message-enter .36s ease both;
    transition: border-color .2s ease;
}

div[data-testid="stChatMessage"]:hover {
    border-color: rgba(167, 139, 250, .28);
}

div[data-testid="stChatInput"] {
    border: 1px solid rgba(151, 164, 196, .24);
    border-radius: 17px;
    background: rgba(21, 25, 38, .92);
    box-shadow: 0 12px 35px rgba(0, 0, 0, .16);
    transition: border-color .2s ease, box-shadow .2s ease;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: rgba(167, 139, 250, .72);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, .12), 0 12px 35px rgba(0, 0, 0, .2);
}

.stButton button {
    min-height: 42px;
    border-radius: 12px;
    font-weight: 600;
    transition: transform .2s ease, border-color .2s ease, background .2s ease, box-shadow .2s ease;
}

.stButton button:focus-visible {
    outline: 2px solid #c4b5fd;
    outline-offset: 3px;
}

.stButton button[kind="primary"] {
    background: linear-gradient(110deg, #6366f1, #8b5cf6 55%, #a855f7);
    border: none;
    box-shadow: 0 7px 20px rgba(99, 102, 241, .2);
}

.stButton button:hover {
    transform: translateY(-2px);
    border-color: rgba(167, 139, 250, .75);
    color: white;
    box-shadow: 0 8px 22px rgba(0, 0, 0, .2);
}

div[data-testid="stFileUploader"] {
    background: linear-gradient(145deg, rgba(21, 25, 38, .9), rgba(16, 20, 31, .9));
    border: 1px dashed rgba(151, 164, 196, .35);
    border-radius: 15px;
    padding: 10px;
    transition: border-color .2s ease, background .2s ease;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(167, 139, 250, .75);
    background: rgba(39, 34, 65, .42);
}

.document-item {
    background: linear-gradient(110deg, rgba(25, 30, 44, .9), rgba(18, 22, 33, .9));
    border: 1px solid rgba(151, 164, 196, .13);
    padding: 11px 12px;
    border-radius: 11px;
    font-size: 12px;
    margin: 8px 0;
    color: #cbd5e1;
    overflow-wrap: anywhere;
    transition: transform .2s ease, border-color .2s ease;
}

.document-item:hover {
    transform: translateX(3px);
    border-color: rgba(167, 139, 250, .38);
}

.document-item i {
    color: #c4b5fd;
    margin-right: 9px;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 13px;
    background: rgba(20, 24, 37, .78);
    transition: border-color .2s ease;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(167, 139, 250, .34);
}

.stMarkdown p {
    line-height: 1.75;
}

footer {
    display: none;
}

@keyframes page-enter {
    from { opacity: 0; transform: translateY(9px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes card-enter {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes message-enter {
    from { opacity: 0; transform: translateY(7px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes icon-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

@keyframes orbit-drift {
    from { transform: translate(0, 0) rotate(0deg); }
    to { transform: translate(-13px, 8px) rotate(8deg); }
}

@keyframes sparkle {
    0%, 100% { opacity: .7; transform: scale(.92); }
    50% { opacity: 1; transform: scale(1.08); }
}

@media (max-width: 700px) {
    .block-container {
        padding-top: 1.25rem;
    }

    .hero-panel {
        padding: 25px 22px;
        border-radius: 19px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def check_backend():
    try:
        return requests.get(
            f"{BACKEND_URL}/",
            timeout=3
        ).status_code == 200
    except requests.RequestException:
        return False


def extract_document_text(file):
    content = file.getvalue()
    extension = file.name.rsplit(".", 1)[-1].lower()

    if extension == "txt":
        return content.decode("utf-8-sig")

    if extension == "pdf":
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if extension == "docx":
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document = ET.fromstring(archive.read("word/document.xml"))

        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in document.iter(f"{namespace}p"):
            text = "".join(
                node.text or ""
                for node in paragraph.iter(f"{namespace}t")
            )
            if text:
                paragraphs.append(text)
        return "\n".join(paragraphs)

    raise ValueError(f"Unsupported document type: .{extension}")


def upload_documents(files):
    progress = st.progress(0)
    status = st.empty()

    success = 0

    for i, file in enumerate(files):
        status.info(f"Processing {file.name}")

        try:
            text = extract_document_text(file)
            chunks = split_text(text)
            if not chunks:
                raise ValueError("No readable text was found in this document.")

            response = requests.post(
                f"{BACKEND_URL}/collection",
                json={"documents": chunks},
                timeout=180
            )

            response.raise_for_status()

            if file.name not in st.session_state.documents:
                st.session_state.documents.append(file.name)

            success += 1

        except requests.RequestException as e:
            st.error(f"Upload failed: {file.name} — {e}")
        except (ValueError, PdfReadError, zipfile.BadZipFile, KeyError, ET.ParseError) as e:
            st.error(f"Could not read {file.name}: {e}")

        progress.progress((i + 1) / len(files))

    status.empty()
    progress.empty()

    if success:
        st.success(f"{success} document(s) indexed successfully.")

    if success:
        st.rerun()


def ask_question(question):
    try:
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json={"prompt": question},
            timeout=120
        )

        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return {
                "answer": "The RAG service returned an invalid response.",
                "sources": []
            }
        return {
            "answer": payload.get("response", "No answer returned."),
            "sources": []
        }

    except requests.RequestException as e:
        return {
            "answer": f"Unable to connect to the RAG service: {e}",
            "sources": []
        }


with st.sidebar:

    st.markdown("""
    <div style="display:flex;align-items:center;margin-bottom:5px">
        <div class="brand-icon"><i class="fa-solid fa-layer-group"></i></div>
        <div class="brand">RAG<span> System</span></div>
    </div>
    <div style="font-size:11px;color:#778196;letter-spacing:1.3px">
        KNOWLEDGE WORKSPACE
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">DOCUMENT MANAGEMENT</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Add knowledge sources",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if st.button(
        "Process Documents",
        type="primary",
        use_container_width=True,
        icon=":material/cloud_upload:"
    ):
        if uploaded_files:
            upload_documents(uploaded_files)
        else:
            st.warning("Select documents to continue.")

    st.markdown('<div class="sidebar-label">YOUR KNOWLEDGE BASE</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;
        color:#929bad;font-size:12px;margin-bottom:12px">
            <span>Indexed documents</span>
            <span style="color:#a5b4fc;font-weight:700">
                {len(st.session_state.documents)}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.documents:
        for document in st.session_state.documents:
            safe_document = html.escape(document)
            st.markdown(
                f'<div class="document-item"><i class="fa-regular fa-file-lines"></i>{safe_document}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div style="color:#778196;font-size:12px;padding:12px 2px">'
            'No documents indexed yet.</div>',
            unsafe_allow_html=True
        )

    st.markdown('<div class="sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)

    if st.button(
        "New Conversation",
        use_container_width=True,
        icon=":material/add:"
    ):
        st.session_state.messages = []
        st.rerun()

    if st.button(
        "Clear Chat History",
        use_container_width=True,
        icon=":material/delete_outline:"
    ):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if check_backend():
        st.markdown(
            '<div class="status"><i class="fa-solid fa-circle-check"></i> &nbsp; API Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.error("API Disconnected")

    st.markdown(
        '<div style="color:#657087;font-size:10px;margin-top:15px">'
        'NEXUS AI · POWERED BY RAG</div>',
        unsafe_allow_html=True
    )


st.markdown("""
<div class="hero-panel">
    <div class="hero-eyebrow"><i class="fa-solid fa-sparkles"></i> Your AI knowledge workspace</div>
    <div class="hero-title">Knowledge, made <span class="hero-accent">conversational.</span></div>
    <div class="hero-subtitle">
        Explore your documents, uncover the details that matter, and get clear answers grounded in your sources.
    </div>
</div>
""", unsafe_allow_html=True)


if not st.session_state.messages:

    st.markdown("""
    <div style="padding:25px 0 20px 0">
        <div style="font-size:11px;color:#c4b5fd;font-weight:700;
        letter-spacing:1.5px">YOUR AI WORKSPACE</div>
        <div style="font-size:25px;font-weight:750;color:#f1f5f9;
        margin-top:10px">What would you like to explore?</div>
        <div style="font-size:13px;color:#9aa3b8;margin-top:7px">
        Start a conversation with your uploaded knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    features = [
        ("fa-file-shield", "Document Intelligence", "Understand and analyze your documents."),
        ("fa-magnifying-glass-chart", "Semantic Retrieval", "Find relevant information intelligently."),
        ("fa-comments", "Contextual Answers", "Get answers grounded in your knowledge.")
    ]

    for col, feature in zip([c1, c2, c3], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon"><i class="fa-solid {feature[0]}"></i></div>
                <div class="feature-title">{feature[1]}</div>
                <div class="feature-desc">{feature[2]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:12px;color:#8992a5;font-weight:700;'
        'letter-spacing:1px;margin-bottom:12px">SUGGESTED PROMPTS</div>',
        unsafe_allow_html=True
    )

    prompts = [
        "Summarize my uploaded documents",
        "Explain the important concepts",
        "Generate interview questions from my documents"
    ]

    p1, p2, p3 = st.columns(3)

    for col, prompt in zip([p1, p2, p3], prompts):
        with col:
            if st.button(prompt, use_container_width=True):
                st.session_state.pending_question = prompt
                st.rerun()


for message in st.session_state.messages:

    with st.chat_message(
        message["role"],
        avatar=":material/auto_awesome:" if message["role"] == "assistant" else ":material/person:"
    ):

        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):

            with st.expander("Retrieved Sources"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")


prompt = st.chat_input("Ask a question about your knowledge base...")

if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None


if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/auto_awesome:"):

        with st.spinner("Retrieving relevant knowledge..."):

            result = ask_question(prompt)

            answer = result.get(
                "answer",
                result.get("response", "No answer returned.")
            )

            sources = result.get("sources", [])

            if isinstance(sources, str):
                sources = [sources]

            st.markdown(answer)

            if sources:
                with st.expander("Retrieved Sources"):
                    for source in sources:
                        st.markdown(f"- {source}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    st.rerun()