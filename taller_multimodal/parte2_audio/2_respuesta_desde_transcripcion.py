"""
2.2 - Flujo completo: Audio (archivo) → Transcripción → Tools (Chroma) → Respuesta
"""
from pathlib import Path
import os
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from tools_git import TOOLS, TOOLS_MAP, _cargar_vectorstore

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Falta GROQ_API_KEY en el archivo .env")

CARPETA = Path(__file__).resolve().parent.parent / "audios"
audios = sorted(
    list(CARPETA.glob("*.wav"))
    + list(CARPETA.glob("*.mp3"))
    + list(CARPETA.glob("*.m4a"))
    + list(CARPETA.glob("*.ogg"))
    + list(CARPETA.glob("*.webm"))
    + list(CARPETA.glob("*.mp4"))
)

if not audios:
    raise FileNotFoundError(
        f"No hay audios en {CARPETA}\n"
        "Coloca al menos 4 grabaciones con preguntas sobre Git."
    )

client = Groq()
llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=1024)
llm_con_tools = llm.bind_tools(TOOLS)

SISTEMA = SystemMessage(content=(
    "Eres SoporteGit, asistente experto en Git. Responde en español. "
    "Usa buscar_en_manuales para consultar la base de conocimiento, "
    "explicar_comando_git para fichas de comandos, y "
    "advertir_comando_peligroso cuando haya riesgo. "
    "Después de usar una tool, redacta una respuesta final clara."
))


def responder_con_tools(pregunta: str) -> str:
    mensajes = [SISTEMA, HumanMessage(content=pregunta)]
    respuesta = llm_con_tools.invoke(mensajes)
    mensajes.append(respuesta)

    if respuesta.tool_calls:
        print(f"  🔧 Tools: {[tc['name'] for tc in respuesta.tool_calls]}")
        for tc in respuesta.tool_calls:
            tool_fn = TOOLS_MAP.get(tc["name"])
            resultado = (
                tool_fn.invoke(tc["args"])
                if tool_fn
                else f"Tool {tc['name']} no encontrada"
            )
            print(f"     → {tc['name']}({tc['args']})")
            preview = str(resultado)[:150].replace("\n", " ")
            print(f"       ↳ {preview}...")
            mensajes.append(
                ToolMessage(content=str(resultado), tool_call_id=tc["id"])
            )
        respuesta_final = llm_con_tools.invoke(mensajes)
        return respuesta_final.content

    return respuesta.content


print("=" * 60)
print("  2.2  Audio → Transcripción → Tools (Chroma) → Respuesta")
print("=" * 60)

vs = _cargar_vectorstore()
if vs is None:
    print("⚠️  Chroma no disponible → fallback local.")
    print("   Actívalo con: cd .. && python -m src.ingest\n")
else:
    print("✅ Base Chroma lista.\n")

for ruta in audios:
    print(f"\n{'═' * 60}")
    print(f"Audio: {ruta.name}")
    print("═" * 60)

    print("\n[1] Transcribiendo...")
    with open(ruta, "rb") as f:
        transcripcion = client.audio.transcriptions.create(
            file=(ruta.name, f.read()),
            model="whisper-large-v3-turbo",
            language="es",
        )
    texto = transcripcion.text.strip()
    print(f"\nTranscripción:\n  {texto}")

    print("\n[2] Respondiendo (con tools si hace falta)...")
    respuesta = responder_con_tools(texto)
    print(f"\nRespuesta:\n{respuesta}")

print("\n" + "=" * 60)
print("Proceso completo terminado.")
print("=" * 60)
