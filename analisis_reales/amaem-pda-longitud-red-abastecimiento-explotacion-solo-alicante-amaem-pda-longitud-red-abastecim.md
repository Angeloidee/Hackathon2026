# Análisis del archivo `amaem-pda-longitud-red-abastecimiento-explotacion-solo-alicante-amaem-pda-longitud-red-abastecim.csv`

## Metadatos básicos

| Campo | Valor |
| --- | --- |
| Ruta | C:\Users\xngel\Desktop\ProyectosCodex\Hackathon-Aguas2026\reales\amaem-pda-longitud-red-abastecimiento-explotacion-solo-alicante-amaem-pda-longitud-red-abastecim.csv |
| Extensión | .csv |
| Tamaño (bytes) | 317 |
| Codificación detectada | utf-8-sig |
| Delimitador | ',' |
| Filas de datos | 6 |
| Columnas | 4 |
| Grupos de filas exactamente idénticas | 0 |
| Filas idénticas adicionales | 0 |

## Estructura del dataset

| Columna | Tipo inferido | No vacíos | Vacíos | Distintos | % distintos | Muestras |
| --- | --- | --- | --- | --- | --- | --- |
| AÑO | numérica | 6 | 0 | 6 | 100.00% | 2020, 2021, 2022, 2023, 2024 |
| EXPLOTACION | texto categórico | 6 | 0 | 1 | 16.67% | Alicante |
| LONGITUD RED ABASTECIMIENTO (km) | numérica | 6 | 0 | 6 | 100.00% | 1111,40, 1113,48, 1130,46, 1131,08, 1130,71 |
| LONGITUD RED ABASTECIMIENTO INSPECCIONADA BUSCAFUGAS (km) | numérica | 6 | 0 | 6 | 100.00% | 1328,92, 1247,14, 1496,57, 1813,70, 1873,99 |

## Vista completa

| AÑO | EXPLOTACION | LONGITUD RED ABASTECIMIENTO (km) | LONGITUD RED ABASTECIMIENTO INSPECCIONADA BUSCAFUGAS (km) |
| --- | --- | --- | --- |
| 2020 | Alicante | 1111,40 | 1328,92 |
| 2021 | Alicante | 1113,48 | 1247,14 |
| 2022 | Alicante | 1130,46 | 1496,57 |
| 2023 | Alicante | 1131,08 | 1813,70 |
| 2024 | Alicante | 1130,71 | 1873,99 |

## Observaciones destacadas

- La columna `EXPLOTACION` es constante: siempre vale `Alicante`.

## Detalle por columna

### Columna: `AÑO`

- Tipo inferido: `numérica`
- No vacíos: `6`
- Vacíos: `0`
- Distintos: `6`
- Longitud mínima/máxima: `4` / `4`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 2020 | 1 |
| 2021 | 1 |
| 2022 | 1 |
| 2023 | 1 |
| 2024 | 1 |
| 2025 | 1 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 2.020 |
| Máximo | 2.025 |
| Media | 2.022,50 |
| Mediana | 2.022,50 |
| Suma | 12.135 |
### Columna: `EXPLOTACION`

- Tipo inferido: `texto categórico`
- No vacíos: `6`
- Vacíos: `0`
- Distintos: `1`
- Longitud mínima/máxima: `8` / `8`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| Alicante | 6 |
### Columna: `LONGITUD RED ABASTECIMIENTO (km)`

- Tipo inferido: `numérica`
- No vacíos: `6`
- Vacíos: `0`
- Distintos: `6`
- Longitud mínima/máxima: `7` / `7`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 1111,40 | 1 |
| 1113,48 | 1 |
| 1130,46 | 1 |
| 1131,08 | 1 |
| 1130,71 | 1 |
| 1128,82 | 1 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 1.111,40 |
| Máximo | 1.131,08 |
| Media | 1.124,33 |
| Mediana | 1.129,64 |
| Suma | 6.745,95 |
### Columna: `LONGITUD RED ABASTECIMIENTO INSPECCIONADA BUSCAFUGAS (km)`

- Tipo inferido: `numérica`
- No vacíos: `6`
- Vacíos: `0`
- Distintos: `6`
- Longitud mínima/máxima: `7` / `7`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 1328,92 | 1 |
| 1247,14 | 1 |
| 1496,57 | 1 |
| 1813,70 | 1 |
| 1873,99 | 1 |
| 1275,92 | 1 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 1.247,14 |
| Máximo | 1.873,99 |
| Media | 1.506,04 |
| Mediana | 1.412,74 |
| Suma | 9.036,24 |

## Lectura analítica específica

### Evolución anual y esfuerzo de inspección

| Año | Red total (km) | Red inspeccionada (km) | % inspeccionado sobre red | Variación anual red (km) |
| --- | --- | --- | --- | --- |
| 2020 | 1.111,40 | 1.328,92 | 119.57% | - |
| 2021 | 1.113,48 | 1.247,14 | 112.00% | 2,08 |
| 2022 | 1.130,46 | 1.496,57 | 132.39% | 16,98 |
| 2023 | 1.131,08 | 1.813,70 | 160.35% | 0,62 |
| 2024 | 1.130,71 | 1.873,99 | 165.74% | -0,37 |
| 2025 | 1.128,82 | 1.275,92 | 113.03% | -1,89 |

- El porcentaje puede superar el 100% si en el año se inspeccionan tramos repetidos o campañas sobre la misma red.
