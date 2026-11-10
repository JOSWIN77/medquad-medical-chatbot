"""
app.py  –  Medical Q&A Chatbot (MedQuAD)
Run:  streamlit run app.py
"""
import streamlit as st
import time

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="MedQuAD Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global */
body { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: #f0f6ff; }

/* Hide default header */
header[data-testid="stHeader"] { background: transparent; }

/* Chat bubbles */
.chat-wrap { display: flex; margin: 8px 0; gap: 10px; align-items: flex-start; }
.chat-wrap.user  { flex-direction: row-reverse; }
.avatar { width:38px; height:38px; border-radius:50%; display:flex;
          align-items:center; justify-content:center; font-size:18px;
          flex-shrink:0; box-shadow:0 2px 6px rgba(0,0,0,.12); }
.av-bot  { background:linear-gradient(135deg,#2563eb,#7c3aed); }
.av-user { background:linear-gradient(135deg,#059669,#0d9488); }
.bubble  { max-width:72%; padding:12px 16px; border-radius:18px;
           font-size:0.92rem; line-height:1.6; box-shadow:0 2px 8px rgba(0,0,0,.08); }
.bubble.bot  { background:#fff; color:#1e293b;
               border-top-left-radius:4px; }
.bubble.user { background:linear-gradient(135deg,#2563eb,#7c3aed);
               color:#fff; border-top-right-radius:4px; }
.meta { font-size:0.72rem; color:#94a3b8; margin-top:5px; }

/* Result cards */
.result-card { background:#fff; border:1px solid #e2e8f0; border-radius:14px;
               padding:14px 18px; margin:8px 0;
               box-shadow:0 2px 6px rgba(0,0,0,.05); }
.result-card:hover { border-color:#2563eb; box-shadow:0 4px 14px rgba(37,99,235,.12); }
.card-header { display:flex; align-items:center; justify-content:space-between;
               margin-bottom:8px; }
.card-q { font-weight:600; color:#1e293b; font-size:0.88rem; }
.badge { padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.badge-high   { background:#dcfce7; color:#15803d; }
.badge-medium { background:#fef9c3; color:#854d0e; }
.badge-low    { background:#fee2e2; color:#991b1b; }
.card-a { color:#334155; font-size:0.86rem; line-height:1.6; }
.card-focus { font-size:0.78rem; color:#64748b; margin-top:6px; }

/* Sidebar */
[data-testid="stSidebar"] { background:#1e293b !important; }
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }

/* Input */
[data-testid="stChatInput"] textarea {
  border-radius:12px !important;
  border:2px solid #2563eb !important;
  font-size:0.9rem !important;
}

/* Entity pills */
.entity-pill { display:inline-block; padding:2px 8px; border-radius:12px;
               font-size:0.75rem; font-weight:600; margin:2px; }

/* Stat cards */
.stat-box { background:rgba(255,255,255,.1); border-radius:10px; padding:10px 14px;
            text-align:center; margin:4px 0; }
.stat-num  { font-size:1.4rem; font-weight:700; color:#93c5fd; }
.stat-lbl  { font-size:0.72rem; color:#94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── Lazy imports (heavy) ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_engine():
    from data_loader import download_medquad
    from retrieval import MedRetriever

    progress = st.empty()
    def cb(msg):
        progress.info(f"⏳ {msg}")

    pairs = download_medquad(max_per_folder=25, status_callback=cb)
    progress.empty()
    engine = MedRetriever(pairs)
    return engine, pairs

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "entities_found" not in st.session_state:
    st.session_state.entities_found = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 MedQuAD Chatbot")
    st.markdown("*Powered by NIH MedQuAD Dataset*")
    st.markdown("---")

    st.markdown("### 📊 Session Stats")
    st.markdown(f"""
    <div class="stat-box"><div class="stat-num">{st.session_state.total_queries}</div>
    <div class="stat-lbl">Queries</div></div>
    <div class="stat-box"><div class="stat-num">{st.session_state.entities_found}</div>
    <div class="stat-lbl">Entities Detected</div></div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔬 Entity Legend")
    entity_info = {
        "🤒 SYMPTOM":    "#ff6b6b",
        "🦠 DISEASE":    "#a855f7",
        "💊 TREATMENT":  "#22c55e",
        "🫀 BODY PART":  "#3b82f6",
        "💉 DRUG":       "#f59e0b",
    }
    for label, color in entity_info.items():
        st.markdown(
            f'<span class="entity-pill" style="background:{color}22;'
            f'border:1px solid {color};color:{color}">{label}</span>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    samples = [
        "What are the symptoms of diabetes?",
        "How is cancer treated?",
        "What causes hypertension?",
        "What is Alzheimer's disease?",
        "What are treatments for asthma?",
        "What are the side effects of aspirin?",
    ]
    for s in samples:
        if st.button(s, key=f"sample_{s}", use_container_width=True):
            st.session_state["prefill"] = s
            st.rerun()

    st.markdown("---")
    top_k = st.slider("Results to show", 1, 5, 3)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_queries = 0
        st.session_state.entities_found = 0
        st.rerun()

    st.markdown("---")
    st.caption("⚠️ For informational use only. Not a substitute for professional medical advice.")

# ── Main header ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🏥 Medical Q&A Assistant")
    st.caption("Ask any medical question — powered by NIH MedQuAD dataset with real-time entity recognition")

# ── Load engine ───────────────────────────────────────────────────────────────
with st.spinner("🔄 Loading MedQuAD knowledge base… (first run downloads data)"):
    try:
        engine, pairs = load_engine()
        st.success(f"✅ Knowledge base ready — **{len(pairs):,}** Q&A pairs indexed", icon="🗄️")
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        st.stop()

from ner import extract_entities, highlight_entities, entity_color

# ── Chat history ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:40px;color:#94a3b8">
          <div style="font-size:3rem">🩺</div>
          <h3 style="color:#64748b">Welcome to MedQuAD Chatbot</h3>
          <p>Ask any medical question. Try the samples in the sidebar!</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = msg["role"]
        av_cls = "av-bot" if role == "bot" else "av-user"
        emoji  = "🤖" if role == "bot" else "👤"
        b_cls  = "bot" if role == "bot" else "user"
        wrap   = "user" if role == "user" else ""

        st.markdown(f"""
        <div class="chat-wrap {wrap}">
          <div class="avatar {av_cls}">{emoji}</div>
          <div class="bubble {b_cls}">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Show result cards for bot answers
        if role == "bot" and "results" in msg:
            for i, r in enumerate(msg["results"]):
                badge_cls = f"badge-{r['confidence'].lower()}"
                focus_tag = f"<div class='card-focus'>🎯 Focus: <b>{r['focus']}</b> &nbsp;|&nbsp; Type: {r.get('type','—')}</div>" if r.get("focus") else ""
                score_pct = int(r["score"] * 100)
                with st.expander(f"📋 Result {i+1} — Confidence: {r['confidence']} ({score_pct}%)", expanded=(i == 0)):
                    st.markdown(f"""
                    <div class="result-card">
                      <div class="card-header">
                        <div class="card-q">❓ {r['question']}</div>
                        <span class="badge {badge_cls}">{r['confidence']}</span>
                      </div>
                      <div class="card-a">{r['answer'][:800]}{'…' if len(r['answer'])>800 else ''}</div>
                      {focus_tag}
                    </div>
                    """, unsafe_allow_html=True)

        if role == "user" and "entities" in msg and msg["entities"]:
            pills = " ".join(
                f'<span class="entity-pill" style="background:{entity_color(e["label"])}22;'
                f'border:1px solid {entity_color(e["label"])};color:{entity_color(e["label"])}">'
                f'{e["text"].title()} · {e["label"]}</span>'
                for e in msg["entities"]
            )
            st.markdown(f"<div style='margin-left:52px;margin-top:-4px'>{pills}</div>", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
query = st.chat_input("Ask a medical question… e.g. 'What are the symptoms of diabetes?'")

# Allow sidebar sample buttons to inject a query
if prefill and not query:
    query = prefill

if query:
    # Extract entities from user query
    entities = extract_entities(query)
    st.session_state.entities_found += len(entities)
    st.session_state.total_queries += 1

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "entities": entities,
    })

    # Retrieve answers
    with st.spinner("🔍 Searching knowledge base…"):
        results = engine.search(query, top_k=top_k)
        time.sleep(0.3)  # UX polish

    if results:
        top = results[0]
        reply = (
            f"I found **{len(results)} relevant result(s)** for your query.<br><br>"
            f"**Best match** (Confidence: {top['confidence']}):<br>"
            f"{top['answer'][:400]}{'…' if len(top['answer']) > 400 else ''}"
        )
    else:
        reply = (
            "I couldn't find a close match in the MedQuAD dataset for that question. "
            "Please try rephrasing, or ask about a specific disease, symptom, or treatment."
        )

    st.session_state.messages.append({
        "role": "bot",
        "content": reply,
        "results": results,
    })
    st.rerun()
