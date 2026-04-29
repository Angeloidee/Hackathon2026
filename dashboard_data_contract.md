# Contrato de datos para dashboard y modelos

## Objetivo

Este documento define la estructura mínima que debe respetar el equipo para alimentar:

- el dashboard `aquatwin_v2.html`
- los modelos predictivos
- el pipeline futuro de STGCN

## 1. Tabla principal para STGCN

Archivo recomendado:

- `synthetic_outputs/stgcn_ready/synthetic_spatiotemporal_daily.csv`

Granularidad:

- una fila por `barrio + fecha`

Columnas actuales:

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `date` | string `YYYY-MM-DD` | fecha del registro |
| `year` | int | año |
| `month` | int | mes |
| `day` | int | día del mes |
| `weekday` | int | día de la semana `0-6` |
| `is_weekend` | int | `0` o `1` |
| `barrio` | string | nodo espacial |
| `lat` | float | latitud del barrio |
| `lon` | float | longitud del barrio |
| `population_factor` | float | factor relativo de demanda |
| `tourism_factor` | float | factor relativo de presión turística |
| `infrastructure_age` | int | antigüedad aproximada |
| `coastal` | int | `0` o `1` |
| `season_index` | int | índice estacional base 100 |
| `temperature_c` | float | temperatura diaria |
| `rainfall_mm` | float | lluvia diaria |
| `consumption_m3_day` | float | consumo diario total |
| `flow_m3h` | float | caudal horario estimado |
| `pressure_bar` | float | presión estimada |
| `risk_score` | float | score continuo de riesgo `0-1` |
| `breakdown_probability` | float | probabilidad de avería `0-1` |
| `breakdown_event` | int | evento binario `0/1` |
| `pressure_alert` | int | alerta binaria |
| `flow_alert` | int | alerta binaria |
| `anomaly_alert` | int | alerta binaria |
| `total_alerts` | int | suma de alertas |
| `risk_level` | string | `bajo`, `medio`, `alto` |

### Targets recomendados

Primer target:

- `consumption_m3_day`

Targets secundarios:

- `risk_score`
- `breakdown_probability`
- `flow_m3h`
- `pressure_bar`

## 2. Grafo espacial

Archivos:

- `synthetic_outputs/stgcn_ready/adjacency_matrix.csv`
- `synthetic_outputs/stgcn_ready/edge_list.csv`

### `adjacency_matrix.csv`

- matriz cuadrada `N x N`
- filas y columnas son barrios
- valores `0/1`

### `edge_list.csv`

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `source` | string | nodo origen |
| `target` | string | nodo destino |
| `weight` | float | peso de la conexión |

## 3. JSON para dashboard

El HTML ya está preparado para leer estos archivos:

- `synthetic_outputs/stgcn_ready/dashboard_kpis.json`
- `synthetic_outputs/stgcn_ready/dashboard_map.json`
- `synthetic_outputs/stgcn_ready/dashboard_prediction.json`

## 3.1 KPIs

Estructura:

```json
{
  "date": "2025-12-31",
  "critical_alerts": 0,
  "warnings": 4,
  "active_nodes": 9,
  "mean_pressure_bar": 3.84,
  "network_flow_m3h": 163.62
}
```

Campos:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `date` | string | fecha de referencia |
| `critical_alerts` | int | KPI de alertas críticas |
| `warnings` | int | KPI de advertencias |
| `active_nodes` | int | número de barrios activos |
| `mean_pressure_bar` | float | KPI de presión |
| `network_flow_m3h` | float | KPI de caudal agregado |

## 3.2 Mapa

Estructura:

```json
[
  {
    "barrio": "CENTRO",
    "lat": 38.3453,
    "lon": -0.4831,
    "pressure_bar": 3.897,
    "flow_m3h": 21.721,
    "infrastructure_age": 52,
    "risk_score": 0.5673,
    "risk_level": "medio",
    "total_alerts": 0,
    "breakdown_probability": 0.0712
  }
]
```

Campos obligatorios:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `barrio` | string | clave del nodo |
| `lat` | float | posición en mapa |
| `lon` | float | posición en mapa |
| `pressure_bar` | float | panel lateral |
| `flow_m3h` | float | panel lateral |
| `infrastructure_age` | int | panel lateral |
| `risk_score` | float | gradiente / scoring |
| `risk_level` | string | color del mapa |
| `total_alerts` | int | alertas del barrio |
| `breakdown_probability` | float | gráfico de averías |

## 3.3 Predicción

Estructura mínima actual:

```json
{
  "labels": ["2022-01", "2022-02"],
  "historical_consumption_m3": [127197.47, 116878.74],
  "avg_risk_score": [0.3797, 0.3846],
  "breakdowns": [21, 14]
}
```

Campos actuales:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `labels` | array string | eje temporal |
| `historical_consumption_m3` | array float | serie histórica |
| `avg_risk_score` | array float | apoyo analítico |
| `breakdowns` | array int | apoyo analítico |

### Campos recomendados para la siguiente versión

Cuando el equipo tenga ya predicción real, conviene extender este JSON con:

| Campo | Tipo | Uso |
| --- | --- | --- |
| `forecast_consumption_m3` | array float o null | predicción |
| `forecast_min_m3` | array float o null | banda inferior |
| `forecast_max_m3` | array float o null | banda superior |

## 4. Split recomendado para modelado

- `train`: `2022-01-01` a `2024-12-31`
- `val`: `2025-01-01` a `2025-06-30`
- `test`: `2025-07-01` a `2025-12-31`

## 5. Convención para el equipo

- Nodo espacial oficial: `barrio`
- Columna temporal oficial: `date`
- Primer target oficial: `consumption_m3_day`
- Salida visual mínima del modelo:
  - consumo futuro por barrio
  - score de riesgo por barrio
  - ranking de probabilidad de avería
