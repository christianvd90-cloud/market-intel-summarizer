# Market Intelligence Summarizer

Servicio API que interpreta datos de mercado de futuros cripto en tiempo real (funding rate, open interest, order book imbalance) usando un LLM, generando reportes en lenguaje natural, con notificacion proactiva a Telegram.

## Motivacion

Los datos crudos de mercado son dificiles de interpretar rapidamente sin experiencia cuantitativa. Este proyecto traduce esas metricas a un resumen accionable en español, y ahora las distribuye de forma proactiva sin que nadie tenga que ir a buscarlas.

## Arquitectura

    [Monitor de order book] --> [CSV en Google Drive] --> [API FastAPI + LLM]
                                                                  |
                                                                  v
                                                         [Notifier (servicio 2)]
                                                                  |
                                                                  v
                                                          [Bot de Telegram]
                                                                  |
                                                                  v
                                                              [Tu chat]

Dos servicios independientes, orquestados con Docker Compose, comunicandose entre si por nombre de servicio dentro de la red de contenedores (no por localhost).

## Stack tecnico

- Python 3.11+
- FastAPI + Pydantic
- Anthropic API (Claude) para interpretacion via LLM
- Telegram Bot API para notificacion proactiva
- Docker + Docker Compose (orquestacion multi-servicio)
- GitHub Actions (CI/CD)

## Instalacion

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env

Completa tu .env con ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID.

## Uso local - API

    uvicorn app.main:app --reload

Documentacion interactiva: http://127.0.0.1:8000/docs

## Uso local - Notifier

    python notifier.py                # una consulta y envio
    python notifier.py --loop 900     # loop continuo cada 900s

## Uso con Docker (ambos servicios)

    docker compose up --build

Esto levanta la API y el notifier como servicios independientes, orquestados en la misma red.

## CI/CD

Cada push a main dispara un pipeline en GitHub Actions: lint (ruff), tests (pytest, sin credenciales), y build de la imagen Docker.

## Seguridad

Todas las credenciales se manejan via variables de entorno (.env, excluido de Git). Ninguna key ni token se expone en logs, codigo o respuestas de la API. Los mensajes de error nunca filtran rutas del sistema ni datos personales.

## Estado del proyecto

Fase 1: servicio funcional con LLM integrado. Completa.
Fase 2: Docker + CI/CD con GitHub Actions. Completa.
Fase 3: conexion a datos reales de produccion (order book via Google Drive CSV). Completa.
Fase 4: notifier de Telegram, orquestacion multi-servicio con Docker Compose. Completa.
Fase 5 (siguiente): capa de deteccion de anomalias (estadistica/ML) antes de notificar, para reducir ruido.

## Contexto

Este proyecto se apoya en un ecosistema mas amplio de automatizacion de trading algoritmico que incluye estrategias de entrada/salida basadas en multiples indicadores tecnicos, gestion de riesgo dinamica y validacion mediante walk-forward testing, operando en produccion de forma continua.
