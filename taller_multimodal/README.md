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

## Imágenes recomendadas (mínimo 5)

1. `git status` con archivos modificados  
2. Listado de ramas (`git branch -a`)  
3. Mensaje de conflicto de merge  
4. `git log --oneline`  
5. Pull Request o tags en GitHub  

## Audios recomendados (mínimo 4)

| # | Hablante | Condición  | Pregunta de ejemplo |
|---|----------|------------|---------------------|
| 1 | A | Sin ruido | ¿Cómo deshago el último commit que aún no he subido? |
| 2 | B | Sin ruido | ¿Qué diferencia hay entre git merge y git rebase? |
| 3 | A | Con ruido | Tengo un conflicto de merge en main.py, ¿cómo lo resuelvo? |
| 4 | B | Sin ruido | ¿Qué hace git cherry-pick y cuándo se usa? |

## Límites (Groq)

- **Visión:** máx. 3 imágenes por solicitud, 20 MB total  
- **Audio:** hasta 25 MB por archivo (plan gratuito)

## Seguridad

- Nunca subas el archivo `.env`
- `.env` ya está en `.gitignore`

## Evaluación del taller

| Criterio | Puntos |
|----------|--------|
| 1. Preguntas sobre imágenes (1.1 y 1.3) | 7.5 |
| 2. Extracción estructurada (1.2) | 12.5 |
| 3. Error provocado (1.4) | 5 |
| 4. Transcripción desde archivo (2.1) | 12.5 |
| 5. Respuesta a partir de transcripción (2.2) | 12.5 |
| **Total** | **50** |
