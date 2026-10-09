"""
Interfaz de chat conversacional para el Asistente de Soporte Git (RAG).
Stack: Groq + Sentence Transformers + Chroma (estilo práctica de clase).

Ejecución local:
    streamlit run app/streamlit_app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from src.rag_chain import query, parse_json_safe, TOP_K

st.set_page_config(
    page_title="SoporteGit — Asistente RAG",
    page_icon="🔧",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🔧 SoporteGit")
st.caption(
    "Asistente experto de soporte técnico basado en RAG · Manuales de Git  \n"
    "Embeddings locales (Sentence Transformers) · LLM Groq · ChromaDB"
)

with st.sidebar:
    st.header("Acerca de")
    st.markdown(
        """
        Este asistente responde **únicamente** con base en los manuales de Git
        indexados. Si la información no está en la base de conocimiento,
        lo indica explícitamente (control de alucinaciones).

        **Stack (práctica de clase):**
        - Embeddings: `paraphrase-multilingual-MiniLM-L12-v2` (local, CPU)
        - Vector store: ChromaDB
        - LLM: Groq (llama-3.3-70b-versatile)
        - Framework: LangChain + Ragas
        """
    )
    st.divider()
    top_k = st.slider("Chunks a recuperar (top_k)", min_value=2, max_value=8, value=TOP_K)
    show_raw = st.checkbox("Mostrar JSON crudo", value=False)
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            data = msg.get("parsed")
            if data:
                if data.get("diagnostico", "").startswith("No encuentro"):
                    st.warning(data["diagnostico"])
                else:
                    st.markdown(f"**Diagnóstico:** {data.get('diagnostico', '')}")
                    if data.get("pasos_solucion"):
                        st.markdown("**Pasos de solución:**")
                        for i, p in enumerate(data["pasos_solucion"], 1):
                            st.markdown(f"{i}. {p}")
                    if data.get("comandos"):
                        st.markdown("**Comandos:**")
                        for c in data["comandos"]:
                            st.code(c, language="bash")
                    if data.get("advertencias"):
                        for a in data["advertencias"]:
                            st.error(f"⚠️ {a}")
                    if data.get("fuente_contexto") and data["fuente_contexto"] != "N/A":
                        st.info(f"📄 Fuente: `{data['fuente_contexto']}`")
            else:
                st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Ver fragmentos recuperados"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**Fragmento {i}** — `{src['source']}`")
                        st.text(
                            src["content"][:400]
                            + ("..." if len(src["content"]) > 400 else "")
                        )
        else:
            st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta sobre Git..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la base de conocimiento..."):
            try:
                history_context = ""
                if len(st.session_state.messages) > 1:
                    recent = st.session_state.messages[-4:]
                    history_lines = []
                    for m in recent:
                        role = "Usuario" if m["role"] == "user" else "Asistente"
                        history_lines.append(f"{role}: {m.get('content', '')[:200]}")
                    history_context = (
                        "Historial reciente:\n" + "\n".join(history_lines) + "\n\n"
                    )

                full_question = history_context + prompt
                raw, docs = query(full_question, top_k=top_k)
                parsed = parse_json_safe(raw)

                if parsed.get("diagnostico", "").startswith("No encuentro"):
                    st.warning(parsed["diagnostico"])
                else:
                    st.markdown(f"**Diagnóstico:** {parsed.get('diagnostico', '')}")
                    if parsed.get("pasos_solucion"):
                        st.markdown("**Pasos de solución:**")
                        for i, p in enumerate(parsed["pasos_solucion"], 1):
                            st.markdown(f"{i}. {p}")
                    if parsed.get("comandos"):
                        st.markdown("**Comandos:**")
                        for c in parsed["comandos"]:
                            st.code(c, language="bash")
                    if parsed.get("advertencias"):
                        for a in parsed["advertencias"]:
                            st.error(f"⚠️ {a}")
                    if parsed.get("fuente_contexto") and parsed["fuente_contexto"] != "N/A":
                        st.info(f"📄 Fuente: `{parsed['fuente_contexto']}`")

                sources = [
                    {
                        "source": d.metadata.get("source_file", "desconocido"),
                        "content": d.page_content,
                    }
                    for d in docs
                ]
                with st.expander("Ver fragmentos recuperados"):
                    for i, src in enumerate(sources, 1):
                        st.markdown(f"**Fragmento {i}** — `{src['source']}`")
                        st.text(
                            src["content"][:400]
                            + ("..." if len(src["content"]) > 400 else "")
                        )

                if show_raw:
                    st.code(raw, language="json")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": raw,
                    "parsed": parsed,
                    "sources": sources,
                })
            except Exception as e:
                st.error(f"Error al procesar la consulta: {e}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {e}",
                    "parsed": None,
                    "sources": [],
                })
