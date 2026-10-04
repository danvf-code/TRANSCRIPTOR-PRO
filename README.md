# TRANSCRIPTOR-PRO

Aplicación web de transcripción de audio y video con IA. Convierte grabaciones en texto con marcas de tiempo `HH:MM:SS` por frase, usando Whisper a través de la API de Groq.

## Características

- **Formatos de entrada:** MP3, WAV, M4A, FLAC, MP4, MKV, MOV, WEBM.
- **Grabaciones largas:** procesamiento por tramos de 15 minutos con marcas de tiempo continuas.
- **Interfaz interactiva:** clic en una hora para saltar a ese momento; la frase activa se resalta durante la reproducción.
- **Búsqueda y copiado** dentro de la transcripción.
- **Exportación:** TXT, SRT, VTT y JSON.
- **Tema claro y oscuro.**
- **API REST** documentada para integrarla en otros sistemas.

## Requisitos

| Requisito | Detalle |
|---|---|
| Python | 3.10 o superior |
| Clave de Groq | Gratuita: https://console.groq.com/keys |
| ffmpeg | Recomendado. Sin él, el límite es 24 MB por archivo |

## Inicio rápido

```bash
git clone https://github.com/danvf-code/TRANSCRIPTOR-PRO.git
cd TRANSCRIPTOR-PRO

python -m venv .venv
.venv\Scripts\activate            # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

copy .env.example .env            # Linux/Mac: cp .env.example .env
```

Abre `.env` y define tu clave:

```env
GROQ_API_KEY=tu_clave_aqui
```

Inicia el servidor:

```bash
python -m uvicorn app.main:app --reload
```

Abre http://localhost:8000.

### Windows

Doble clic en `run.bat`. Crea el entorno, instala dependencias, abre `.env` la primera vez y arranca el servidor.

Instalar ffmpeg:

```powershell
winget install Gyan.FFmpeg
```

> Si Windows bloquea `uvicorn.exe` por una directiva de control de aplicaciones, usa siempre `python -m uvicorn`.

### Docker

```bash
docker build -t transcriptor-pro .
docker run -p 8000:8000 -e GROQ_API_KEY=tu_clave transcriptor-pro
```

La imagen incluye ffmpeg.

## Modelos

| Modelo | Uso |
|---|---|
| `whisper-large-v3-turbo` | Rápido y económico (por defecto) |
| `whisper-large-v3` | Máxima precisión |

## API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/transcribe` | Campos: `file`, `model`, `language`. Devuelve `job_id`. |
| `GET` | `/api/jobs/{id}?since=N` | Estado, progreso y frases nuevas desde la posición `N`. |
| `GET` | `/api/jobs/{id}/export?format=txt\|srt\|vtt\|json&timestamps=true` | Descarga la transcripción. |

Ejemplo:

```bash
curl -F "file=@entrevista.mp3" -F "model=whisper-large-v3-turbo" -F "language=es" \
  http://localhost:8000/api/transcribe
```

## Estructura del proyecto

```
app/
  main.py            API y gestión de trabajos
  transcriber.py     ffmpeg opcional + cliente de Groq
  exporters.py       TXT, SRT, VTT, JSON
  static/index.html  Interfaz web
.env.example         Plantilla de variables de entorno
Dockerfile
requirements.txt
run.bat              Arranque con un clic en Windows
```

## Seguridad y privacidad

- El archivo `.env` está en `.gitignore`. **Nunca subas tu clave al repositorio.**
- El audio se envía a Groq para su transcripción. No uses el servicio con grabaciones confidenciales sin revisar sus condiciones.
- Si expones una clave por error, revócala en https://console.groq.com/keys y crea otra.

## Limitaciones

- Los trabajos se guardan en memoria; se pierden al reiniciar el servidor.
- El plan gratuito de Groq tiene límites por minuto y por día. Ante un error `429`, espera unos minutos.

## Licencia

Añade aquí tu licencia (por ejemplo, MIT).
