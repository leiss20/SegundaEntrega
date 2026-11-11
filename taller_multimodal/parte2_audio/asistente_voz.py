"""
Asistente de voz en vivo — SoporteGit
=====================================
1. Escucha por el micrófono
2. Transcribe con Whisper (Groq)
3. El LLM decide si usar tools (búsqueda en Chroma, explicar comando, etc.)
4. Ejecuta las tools y responde

Requisitos:
    pip install -r requirements.txt
    # Y tener el índice Chroma generado:
    #   cd .. && python -m src.ingest
"""
from pathlib import Path
import os
import io
import time
from dotenv import load_dotenv

import sounddevice as sd
from scipy.io.wavfile import write
from tqdm import tqdm

from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from tools_git import TOOLS, TOOLS_MAP

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Falta GROQ_API_KEY en el archivo .env")

DURACION_SEGUNDOS = 12
SAMPLE_RATE = 16000
CANALES = 1

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=1024,
)
llm_con_tools = llm.bind_tools(TOOLS)

SISTEMA = SystemMessage(content=(
    "Eres SoporteGit, un asistente de soporte técnico experto en Git. "
    "Responde siempre en español, de forma clara y profesional.\n"
    "Tienes tools disponibles:\n"
    "- buscar_en_manuales: busca en la base de conocimiento (manuales de Git indexados).\n"
    "- explicar_comando_git: ficha rápida de un comando.\n"
    "- advertir_comando_peligroso: avisos de seguridad.\n"
    "Usa buscar_en_manuales siempre que la pregunta sea sobre conceptos, flujos o problemas de Git.\n"
    "Si es un saludo o no requiere tool, responde directamente.\n"
    "Después de recibir el resultado de una tool, redacta una respuesta final útil "
    "(no devuelvas solo el texto crudo de la tool)."
))


def grabar_audio(segundos: int = DURACION_SEGUNDOS) -> bytes:
    print(f"\n🎤 Grabando {segundos} s... (habla ahora)")
    audio = sd.rec(
        int(segundos * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CANALES,
        dtype="int16",
    )
    for _ in tqdm(range(segundos * 10), desc="Grabando", ncols=60):
        time.sleep(0.1)
    sd.wait()
    print("✅ Grabación terminada.")

    buf = io.BytesIO()
    write(buf, SAMPLE_RATE, audio)
    return buf.getvalue()


def transcribir(wav_bytes: bytes) -> str:
    client = Groq()
    result = client.audio.transcriptions.create(
        file=("grabacion.wav", wav_bytes),
        model="whisper-large-v3-turbo",
        language="es",
    )
    return result.text.strip()


def responder_con_tools(pregunta: str) -> str:
    mensajes = [SISTEMA, HumanMessage(content=pregunta)]

    respuesta = llm_con_tools.invoke(mensajes)
    mensajes.append(respuesta)

    if respuesta.tool_calls:
        print(f"\n🔧 Tools solicitadas: {[tc['name'] for tc in respuesta.tool_calls]}")
        for tc in respuesta.tool_calls:
            nombre = tc["name"]
            args = tc["args"]
            print(f"   → {nombre}({args})")
            tool_fn = TOOLS_MAP.get(nombre)
            if tool_fn is None:
                resultado = f"Tool '{nombre}' no encontrada."
            else:
                resultado = tool_fn.invoke(args)
            preview = str(resultado)[:200].replace("\n", " ")
            print(f"     ↳ {preview}...")
            mensajes.append(
                ToolMessage(content=str(resultado), tool_call_id=tc["id"])
            )

        respuesta_final = llm_con_tools.invoke(mensajes)
        return respuesta_final.content

    return respuesta.content


def main():
    print("=" * 60)
    print("  SoporteGit — Asistente de voz con tools + Chroma")
    print("=" * 60)
    print("Comandos:  [Enter] grabar  |  q + Enter salir")
    print("-" * 60)

    from tools_git import _cargar_vectorstore
    vs = _cargar_vectorstore()
    if vs is None:
        print("⚠️  Chroma no disponible → se usará fallback local.")
        print("   Para activarlo: cd .. && python -m src.ingest\n")
    else:
        print("✅ Base Chroma lista.\n")

    while True:
        accion = input("\nPresiona Enter para hablar (o 'q' para salir): ").strip().lower()
        if accion == "q":
            print("Hasta luego.")
            break

        try:
            wav_bytes = grabar_audio()
            print("\n📝 Transcribiendo...")
            texto = transcribir(wav_bytes)
            print(f"\nTú dijiste:\n  «{texto}»")

            if not texto:
                print("No se detectó voz. Intenta de nuevo.")
                continue

            print("\n🤖 Pensando...")
            respuesta = responder_con_tools(texto)
            print(f"\nRespuesta:\n{respuesta}")

        except KeyboardInterrupt:
            print("\nInterrumpido.")
            break
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
