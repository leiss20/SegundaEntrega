"""
1.1 - Pregunta sobre una imagen del dominio Git
Modelo de visión: qwen/qwen3.8-27b (Groq)
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
    + list(CARPETA.glob("*.webp"))
)

if not imagenes:
    raise FileNotFoundError(
        f"No hay imágenes en {CARPETA}\n"
        "Coloca al menos una captura de terminal Git, conflicto, ramas, etc."
    )

print("=" * 60)
print("  1.1  Pregunta sobre una imagen (SoporteGit)")
print("=" * 60)
print("\nImágenes disponibles:")
for i, img in enumerate(imagenes, 1):
    print(f"  {i}. {img.name}")

while True:
    try:
        idx = int(input("\nElige el número de la imagen: ")) - 1
        if 0 <= idx < len(imagenes):
            break
        print("Número fuera de rango.")
    except ValueError:
        print("Ingresa un número válido.")

ruta = imagenes[idx]
img_bytes = ruta.read_bytes()
img_b64 = base64.b64encode(img_bytes).decode("utf-8")

ext = ruta.suffix.lower()
mime_map = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
mime = mime_map.get(ext, "image/png")

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=1024,
)

pregunta = (
    "¿Qué comando de Git se está ejecutando o qué situación se observa en esta imagen? "
    "Explica brevemente qué significa y qué podría hacer el usuario a continuación."
)

mensaje = HumanMessage(
    content=[
        {"type": "text", "text": pregunta},
        {"type": "image", "base64": img_b64, "mime_type": mime},
    ]
)

print("\n--- Imagen ---")
print(ruta.name)
print("\n--- Pregunta ---")
print(pregunta)
print("\n--- Respuesta del modelo ---")
respuesta = llm.invoke([mensaje])
print(respuesta.content)
print("\n" + "=" * 60)
