# Análisis del archivo `amaem-pda-agua-registrada-trimestral-explotacion-solo-alicante-amaem-pda-agua-registrada-trimest.csv`

## Metadatos básicos

| Campo | Valor |
| --- | --- |
| Ruta | C:\Users\xngel\Desktop\ProyectosCodex\Hackathon-Aguas2026\reales\amaem-pda-agua-registrada-trimestral-explotacion-solo-alicante-amaem-pda-agua-registrada-trimest.csv |
| Extensión | .csv |
| Tamaño (bytes) | 671 |
| Codificación detectada | utf-8-sig |
| Delimitador | ',' |
| Filas de datos | 24 |
| Columnas | 4 |
| Grupos de filas exactamente idénticas | 0 |
| Filas idénticas adicionales | 0 |

## Estructura del dataset

| Columna | Tipo inferido | No vacíos | Vacíos | Distintos | % distintos | Muestras |
| --- | --- | --- | --- | --- | --- | --- |
| AÑO | numérica | 24 | 0 | 6 | 25.00% | 2020, 2021, 2022, 2023, 2024 |
| TRIMESTRE | numérica | 24 | 0 | 4 | 16.67% | 1, 2, 3, 4 |
| Explotación | texto categórico | 24 | 0 | 1 | 4.17% | Alicante |
| TOTAL Volumen agua potable registrada (m³) | numérica | 24 | 0 | 24 | 100.00% | 4745613, 4638840, 6014075, 5345197, 4756850 |

## Primeras y últimas filas

| AÑO | TRIMESTRE | Explotación | TOTAL Volumen agua potable registrada (m³) |
| --- | --- | --- | --- |
| 2020 | 1 | Alicante | 4745613 |
| 2020 | 2 | Alicante | 4638840 |
| 2020 | 3 | Alicante | 6014075 |
| 2020 | 4 | Alicante | 5345197 |
| 2021 | 1 | Alicante | 4756850 |
| 2024 | 4 | Alicante | 5812841 |
| 2025 | 1 | Alicante | 5252813 |
| 2025 | 2 | Alicante | 5400161 |
| 2025 | 3 | Alicante | 6640346 |
| 2025 | 4 | Alicante | 5960744 |

## Observaciones destacadas

- La columna `Explotación` es constante: siempre vale `Alicante`.

## Detalle por columna

### Columna: `AÑO`

- Tipo inferido: `numérica`
- No vacíos: `24`
- Vacíos: `0`
- Distintos: `6`
- Longitud mínima/máxima: `4` / `4`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 2020 | 4 |
| 2021 | 4 |
| 2022 | 4 |
| 2023 | 4 |
| 2024 | 4 |
| 2025 | 4 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 2.020 |
| Máximo | 2.025 |
| Media | 2.022,50 |
| Mediana | 2.022,50 |
| Suma | 48.540 |
### Columna: `TRIMESTRE`

- Tipo inferido: `numérica`
- No vacíos: `24`
- Vacíos: `0`
- Distintos: `4`
- Longitud mínima/máxima: `1` / `1`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 1 | 6 |
| 2 | 6 |
| 3 | 6 |
| 4 | 6 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 1 |
| Máximo | 4 |
| Media | 2,50 |
| Mediana | 2,50 |
| Suma | 60 |
### Columna: `Explotación`

- Tipo inferido: `texto categórico`
- No vacíos: `24`
- Vacíos: `0`
- Distintos: `1`
- Longitud mínima/máxima: `8` / `8`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| Alicante | 24 |
### Columna: `TOTAL Volumen agua potable registrada (m³)`

- Tipo inferido: `numérica`
- No vacíos: `24`
- Vacíos: `0`
- Distintos: `24`
- Longitud mínima/máxima: `7` / `7`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 4745613 | 1 |
| 4638840 | 1 |
| 6014075 | 1 |
| 5345197 | 1 |
| 4756850 | 1 |
| 4852555 | 1 |
| 5958410 | 1 |
| 5282889 | 1 |
| 4836457 | 1 |
| 4974253 | 1 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 4.638.840 |
| Máximo | 6.640.346 |
| Media | 5.519.245,29 |
| Mediana | 5.463.187,50 |
| Suma | 132.461.887 |

## Lectura analítica específica

### Totales anuales de agua registrada

| Año | Volumen total (m³) |
| --- | --- |
| 2020 | 20.743.725 |
| 2021 | 20.850.704 |
| 2022 | 21.782.951 |
| 2023 | 22.570.839 |
| 2024 | 23.259.604 |
| 2025 | 23.254.064 |

- Trimestre con mayor volumen: `2025 T3` con `6.640.346` m³.
- Trimestre con menor volumen: `2020 T2` con `4.638.840` m³.
