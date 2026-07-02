# Imagen base ligera con Python 3.11
FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias primero (mejor uso de cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el codigo de la app y el notifier
COPY app/ ./app/
COPY notifier.py .

# Nunca copies .env al contenedor. Las credenciales se inyectan
# en runtime via variables de entorno (ver docker-compose.yml).

EXPOSE 8000

# Usuario no-root por buenas practicas de seguridad
RUN useradd -m appuser
USER appuser

# Comando por defecto: levanta la API. El servicio "notifier" en
# docker-compose.yml sobreescribe este comando para correr notifier.py.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
