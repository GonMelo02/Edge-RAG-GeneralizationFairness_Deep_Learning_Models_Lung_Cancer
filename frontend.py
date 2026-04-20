import streamlit as st
import requests
import os
API_URL = os.getenv("API_URL", "http://localhost:8000")
# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Edge RAG",
    layout="centered",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #0a0e1a;
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(0, 212, 170, 0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(0, 120, 255, 0.06) 0%, transparent 50%);
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Main container width ── */
.block-container {
    max-width: 820px;
    padding-top: 2rem;
    padding-bottom: 6rem;
}

/* ── Header area ── */
.rag-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(0, 212, 170, 0.15);
    margin-bottom: 2rem;
}
.rag-header h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem;
    font-weight: 600;
    color: #7ab0a8;
    letter-spacing: -0.02em;
    margin: 0 0 0.3rem 0;
}
.rag-header .subtitle {
    font-size: 0.82rem;
    color: #4a7c6f;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.status-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00d4aa;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 0.75rem;
    border: 1px solid transparent;
    padding: 0.1rem 0.5rem;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(0, 120, 255, 0.07);
    border-color: rgba(0, 120, 255, 0.15);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(0, 212, 170, 0.05);
    border-color: rgba(0, 212, 170, 0.12);
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #c8ddd8 !important;
    line-height: 1.7 !important;
}

/* ── Bottom bar ── */
[data-testid="stBottom"] {
    background: #0a0e1a !important;
    border-top: 1px solid rgba(0, 212, 170, 0.10) !important;
    padding: 1rem 0 !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: #0f1525 !important;
    border: 1px solid rgba(0, 212, 170, 0.25) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0, 212, 170, 0.55) !important;
    box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.08) !important;
}
[data-testid="stChatInput"] textarea {
    color: #0a0e1a !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #3a6058 !important;
}

/* ── Sources expander ── */
[data-testid="stExpander"] {
    background: rgba(15, 21, 37, 0.6) !important;
    border: 1px solid rgba(0, 212, 170, 0.12) !important;
    border-radius: 10px !important;
    margin-top: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    color: #00d4aa !important;
    font-size: 0.82rem !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stExpander"] summary:hover {
    color: #33e0bb !important;
}

/* ── Source card ── */
.source-card {
    background: rgba(0, 212, 170, 0.03);
    border: 1px solid rgba(0, 212, 170, 0.12);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.source-card:last-child {
    margin-bottom: 0;
}
.source-filename {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 600;
    color: #00d4aa;
    margin-bottom: 0.4rem;
}
.source-filename::before {
    content: "Document";
    font-size: 0.9rem;
}
.source-excerpt {
    font-size: 0.78rem;
    color: #5a8a80;
    line-height: 1.55;
    border-left: 2px solid rgba(0, 212, 170, 0.2);
    padding-left: 0.75rem;
    margin: 0;
    font-style: italic;
}

/* ── Error boxes ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* ── Spinner text ── */
[data-testid="stSpinner"] p {
    color: #4a7c6f !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #2a4a42;
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}
.empty-state p {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ─── Helper — render source cards ───────────────────────────────────────────────
def render_sources(source_docs: list):
    if not source_docs:
        return

    seen = {}
    for doc in source_docs:
        if isinstance(doc, dict):
            filename = doc.get("metadata", {}).get("source", "Unknown")
            page     = doc.get("metadata", {}).get("page", "N/A")
            excerpt  = doc.get("page_content", "")
        else:
            filename = "Source"
            page     = "N/A"
            excerpt  = str(doc)

        key = f"{filename}_p{page}"
        if key not in seen:
            seen[key] = {"filename": filename, "page": page, "excerpt": excerpt}

    label = f"Sources ({len(seen)} chunk{'s' if len(seen) > 1 else ''})"
    with st.expander(label):
        for item in seen.values():
            display_name = item["filename"].split("/")[-1].split("\\")[-1]
            preview = item["excerpt"].strip()[:200].replace("\n", " ")
            if len(item["excerpt"]) > 200:
                preview += "…"

            st.markdown(f"""
            <div class="source-card">
                <div class="source-filename">{display_name} &nbsp;·&nbsp; p.{item["page"]}</div>
                <p class="source-excerpt">{preview}</p>
            </div>
            """, unsafe_allow_html=True)


# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
    <h1> Private Bioinformatics RAG</h1>
    <div class="subtitle">
        <span class="status-dot"></span>
        Running locally &nbsp;·&nbsp; Docker &nbsp;·&nbsp; Phi-3
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Session state ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Render chat history ─────────────────────────────────────────────────────────
if not st.session_state.messages:
    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        st.image("static/luna_malignant.png", use_container_width=True)
        st.markdown("""
        <div style="text-align:center; font-family:'JetBrains Mono',monospace; 
                    font-size:0.7rem; color:#2a4a42; margin-top:0.4rem; 
                    letter-spacing:0.04em;">
            Illustrative malignant nodule from LUNA25 dataset
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div class="empty-state">
        <p>Ask anything about your documents.<br>Your data never leaves this machine.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                render_sources(msg["sources"])

# ─── Chat input ──────────────────────────────────────────────────────────────────
question = st.chat_input("Ask a question about your documents…")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Querying the model…"):
            try:
                response = requests.post(
                f"{API_URL}/perguntar",
                json={"query": question},
                timeout=500,
            )

                if response.status_code == 200:
                    data = response.json()

                    # Suporta formato novo e antigo
                    resposta_llm = data.get("result") or data.get("resposta", "No answer generated.")
                    source_docs  = data.get("source_documents") or data.get("fontes", [])

                    st.markdown(resposta_llm)
                    render_sources(source_docs)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": resposta_llm,
                        "sources": source_docs,
                    })

                else:
                    error_msg = f"API returned status **{response.status_code}**."
                    st.error(f" {error_msg}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f" {error_msg}",
                        "sources": [],
                    })

            except requests.exceptions.ConnectionError:
                msg = " Cannot reach the API. Is Docker running on port **8000**?"
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": msg, "sources": []
                })

            except requests.exceptions.Timeout:
                msg = "Request timed out. The model may still be loading."
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant", "content": msg, "sources": []
                })