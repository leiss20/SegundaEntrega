"""
1.4 - Error provocado a propósito
Se fuerza el límite de máximo 3 imágenes del modelo qwen/qwen3.8-27b
"""
from pathlib import Path
import base64
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Falta GROQ_API_KEY en el archivo .env")

CARPETA = Path(__file__).resolve().parent.parent / "imagenes"
imagenes = sorted(
    list(CARPETA.glob("*.png"))
    + list(CARPETA.glob("*.jpg"))
    + list(CARPETA.glob("*.jpeg"))
)

if not imagenes:
    raise FileNotFoundError(
        f"No hay imágenes en {CARPETA}. "
        "Se necesita al menos una para provocar el error."
    )

ruta = imagenes[0]
img_b64 = base64.b64encode(ruta.read_bytes()).decode("utf-8")
mime = "image/png" if ruta.suffix.lower() == ".png" else "image/jpeg"

print("=" * 60)
print("  1.4  Error provocado (SoporteGit)")
print("=" * 60)
print(f"\nImagen base usada: {ruta.name}")
print("Acción: se intentan enviar 4 imágenes (límite del modelo = 3)")
print("-" * 60)

# Construir mensaje con 4 imágenes (más del límite permitido)
contenido = [{"type": "text", "text": "Describe brevemente estas imágenes de Git."}]
for i in range(4):
    contenido.append(
        {"type": "image", "base64": img_b64, "mime_type": mime}
    )

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=500,
)

try:
    respuesta = llm.invoke([HumanMessage(content=contenido)])
    print("\n⚠️  La API respondió sin error (inesperado):")
    print(respuesta.content)
except Exception as e:
    print("\n✅ Error capturado correctamente:")
    print(f"   Tipo   : {type(e).__name__}")
    print(f"   Mensaje: {e}")
    print("\nCausa: se superó el límite de 3 imágenes por solicitud")
    print("       documentado para el modelo qwen/qwen3.8-27b en Groq.")

print("\n" + "=" * 60)
