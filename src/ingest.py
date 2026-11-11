"""
Pipeline de ingesta, chunking, vectorización y creación del índice vectorial.
Estilo práctica de clase: Sentence Transformers (local, CPU) + ChromaDB.
 
Ejecutar una sola vez (o cuando se actualice el corpus):
    python -m src.ingest
"""
 
import os
import hashlib
import shutil
from pathlib import Path
 
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
 
# ---------------------------------------------------------------------------
# Configuración de parámetros (justificados en el PDF / README)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "data" / "docs"
PERSIST_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "git_manuals"
 
# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
SEPARATORS = ["\n## ", "\n### ", "\n\n", "\n", " ", ""]
 
# Embeddings locales (igual que la práctica de clase)
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 384 dims, multilingüe, CPU
 
 
def load_documents():

    """Carga .md, .txt y .pdf del directorio de documentos (compatible Windows)."""

    docs = []

    if not DOCS_DIR.exists():

        raise SystemExit(f"No existe la carpeta: {DOCS_DIR}")
 
    # Buscar todos los tipos de archivo

    archivos_md  = list(DOCS_DIR.glob("**/*.md"))

    archivos_txt = list(DOCS_DIR.glob("**/*.txt"))

    archivos_pdf = list(DOCS_DIR.glob("**/*.pdf"))

    archivos = archivos_md + archivos_txt + archivos_pdf
 
    print(f"[ingest] Carpeta: {DOCS_DIR}")

    print(f"[ingest] Archivos encontrados: {len(archivos)}")

    for f in archivos:

        print(f"  - {f.name}")
 
    for path in archivos:

        try:

            if path.suffix.lower() == ".pdf":

                loader = PyPDFLoader(str(path))

            else:

                loader = TextLoader(str(path), encoding="utf-8")

            docs.extend(loader.load())

        except Exception as e:

            print(f"  [!] Error cargando {path.name}: {e}")
 
    print(f"[ingest] Cargados {len(docs)} documentos/páginas")

    return docs
 
 
 
def chunk_documents(docs):
    """Fragmenta los documentos con la estrategia elegida."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(docs)
 
    for i, chunk in enumerate(chunks):
        source = Path(chunk.metadata.get("source", "unknown")).name
        chunk.metadata["source_file"] = source
        chunk.metadata["chunk_id"] = i
        chunk.metadata["content_hash"] = hashlib.md5(
            chunk.page_content.encode()
        ).hexdigest()[:8]
 
    print(f"[ingest] Generados {len(chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks
 
 
def get_embeddings():
    """Carga el modelo de embeddings local (Sentence Transformers)."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
 
 
def build_vectorstore(chunks, embeddings):
    """Crea (o recrea) el índice Chroma persistente."""
    if PERSIST_DIR.exists():
        shutil.rmtree(PERSIST_DIR)
        print(f"[ingest] Índice anterior eliminado: {PERSIST_DIR}")
 
    print(f"[ingest] Indexando {len(chunks)} fragmentos en ChromaDB...")
    print(f"         (Embeddings locales: {EMBEDDING_MODEL})")
 
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )
    total = vectorstore._collection.count()
    print(f"[ingest] Índice Chroma creado en {PERSIST_DIR}")
    print(f"         Fragmentos indexados: {total}")
    print(f"         Dimensión de vectores: 384")
    return vectorstore
 
 
def main():
    docs = load_documents()
    if not docs:
        raise SystemExit(
            f"No se encontraron documentos en {DOCS_DIR}\n"
            "Asegúrate de que haya archivos .md o .txt dentro de data/docs/"
        )
    chunks = chunk_documents(docs)
    embeddings = get_embeddings()
    build_vectorstore(chunks, embeddings)
    print("[ingest] Proceso completado con éxito.")
 
 
if __name__ == "__main__":
    main()