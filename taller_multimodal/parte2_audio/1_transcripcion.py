"""
2.1 - Transcripción de audios desde archivo
Modelo: whisper-large-v3-turbo (Groq)
"""
from pathlib import Path
import os
from dotenv import load_dotenv
from groq import Groq

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
        "Coloca al menos 4 grabaciones (.wav / .mp3) con preguntas sobre Git."
    )

client = Groq()

print("=" * 60)
print("  2.1  Transcripción desde archivo (SoporteGit)")
print("=" * 60)
print(f"\nAudios encontrados: {len(audios)}")
for i, a in enumerate(audios, 1):
    print(f"  {i}. {a.name}")

for ruta in audios:
    print(f"\n{'─' * 50}")
    print(f"Transcribiendo: {ruta.name}")
    print("─" * 50)

    with open(ruta, "rb") as f:
        transcripcion = client.audio.transcriptions.create(
            file=(ruta.name, f.read()),
            model="whisper-large-v3-turbo",
            language="es",
        )

    print(transcripcion.text)

print("\n" + "=" * 60)
print("Transcripción terminada.")
print("=" * 60)
