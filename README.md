# Transcriptor Pro

Aplicación web que convierte **audio y video en texto**, con la hora (`HH:MM:SS`) de cada frase.
La transcripción usa Whisper a través de la API de Groq.

## Características
- Acepta MP3, WAV, M4A, FLAC, MP4, MKV, MOV, WEBM.
- Marcas de tiempo por frase, también en grabaciones largas (se procesan por tramos de 15 minutos).
- Clic en una hora para saltar a ese momento; la frase activa se resalta al reproducir.
- Búsqueda dentro de la transcripción y botón de copiar.
- Exporta a TXT, SRT, VTT y JSON.
- Tema claro y oscuro.

## Requisitos
- Python 3.10 o superior
- Clave de API de Groq (gratuita): https://console.groq.com/keys
- ffmpeg (recomendado): comprime el audio y extrae el sonido de videos largos. Sin ffmpeg solo se aceptan archivos de hasta 24 MB.

## Instalación
```bash
python -m venv .venv
.venv\Scripts\activate           # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
```
Abre `.env` y pega tu clave en `GROQ_API_KEY=`. Luego:
```bash
uvicorn app.main:app --reload
```
Abre http://localhost:8000.

### Windows
Después de instalar Python, haz doble clic en `run.bat`: crea el entorno, instala las dependencias, abre `.env` la primera vez y arranca el servidor.
Para instalar ffmpeg: `winget install Gyan.FFmpeg`.

### Docker
```bash
docker build -t transcriptor-pro .
docker run -p 8000:8000 -e GROQ_API_KEY=tu_clave transcriptor-pro
```

## Privacidad
El audio se envía a Groq para transcribirse. No uses este servicio con grabaciones confidenciales sin revisar sus condiciones.

## Modelos
| Modelo | Uso |
|---|---|
| whisper-large-v3-turbo | Rápido y económico (por defecto) |
| whisper-large-v3 | Máxima precisión |

## API
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/transcribe` | Campos: `file`, `model`, `language`. Devuelve `job_id`. |
| GET | `/api/jobs/{id}?since=N` | Estado, progreso y frases nuevas desde la posición N. |
| GET | `/api/jobs/{id}/export?format=txt\|srt\|vtt\|json&timestamps=true` | Descarga la transcripción. |

## Estructura
```
app/
  main.py         API y manejo de trabajos
  transcriber.py  ffmpeg opcional + API de Groq
  exporters.py    TXT, SRT, VTT, JSON
  static/index.html  Interfaz web
.env.example
Dockerfile
requirements.txt
run.bat
```

## Notas
- Los trabajos se guardan en memoria; al reiniciar el servidor se pierden.
- El plan gratuito de Groq tiene límites de uso por minuto y por día. Si aparece un error 429, espera unos minutos.
