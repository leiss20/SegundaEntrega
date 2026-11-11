"""
1.3 - Varias imágenes en una sola solicitud (comparación / resumen conjunto)
Modelo de visión: qwen/qwen3.8-27b (máximo 3 imágenes por solicitud)
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

if len(imagenes) < 2:
    raise FileNotFoundError(
        f"Se necesitan al menos 2 imágenes en {CARPETA}\n"
        f"Encontradas: {len(imagenes)}"
    )

# Elige 2 o 3 imágenes (límite del modelo = 3)
MAX_IMAGENES = 3
seleccionadas = imagenes[:MAX_IMAGENES]

print("=" * 60)
print("  1.3  Varias imágenes en una solicitud (SoporteGit)")
print("=" * 60)
print("\nImágenes que se enviarán:")
for img in seleccionadas:
    print(f"  - {img.name}")

contenido = [
    {
        "type": "text",
        "text": (
            "Te envío varias capturas relacionadas con Git. "
            "Haz un resumen conjunto: ¿qué tienen en común? "
            "¿Qué flujo de trabajo o problema se está ilustrando? "
            "Compara las situaciones si es posible y sugiere el siguiente paso lógico."
        ),
    }
]

for ruta in seleccionadas:
    img_b64 = base64.b64encode(ruta.read_bytes()).decode("utf-8")
    ext = ruta.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    if ext == ".webp":
        mime = "image/webp"
    contenido.append({"type": "image", "base64": img_b64, "mime_type": mime})

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=1500,
)

mensaje = HumanMessage(content=contenido)

print("\n--- Respuesta del modelo ---")
respuesta = llm.invoke([mensaje])
print(respuesta.content)
print("\n" + "=" * 60)
