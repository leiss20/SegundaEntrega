"""
1.2 - Extracción estructurada de 3 imágenes de Git → JSON validado
Modelo de visión: qwen/qwen3.8-27b (Groq)
"""
from pathlib import Path
import base64
import json
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise ValueError("Falta GROQ_API_KEY en el archivo .env")


# ---------- Esquema (mínimo 5 campos útiles del dominio Git) ----------
class InfoGitImagen(BaseModel):
    comando_principal: Optional[str] = Field(
        None, description="Comando de Git visible (ej: git status, git merge, git log)"
    )
    tipo_situacion: str = Field(
        ...,
        description="Tipo de situación: status | conflicto | ramas | log | error | rebase | otro",
    )
    archivos_mencionados: List[str] = Field(
        default_factory=list, description="Nombres de archivos visibles en la imagen"
    )
    rama_actual: Optional[str] = Field(
        None, description="Nombre de la rama actual si se puede ver"
    )
    mensaje_error: Optional[str] = Field(
        None, description="Texto del error o conflicto si existe"
    )
    resumen_corto: str = Field(
        ..., description="Resumen en una frase de lo que muestra la imagen"
    )


# ---------- Configuración ----------
CARPETA = Path(__file__).resolve().parent.parent / "imagenes"
imagenes = sorted(
    list(CARPETA.glob("*.png"))
    + list(CARPETA.glob("*.jpg"))
    + list(CARPETA.glob("*.jpeg"))
    + list(CARPETA.glob("*.webp"))
)

if len(imagenes) < 3:
    raise FileNotFoundError(
        f"Se necesitan al menos 3 imágenes en {CARPETA}\n"
        f"Encontradas: {len(imagenes)}"
    )

# Usa las 3 primeras (puedes cambiar los índices)
imagenes_a_usar = imagenes[:3]

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    max_tokens=1024,
)

PROMPT = """Analiza esta captura relacionada con Git y extrae la información en formato JSON estricto.
Usa exactamente estas claves (sin agregar ni quitar ninguna):

{
  "comando_principal": string o null,
  "tipo_situacion": "status" | "conflicto" | "ramas" | "log" | "error" | "rebase" | "otro",
  "archivos_mencionados": [lista de strings],
  "rama_actual": string o null,
  "mensaje_error": string o null,
  "resumen_corto": string
}

Responde SOLO con el JSON válido, sin markdown, sin explicaciones, sin ```.
"""

resultados = []

print("=" * 60)
print("  1.2  Extracción estructurada (SoporteGit)")
print("=" * 60)

for ruta in imagenes_a_usar:
    print(f"\n{'─' * 50}")
    print(f"Procesando: {ruta.name}")
    print("─" * 50)

    img_b64 = base64.b64encode(ruta.read_bytes()).decode("utf-8")
    ext = ruta.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    if ext == ".webp":
        mime = "image/webp"

    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": PROMPT},
            {"type": "image", "base64": img_b64, "mime_type": mime},
        ]
    )

    respuesta = llm.invoke([mensaje])
    texto = respuesta.content.strip()

    # Limpieza por si el modelo agrega ```json
    if "```" in texto:
        partes = texto.split("```")
        for p in partes:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{"):
                texto = p
                break

    print("\nRespuesta cruda del modelo:")
    print(texto)

    # Validación
    try:
        data = json.loads(texto)
        obj = InfoGitImagen(**data)
        print("\n✅ JSON válido según el esquema")
        print(obj.model_dump_json(indent=2, ensure_ascii=False))
        resultados.append(
            {"imagen": ruta.name, "ok": True, "datos": obj.model_dump()}
        )
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: no es JSON válido → {e}")
        resultados.append({"imagen": ruta.name, "ok": False, "error": str(e)})
    except ValidationError as e:
        print(f"\n❌ Error de validación del esquema →")
        print(e)
        resultados.append({"imagen": ruta.name, "ok": False, "error": str(e)})

# ---------- Resumen final ----------
print("\n\n" + "=" * 60)
print("  RESUMEN DE VALIDACIÓN")
print("=" * 60)
ok_count = 0
for r in resultados:
    estado = "✅ OK" if r["ok"] else "❌ FALLÓ"
    print(f"  {r['imagen']}: {estado}")
    if r["ok"]:
        ok_count += 1

print(f"\nImágenes con JSON válido: {ok_count}/{len(resultados)}")
print(
    "\nNota para el informe: completa la tabla de aciertos campo por campo "
    "comparando el valor real que ves en la imagen con el valor extraído."
)
