"""
Tools de SoporteGit.
La tool buscar_en_manuales consulta la base Chroma del proyecto SegundaEntrega.
Si no encuentra el índice, usa un fallback local para que el taller siga funcionando.
"""
from pathlib import Path
import os
from langchain_core.tools import tool


# ---------------------------------------------------------------------------
ROOT_PROYECTO = Path(__file__).resolve().parent.parent.parent  # SegundaEntrega/
CHROMA_DIR = ROOT_PROYECTO / "chroma_db"
COLLECTION_NAME = "git_manuals"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 4

_vectorstore = None  # cache


def _cargar_vectorstore():
    """Carga Chroma + embeddings una sola vez. Devuelve None si no está disponible."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    if not CHROMA_DIR.exists():
        print(f"[tools] No se encontró chroma_db en {CHROMA_DIR}")
        return None

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        vs = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )
        n = vs._collection.count()
        if n == 0:
            print("[tools] El índice Chroma existe pero está vacío.")
            return None

        print(f"[tools] Chroma cargado: {n} fragmentos en '{COLLECTION_NAME}'")
        _vectorstore = vs
        return _vectorstore
    except Exception as e:
        print(f"[tools] No se pudo cargar Chroma: {type(e).__name__}: {e}")
        return None


# ---------------------------------------------------------------------------
# Fallback local (si no hay Chroma)
# ---------------------------------------------------------------------------
_FALLBACK = {
    "conflicto": (
        "Conflictos de merge/rebase:\n"
        "1. Git marca los archivos en conflicto.\n"
        "2. Abre el archivo y busca <<<<<<< ======= >>>>>>>.\n"
        "3. Edita dejando el código correcto y borra los marcadores.\n"
        "4. git add <archivo>\n"
        "5. merge → git commit | rebase → git rebase --continue"
    ),
    "merge vs rebase": (
        "merge: une historias con un commit de merge (historial no lineal).\n"
        "rebase: reescribe commits encima de otra rama (historial lineal).\n"
        "Regla: no hagas rebase de commits ya publicados en un remoto compartido."
    ),
    "deshacer": (
        "Si el commit AÚN NO se subió:\n"
        "  git reset --soft HEAD~1  → mantiene cambios en staging\n"
        "  git reset HEAD~1        → mantiene cambios en working tree\n"
        "  git reset --hard HEAD~1 → BORRA los cambios (irreversible)\n"
        "Si YA se subió: git revert <hash>"
    ),
    "push rechazado": (
        "El remoto tiene commits que tú no tienes.\n"
        "Solución: git pull --rebase origin <rama> → resolver conflictos → git push"
    ),
    "rama": (
        "Crear y cambiar de rama:\n"
        "  git switch -c feature/nueva\n"
        "  git switch main\n"
        "Listar: git branch -a"
    ),
}


def _fallback_buscar(consulta: str) -> str:
    q = consulta.lower()
    for clave, texto in _FALLBACK.items():
        if clave in q:
            return f"[Fallback local]\n{texto}"
    return (
        "[Fallback local] No encontré información específica. "
        "Prueba con: conflicto, merge vs rebase, deshacer commit, push rechazado, rama.\n"
        "Para usar la base completa, ejecuta primero: python -m src.ingest  (desde SegundaEntrega)"
    )


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------

@tool
def buscar_en_manuales(consulta: str) -> str:
    """Busca en los manuales de Git indexados (ChromaDB) fragmentos relevantes para la consulta.
    Úsala siempre que el usuario pregunte sobre conceptos, flujos, conflictos o comandos de Git.

    Args:
        consulta: pregunta o tema a buscar (ej: 'cómo resolver un conflicto de merge').
    """
    vs = _cargar_vectorstore()
    if vs is None:
        return _fallback_buscar(consulta)

    try:
        docs = vs.similarity_search(consulta, k=TOP_K)
        if not docs:
            return "No se encontraron fragmentos relevantes en los manuales."

        partes = []
        for i, d in enumerate(docs, 1):
            fuente = d.metadata.get("source_file") or d.metadata.get("source", "desconocido")
            partes.append(f"[{i}] Fuente: {fuente}\n{d.page_content.strip()}")
        return "\n\n---\n\n".join(partes)
    except Exception as e:
        return f"Error al buscar en Chroma: {e}\n\n{_fallback_buscar(consulta)}"


@tool
def explicar_comando_git(comando: str) -> str:
    """Explica qué hace un comando de Git, su sintaxis básica y un ejemplo de uso.
    Úsala cuando el usuario pregunte por un comando concreto.

    Args:
        comando: nombre del comando sin la palabra 'git' (ej: 'status', 'rebase', 'cherry-pick').
    """
    catalogo = {
        "status": "git status — Estado del working directory y staging area.\nSintaxis: git status [-s]",
        "add": "git add — Añade cambios al staging area.\nSintaxis: git add <archivo> | git add .",
        "commit": "git commit — Crea un commit.\nSintaxis: git commit -m \"mensaje\"",
        "branch": "git branch — Lista, crea o elimina ramas.\nSintaxis: git branch | git branch <nombre>",
        "checkout": "git checkout — Cambia de rama o restaura archivos.\nPrefiere: git switch / git restore",
        "switch": "git switch — Cambia de rama.\nSintaxis: git switch <rama> | git switch -c <nueva>",
        "merge": "git merge — Integra cambios de otra rama.\nSintaxis: git merge <rama>",
        "rebase": "git rebase — Reaplica commits encima de otra rama (historial lineal).\nADVERTENCIA: no rebase de commits ya publicados.",
        "pull": "git pull — Trae e integra cambios del remoto.\nSintaxis: git pull --rebase origin <rama>",
        "push": "git push — Sube commits al remoto.\nSintaxis: git push origin <rama>",
        "log": "git log — Historial de commits.\nSintaxis: git log --oneline --graph --all",
        "reset": "git reset — Deshace commits o saca del staging.\nADVERTENCIA: --hard es irreversible.",
        "cherry-pick": "git cherry-pick — Aplica un commit concreto de otra rama.\nSintaxis: git cherry-pick <hash>",
        "stash": "git stash — Guarda temporalmente cambios no confirmados.\nSintaxis: git stash | git stash pop",
        "tag": "git tag — Crea o lista etiquetas.\nSintaxis: git tag v1.0.0",
        "clone": "git clone — Copia un repositorio remoto.\nSintaxis: git clone <url>",
        "init": "git init — Inicializa un repositorio nuevo.\nSintaxis: git init",
        "diff": "git diff — Diferencias entre working tree, staging y commits.\nSintaxis: git diff | git diff --staged",
        "remote": "git remote — Gestiona remotos.\nSintaxis: git remote -v | git remote add origin <url>",
    }
    clave = comando.strip().lower().replace("git ", "").split()[0]
    if clave in catalogo:
        return catalogo[clave]
    # Si no está en el catálogo corto, intenta buscar en los manuales
    return buscar_en_manuales.invoke(f"comando git {comando}")


@tool
def advertir_comando_peligroso(comando: str) -> str:
    """Devuelve advertencias de seguridad sobre comandos destructivos de Git.
    Úsala siempre que el usuario mencione reset --hard, push --force, clean -fd, etc.

    Args:
        comando: el comando completo o parcial que el usuario quiere ejecutar.
    """
    peligrosos = {
        "reset --hard": "IRREVERSIBLE. Borra todos los cambios no confirmados del working tree y del staging.",
        "push --force": "Puede sobrescribir el historial remoto y afectar a otros colaboradores. Usa --force-with-lease si es necesario.",
        "push -f": "Igual que push --force. Riesgo de reescribir historial remoto.",
        "clean -fd": "Elimina archivos y carpetas no rastreados de forma permanente.",
        "branch -D": "Elimina una rama aunque no esté fusionada (pérdida de commits).",
        "filter-branch": "Reescribe todo el historial. Operación avanzada y peligrosa.",
    }
    cmd = comando.lower()
    avisos = [f"⚠️ {v}" for k, v in peligrosos.items() if k in cmd]
    if avisos:
        return "\n".join(avisos)
    return "No se detectó un comando especialmente destructivo en la consulta."


# Lista lista para bind_tools
TOOLS = [buscar_en_manuales, explicar_comando_git, advertir_comando_peligroso]
TOOLS_MAP = {t.name: t for t in TOOLS}
