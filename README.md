# SoporteGit — Asistente Experto basado en RAG (Avance 2)

**Autores:** Leisson Arley Murillo Alvarez · Milen Dayana Herrera Delgado  
**Docente:** Pajaro Fuentes Leandro  
**Institución:** Fundación Universitaria Konrad Lorenz  

---

## Descripción

Sistema de IA tipo **Analista de Soporte Técnico** que responde preguntas sobre manuales de Git utilizando un pipeline RAG completo.

**Stack alineado con la práctica de clase:**
| Componente | Tecnología |
|---|---|
| Embeddings | Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) — local, CPU |
| Vector store | ChromaDB (persistente, similitud coseno) |
| LLM | Groq API (`llama-3.3-70b-versatile`) — gratuito, ultra-rápido |
| Framework | LangChain + Ragas |
| Interfaz | Streamlit |

Los documentos fuente **nunca** se envían completos a servicios externos: solo se recuperan y envían al LLM los fragmentos relevantes para cada consulta.

## Flujo RAG implementado

```
📄 Manuales Git (data/docs/)
       │
       ▼
  ✂️  PASO 1 — Carga de documentos (DirectoryLoader + TextLoader)
       │
       ▼
  🧩  PASO 2 — Chunking (RecursiveCharacterTextSplitter, size=800, overlap=150)
       │
       ▼
  🔢  PASO 3 — Embeddings locales (Sentence Transformers, 384 dims)
       │
       ▼
  🗄️  PASO 4 — ChromaDB (persistente, metadatos de fuente)
       │
       ▼
  ❓  Consulta del usuario
       │
       ▼
  🔍  PASO 5 — Recuperación (similitud coseno, top_k=4)
       │
       ▼
  📝  PASO 6 — Prompt aumentado (System + Few-Shot + <contexto>/<instruccion>)
       │
       ▼
  🤖  PASO 7 — Groq genera respuesta JSON estructurada
       │
       ▼
  📊  PASO 8 — Evaluación Ragas
```

### Justificación de parámetros

- **Chunk size=800 / overlap=150**: captura secciones completas (comando + explicación) sin diluir la señal semántica.
- **Separadores por encabezados Markdown**: preserva coherencia semántica de cada chunk.
- **Embeddings locales**: sin costo, sin API key, multilingüe, ideal para Colab/CPU.
- **ChromaDB**: ligera, metadatos ricos (`source_file`, `chunk_id`, `content_hash`) para citación.
- **top_k=4**: balance cobertura/ruido; se evaluó también k=6 en la iteración de mejora.
- **System Prompt + Few-Shot + XML**: reutilizados del Avance 1 (anti-alucinación, seguridad, JSON estricto).

## Estructura del repositorio

```
Avance2_RAG/
├── app/streamlit_app.py      # Interfaz de chat conversacional
├── data/docs/                # Corpus (5 manuales Git en Markdown)
├── eval/
│   ├── eval_dataset.json     # 18 preguntas + ground truth
│   └── run_ragas.py          # Evaluación Ragas
├── src/
│   ├── ingest.py             # Ingesta + chunking + vectorización
│   └── rag_chain.py          # Recuperación + generación (Groq)
├── chroma_db/                # Índice vectorial (generado)
├── .env.example
├── requirements.txt
└── README.md
```

## Instalación y ejecución

```bash
# 1. Clonar
git clone <url-del-repo>
cd Avance2_RAG

# 2. Entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. API Key de Groq (gratis en https://console.groq.com)
cp .env.example .env
# Editar .env y poner GROQ_API_KEY=gsk_...

# 5. Crear el índice vectorial (solo la primera vez)
python -m src.ingest

# 6. Probar la cadena RAG
python -m src.rag_chain

# 7. Evaluación Ragas
python -m eval.run_ragas --run_name baseline
python -m eval.run_ragas --top_k 6 --run_name topk6

# 8. Interfaz de chat
streamlit run app/streamlit_app.py
```

## Despliegue (Streamlit Community Cloud)

1. Sube el repo a GitHub (sin `.env`).
2. En [share.streamlit.io](https://share.streamlit.io) selecciona el repo y `app/streamlit_app.py`.
3. En **Secrets** añade:
   ```
   GROQ_API_KEY = "gsk_..."
   ```
4. La URL pública quedará: `https://segundaentregakt8falpwttzfwzkxgwkzsq.streamlit.app/`

> Si el índice Chroma no se sube, regenera con `python -m src.ingest` en un paso de build o al arranque.

## Evaluación con Ragas

Conjunto de **18 preguntas** (incluye casos fuera de alcance para medir alucinaciones).

| Métrica | Qué mide |
|---|---|
| faithfulness | Fidelidad de la respuesta al contexto |
| answer_relevancy | Relevancia de la respuesta a la pregunta |
| context_precision | Precisión de los chunks recuperados |
| context_recall | Cobertura del ground truth por los chunks |

Baseline (top_k=4): faithfulness 0.375 · answer_relevancy 0.564 · context_precision 0.347 · context_recall 0.333 (la más baja; cuello de botella en recuperación/chunking).

Iteración (top_k=6): answer_relevancy subió a 0.885 (+0.32); context_precision bajó a 0.167. Faithfulness y context_recall no fueron calculables (NaN) en ese run.

Se documenta la comparación antes/después y propuestas de mejora (priorizar .md, reducir chunk size, re-ranking) en el PDF de entrega. Resultados en eval/results/.

## URL pública

> *https://segundaentrega-kt8falpwttzfwzkxgwkzsq.streamlit.app/*

## Repositorio

https://github.com/leiss20/SegundaEntrega.git

---
*Avance 2 — Desarrollo de un Asistente Experto basado en RAG*  
*Fundación Universitaria Konrad Lorenz*
