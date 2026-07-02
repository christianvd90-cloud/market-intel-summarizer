# market-intel-summarizer

Sistema de trading algorítmico para Binance construido mediante investigación cuantitativa iterativa. Este repositorio documenta el proceso completo — incluyendo los fracasos — y expone públicamente la metodología de validación y la infraestructura de recolección de datos. El código de producción de los sistemas validados se distribuye por niveles de acceso (ver sección [Acceso al código](#acceso-al-código)).

> **Aviso:** Los resultados de backtesting son simulaciones con costos reales (comisiones, funding, slippage). No son garantía de rendimiento futuro. Todo el sistema opera en modo paper hasta validación completa en vivo.

---

## Estado del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Servicio funcional con LLM integrado, pruebas end-to-end | ✅ Completa |
| 2 | Docker + CI/CD con GitHub Actions | ✅ Completa |
| 3 | Conexión a datos reales de Binance (spot + futuros) | ✅ Completa |
| 4 | Cadena de 10 bots spot descartada — edge no robusto OOS | ✅ Documentada |
| 5 | Sistema CA validado en producción (BTC + INJ, paper) | ✅ Activa |
| 6 | SCALPR (scalping 15m BTC + INJ) validado walk-forward | ✅ Activa |
| 7 | Funding arb delta-neutral validado — primer alpha all-weather | ✅ Activa |
| 8 | Monitor de microestructura v4 (OB + OI + funding + basis) | ✅ Corriendo |
| 9 | Validación multi-activo (ETH candidato, SOL descartado) | ✅ Completa |
| 10 | Detector de giros de funding (48% recall OOS, plan B) | 🔄 En curso |
| 11 | Re-validación del detector con datos de OI y basis reales | ⏳ 4–6 semanas |
| 12 | Evaluación de capital real en funding arb (~30 fundings) | ⏳ ~2 semanas |

---

## Acceso al código

El proyecto tiene tres niveles de acceso. Esta distinción es explícita y deliberada — el código de producción es el resultado de cientos de horas de investigación y validación, y se distribuye de forma controlada.

### 🟢 Público — en este repositorio

| Archivo | Descripción |
|---------|-------------|
| `orderbook_monitor_v4.py` | Monitor de microestructura (OB + OI + funding + basis) |
| `backtesting_v29.py` | Motor de backtesting CA (versión final, sin parámetros optimizados) |
| `detector_giros_funding_wf_v1.py` | Detector walk-forward de giros de funding (línea base) |
| `requirements.txt` | Dependencias del proyecto |
| `docs/` | Las 183 conclusiones documentadas en Markdown |

### 🔵 Acceso técnico — tier $29–49/mes

Código de producción de los sistemas validados, parámetros exactos, instaladores launchd y actualizaciones cuando hay nuevas validaciones walk-forward.

| Archivo | Descripción |
|---------|-------------|
| `paper_trading_bot.py` | CA BTC — trend following 1H (producción, paper) |
| `paper_trading_bot_inj_v2.py` | CA INJ — trend following 1H (producción, paper) |
| `scalping_bot_btc.py` | SCALPR BTC V7 — scalping 15m |
| `scalping_bot_inj.py` | SCALPR INJ V7 — scalping 15m |
| `funding_paper_bot_v2.py` | Funding arb (leverage configurable, multi-activo preparado) |
| `instalar_*.py` | Instaladores launchd para cada servicio |

### 🟣 Investigación en vivo — tier $99–149/mes

Acceso al proceso de investigación en curso: experimentos antes de ser publicados, sesiones de validación cada dos semanas, dashboard de P&L en tiempo real del funding bot, y canal directo para preguntas técnicas.

> Para información sobre acceso a los tiers técnico y de investigación: [christianvd90@gmail.com](mailto:christianvd90@gmail.com)

---

## Sistemas en producción (paper)

Tres servicios corriendo en `launchd` de macOS:

```
com.scalpr.btc.live      SCALPR BTC — scalping spot paper
com.funding.paper.bot    Funding arb delta-neutral — cada 8h
com.orderbook.monitor    Monitor de microestructura — cada 5 min
```

### CA — Trend following (BTC/USDT + INJ/USDT, 1H)

Estrategia E6: seis condiciones simultáneas en tres marcos temporales (1D / 4H / 1H). Configuración validada tras 29 versiones de backtesting y walk-forward 4/4 a favor.

| Parámetro | BTC | INJ |
|-----------|-----|-----|
| Stop mínimo | 2.4 × ATR | 2.5 × ATR |
| TP1 | 4.8 × ATR (50% posición) | 4.8 × ATR (50%) |
| TP2 | 8.0 × ATR (50% restante) | 8.0 × ATR (50%) |
| Leverage | x5 margen aislado | x5 margen aislado |
| Riesgo dinámico | 1.5% / 1.8% / 2.1% según rachas | igual |
| Filtro C7 ATR% | inactivo | ≤ 2.0% activo |
| Capital paper | $500 | $283.57 |

Walk-forward (35 meses, ventanas OOS de 2 meses): **R² ≥ 75%, score RoMaD × PF**.
*Código y parámetros exactos disponibles en el tier técnico.*

### SCALPR — Scalping (BTC/USDT + INJ/USDT, 15m)

| Parámetro | SCALPR BTC V7 | SCALPR INJ V7 |
|-----------|--------------|--------------|
| SL | 1.8 × ATR | 1.8 × ATR |
| TP1 | 2.0 × ATR (50%) | 2.0 × ATR (50%) |
| TP2 | 4.0 × ATR (50%) | 4.0 × ATR (50%) |
| ADX mínimo | 25 | 32 |
| Horas bloqueadas | 4,8,11,14,15,17 | 0,1,5,16 |
| Días bloqueados | lun, dom | lun, mar |
| Mejor régimen | VOLÁTIL (70% WR) | — |

*Código y parámetros exactos disponibles en el tier técnico.*

### Funding arb delta-neutral (BTC/USDT)

Posición spot long + perp short simultáneas. Cobra el funding rate tres veces al día (UTC 0/8/16) sin exposición direccional.

| Métrica | Valor |
|---------|-------|
| CAGR histórico (35m) | +8.7% |
| Drawdown máximo | -0.25% |
| % tiempo funding positivo | 86% |
| Basis riesgo acumulado | +0.01% |
| Peor tramo 30 días | -0.17% |
| Basis que liquidaría a 2x | 49.5% (histórico max: 0.29%) |

ETH validada con perfil idéntico (+7.9% CAGR, 84% positivo). SOL descartada (DD -2.59%).
*Bot v2 con leverage configurable (1x–5x) disponible en el tier técnico.*

---

## Infraestructura de recolección — disponible públicamente

`orderbook_monitor_v4.py` captura cada 5 minutos para BTC, ETH y SOL:

```
order book   → mid, spread, imbalance, microprice, muros
OI           → contratos abiertos (apalancamiento agregado)
funding      → rate actual
mark_price   → precio oficial del perpetuo
basis_pct    → (mark - spot) / spot × 100
```

Los datos se guardan en CSV diario en Google Drive. La recolección continua empezó en junio 2026 — en 4–6 semanas habrá suficiente historia para re-validar el detector de giros de funding con basis y OI reales.

---

## Hallazgos principales (selección de 183 conclusiones)

### Sobre lo que NO funciona

- **El precio de BTC no es predecible a corto plazo.** Ni con trend following, ni con reversión, ni con TimesFM (foundation model de Google): 53% de acierto direccional, indistinguible del azar. No es falta de sofisticación — es propiedad del activo.

- **La sobre-operación destruye cualquier edge pequeño.** Estrategia S2 del funding (cambiar de lado según el signo): 290 cambios = 43.5% del capital en costos. Una cadena de 10 bots spot con señal basada en envolvente + volumen: edge concentrado en 2024, muerto en 2026, R² cae a 50% con slippage real.

- **N=40 produce ilusiones estadísticas.** TimesFM parecía superar al naive en funding con N=40 (80% vs 70%). Con N=150 se invirtió (57% vs 75%). Regla del proyecto: N ≥ 150 antes de concluir.

- **La rotación dinámica entre activos es destruida por los costos.** 492 cambios de activo en BTC/ETH = 73.8% en comisiones. Half-life del spread de funding: 1–2 periodos (8–16h). El spread revierte antes de que se pueda actuar.

### Sobre lo que sí funciona

- **El alpha real no es direccional — es estructural.** Cobrar la prima que los longs sobreapalancados pagan en los perpetuos. La contraparte existe y es identificable.

- **El basis spot-perp es el predictor más fuerte de giros de funding** (separación 0.334, segunda variable más útil tras el funding_actual). No la volatilidad sola (recall 5% OOS) ni la caída de precio (0.148).

- **El detector de giros combinado supera al azar con p<0.001.** 48% de recall OOS con permutación vs 45% de TimesFM. Impacto marginal (+0.3–0.8% CAGR) pero estadísticamente real.

- **El break-even prematuro colapsa el sistema.** BE antes de TP1 genera una "zona de exposición a reversión". BE@TP1 y sin-BE son equivalentes y seguros. Cualquier punto intermedio es peligroso.

*Las 183 conclusiones completas están en `docs/` (acceso público).*

---

## Metodología de validación

Todo cambio al sistema debe pasar por el mismo proceso antes de adopción:

1. **Edge vs control aleatorio** — permutación, no t-test (distribuciones fat-tailed)
2. **Walk-forward R² ≥ 75%** de ventanas OOS ganadoras
3. **N ≥ 150** antes de concluir
4. **Score = RoMaD × PF** como métrica primaria (no Sharpe — retornos no gaussianos)
5. **Aislamiento de variables** — una a la vez, nunca múltiples simultáneas
6. **Auditoría de datos crudos** antes de cualquier análisis

---

## Instalación — componentes públicos

```bash
# Requisitos: Python 3.9+, macOS (launchd)
git clone https://github.com/christianvd90-cloud/market-intel-summarizer
cd market-intel-summarizer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Variables de entorno necesarias
cp .env.example .env
# Editar .env con las keys de Binance y el token de Telegram

# Monitor de microestructura (incluido en este repo)
python instalar_orderbook_launchd_v4.py
```

Los instaladores de los sistemas CA, SCALPR y funding arb están disponibles en el tier técnico.

---

## Líneas de investigación activas

| Línea | Hipótesis | Datos necesarios | Plazo |
|-------|-----------|-----------------|-------|
| Detector giros + basis real | basis mejora recall OOS de 48% a >60% | 4–6 semanas de monitor v4 | ago 2026 |
| Detector giros + OI real | caídas de OI predicen desapalancamiento | mismo dataset | ago 2026 |
| ETH funding arb en paralelo | mismo alpha, capital adicional | ~30 fundings BTC confirmados | jul 2026 |
| Imbalance OB como predictor | imbalance extremo precede movimiento | miles de lecturas a 5min | ago 2026 |
| Mom/ATR% para SCALPR | filtrar señales con movimiento pequeño relativo a volatilidad | datos actuales | pendiente |

Los resultados de estas investigaciones se publican primero en el tier de investigación en vivo, y posteriormente en `docs/` cuando están validados.

---

## Lo que este proyecto no hace

- No provee señales de trading en tiempo real
- No gestiona capital de terceros
- No garantiza rendimiento futuro
- No recomienda ningún nivel de apalancamiento — cada operador debe evaluar su tolerancia al riesgo

---

*183 conclusiones documentadas. Última actualización: julio 2026.*
