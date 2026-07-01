# Market Intelligence Summarizer

Servicio API que interpreta datos de mercado de futuros cripto en tiempo real (funding rate, open interest, order book imbalance) usando un LLM, generando reportes en lenguaje natural listos para distribucion automatizada.

## Stack tecnico

- Python 3.11+
- FastAPI
- Pydantic
- Anthropic API (Claude)
- Docker + Docker Compose
- GitHub Actions (CI/CD)

## Instalacion

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tu ANTHROPIC_API_KEY
\`\`\`

## Uso local

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

Documentacion interactiva: http://127.0.0.1:8000/docs

## Uso con Docker

\`\`\`bash
docker compose up --build
\`\`\`

## Seguridad

Todas las credenciales se manejan via variables de entorno (.env, excluido de Git). Ninguna key se expone en logs, codigo o respuestas de la API.

## Estado del proyecto

Fase 1: servicio funcional con datos mock. Completa.
Fase 2: Docker + CI/CD con GitHub Actions. Completa.
Fase 3 (siguiente): conexion a datos reales de produccion.
