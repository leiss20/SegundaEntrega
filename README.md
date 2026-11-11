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

# Taller Multimodal y Audio — SoporteGit

**Dominio:** Asistente de soporte técnico sobre Git (manuales, comandos, ramas, conflictos, rebase, tags).

**Autores del proyecto base:** Leisson Arley Murillo Alvarez · Milen Dayana Herrera Delgado  
**Asignatura:** Desarrollo de Aplicaciones con IA — Fundación Universitaria Konrad Lorenz

---

## Requisitos

- Python 3.10+
- Cuenta gratuita en [Groq](https://console.groq.com) → API Key
- Micrófono (para el asistente de voz en vivo)
- Imágenes del dominio (capturas de terminal Git, conflictos, ramas, etc.)
- Audios cortos (10-30 s) con preguntas sobre Git

## Instalación rápida

```bash
cd taller_multimodal

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edita .env y pon: GROQ_API_KEY=gsk_...
```

## Estructura

```
taller_multimodal/
├── README.md
├── .env.example
├── requirements.txt
├── imagenes/                  ← capturas (.png / .jpg)
├── audios/                    ← grabaciones (.wav / .mp3)
├── parte1_vision/
│   ├── 1_pregunta_imagen.py
│   ├── 2_extraccion_estructurada.py
│   ├── 3_varias_imagenes.py
│   └── 4_error_provocado.py
└── parte2_audio/
    ├── 1_transcripcion.py
    ├── 2_respuesta_desde_transcripcion.py   ← con TOOLS
    └── asistente_voz.py                     ← MICRÓFONO EN VIVO + TOOLS
```

## Cómo ejecutar

### Parte 1 – Visión (qwen/qwen3.8-27b)

```bash
python parte1_vision/1_pregunta_imagen.py
python parte1_vision/2_extraccion_estructurada.py
python parte1_vision/3_varias_imagenes.py
python parte1_vision/4_error_provocado.py
```

### Parte 2 – Audio + Tools

```bash
# Transcripción de archivos
python parte2_audio/1_transcripcion.py

# Archivo → transcripción → tools → respuesta
python parte2_audio/2_respuesta_desde_transcripcion.py

# ★ ASISTENTE EN VIVO (micrófono)
python parte2_audio/asistente_voz.py
```

### Cómo funciona el asistente de voz

1. Presionas Enter
2. Hablas 12 segundos (el micrófono graba)
3. Whisper transcribe tu pregunta
4. El LLM decide si necesita **tools**:
   - `explicar_comando_git` — ficha de un comando
   - `buscar_concepto_git` — conflictos, merge vs rebase, etc.
   - `advertir_comando_peligroso` — reset --hard, push --force...
5. Ejecuta las tools y te responde

## Tools incluidas

| Tool | Para qué sirve |
|------|----------------|
| `explicar_comando_git` | Explica status, commit, merge, rebase, cherry-pick, etc. |
| `buscar_concepto_git` | Conflictos, merge vs rebase, deshacer commit, push rechazado |
| `advertir_comando_peligroso` | Avisa de comandos destructivos |

## Imágenes utilizadas (`imagenes/`)

1. `Captura de pantalla 2026-11-10 165336.png` — Guía rápida de configuración, staging y commits en Git.
2. `Captura de pantalla 2026-11-10 171849.png` — Terminal en rama `newbranch` ejecutando `git status` y `git add *`.
3. `Git.png` — Tabla *Git Cheat Sheet* con comandos básicos y gestión de ramas.
4. `Imagen.jpg` — Documento de referencia *"Más de 100 comandos para GitHub / Git que deberías conocer"*.
5. `iniciarGit.jpg` — Terminal con inicialización de repositorio, commit inicial y `git push -u origin main`.

## Audios utilizados (`audios/`)

| Archivo | Hablante | Condición | Duración | Tema de la consulta |
| :--- | :--- | :--- | :---: | :--- |
| `Audio 1.mp4` | Integrante 1 | Con ruido de fondo | 17 s | Corregir mensaje del último commit (`--amend`) y riesgo de `reset --hard`. |
| `Audio 2.mp4` | Integrante 1 | Con ruido de fondo | 15 s | Subir un proyecto local a un repositorio en GitHub paso a paso. |
| `Audio 3.mp4` | Integrante 1 | Con ruido de fondo | 25 s | Historia lineal antes de Pull Request (`merge` vs `rebase`) y riesgos en ramas compartidas. |
| `Audio 4.mp4` | Integrante 2 | Sin ruido de fondo | 18 s | Crear una nueva rama en Git y cambiar a ella sin afectar `main`. |
| `Audio 5.mp4` | Integrante 2 | Con ruido de fondo | 11 s | Funcionamiento de `git cherry-pick` y resolución de conflictos. |

*(Nota: En `2_respuesta_desde_transcripcion.py`, los archivos `Audio 4.mp4` y `Audio 5.mp4` evalúan `cherry-pick` y creación de rama respectivamente).*

