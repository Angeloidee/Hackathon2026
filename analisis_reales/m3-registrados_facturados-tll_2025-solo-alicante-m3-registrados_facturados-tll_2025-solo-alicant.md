# Análisis del archivo `m3-registrados_facturados-tll_2025-solo-alicante-m3-registrados_facturados-tll_2025-solo-alicant.csv`

## Metadatos básicos

| Campo | Valor |
| --- | --- |
| Ruta | C:\Users\xngel\Desktop\ProyectosCodex\Hackathon-Aguas2026\reales\m3-registrados_facturados-tll_2025-solo-alicante-m3-registrados_facturados-tll_2025-solo-alicant.csv |
| Extensión | .csv |
| Tamaño (bytes) | 54159884 |
| Codificación detectada | utf-8-sig |
| Delimitador | ',' |
| Filas de datos | 767202 |
| Columnas | 8 |
| Grupos de filas exactamente idénticas | 18835 |
| Filas idénticas adicionales | 723538 |

## Estructura del dataset

| Columna | Tipo inferido | No vacíos | Vacíos | Distintos | % distintos | Muestras |
| --- | --- | --- | --- | --- | --- | --- |
| EXPLOTACION | texto categórico | 767202 | 0 | 1 | 0.00% | ALICANTE |
| FECHA FACTURA | fecha | 767202 | 0 | 230 | 0.03% | 02/01/2025, 03/01/2025, 07/01/2025, 08/01/2025, 09/01/2025 |
| PERIODO | texto categórico | 767202 | 0 | 13 | 0.00% | 2025 -  01, 2025 -  02, 2025 -  03, 2025 -  04, 2025 -  05 |
| PERIODICIDAD | texto categórico | 767122 | 80 | 2 | 0.00% | Mensual, Trimestral |
| DIAS LECTURA | numérica | 767202 | 0 | 177 | 0.02% | 30, 90, 32, 17, 8 |
| FECHA LECTURA | fecha | 767202 | 0 | 240 | 0.03% | 27/12/2024, 02/01/2025, 30/12/2024, 31/12/2024, 03/01/2025 |
| FECHA PREVISTA LECTURA | fecha | 767202 | 0 | 140 | 0.02% | 27/12/2024, 03/01/2025, 30/12/2024, 31/12/2024, 02/01/2025 |
| M3 A FACTURAR | numérica | 767202 | 0 | 1564 | 0.20% | 0, 35, 29, 1.634, 37 |

## Primeras y últimas filas

| EXPLOTACION | FECHA FACTURA | PERIODO | PERIODICIDAD | DIAS LECTURA | FECHA LECTURA | FECHA PREVISTA LECTURA | M3 A FACTURAR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ALICANTE | 02/01/2025 | 2025 -  01 | Mensual | 30 | 27/12/2024 | 27/12/2024 | 0 |
| ALICANTE | 02/01/2025 | 2025 -  01 | Mensual | 30 | 27/12/2024 | 27/12/2024 | 35 |
| ALICANTE | 02/01/2025 | 2025 -  01 | Mensual | 30 | 27/12/2024 | 27/12/2024 | 0 |
| ALICANTE | 02/01/2025 | 2025 -  01 | Mensual | 30 | 27/12/2024 | 27/12/2024 | 0 |
| ALICANTE | 02/01/2025 | 2025 -  01 | Mensual | 30 | 27/12/2024 | 27/12/2024 | 29 |
| ALICANTE | 30/12/2025 | 2026 -  01 | Mensual | 30 | 24/12/2025 | 23/12/2025 | 0 |
| ALICANTE | 30/12/2025 | 2026 -  01 | Mensual | 30 | 24/12/2025 | 23/12/2025 | 28 |
| ALICANTE | 30/12/2025 | 2026 -  01 | Mensual | 30 | 24/12/2025 | 23/12/2025 | 0 |
| ALICANTE | 30/12/2025 | 2026 -  01 | Mensual | 30 | 24/12/2025 | 23/12/2025 | 0 |
| ALICANTE | 31/12/2025 | 2026 -  01 | Trimestral | 90 | 31/12/2025 | 02/01/2026 | 18 |

## Observaciones destacadas

- La columna `EXPLOTACION` es constante: siempre vale `ALICANTE`.
- La columna `PERIODICIDAD` tiene 80 valores vacíos (0.01% del total).

## Detalle por columna

### Columna: `EXPLOTACION`

- Tipo inferido: `texto categórico`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `1`
- Longitud mínima/máxima: `8` / `8`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| ALICANTE | 767202 |
### Columna: `FECHA FACTURA`

- Tipo inferido: `fecha`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `230`
- Longitud mínima/máxima: `10` / `10`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 12/06/2025 | 20547 |
| 13/03/2025 | 19923 |
| 12/09/2025 | 19602 |
| 16/01/2025 | 17706 |
| 15/07/2025 | 17389 |
| 13/10/2025 | 16219 |
| 15/01/2025 | 15906 |
| 15/12/2025 | 15904 |
| 16/04/2025 | 15857 |
| 11/12/2025 | 15787 |

Rango temporal:

| Métrica | Valor |
| --- | --- |
| Primera fecha | 2025-01-02T00:00:00 |
| Última fecha | 2025-12-31T00:00:00 |
### Columna: `PERIODO`

- Tipo inferido: `texto categórico`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `13`
- Longitud mínima/máxima: `10` / `10`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 2025 -  04 | 189209 |
| 2025 -  03 | 187854 |
| 2025 -  02 | 186689 |
| 2025 -  01 | 184158 |
| 2025 -  10 | 2253 |
| 2025 -  12 | 2253 |
| 2025 -  11 | 2241 |
| 2025 -  09 | 2237 |
| 2025 -  08 | 2228 |
| 2025 -  07 | 2196 |
### Columna: `PERIODICIDAD`

- Tipo inferido: `texto categórico`
- No vacíos: `767122`
- Vacíos: `80`
- Distintos: `2`
- Longitud mínima/máxima: `7` / `10`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| Trimestral | 740378 |
| Mensual | 26744 |
### Columna: `DIAS LECTURA`

- Tipo inferido: `numérica`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `177`
- Longitud mínima/máxima: `1` / `3`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 91 | 397247 |
| 90 | 137877 |
| 92 | 112512 |
| 88 | 27859 |
| 94 | 24857 |
| 89 | 17523 |
| 87 | 11627 |
| 29 | 9304 |
| 30 | 8598 |
| 31 | 5423 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 0 |
| Máximo | 365 |
| Media | 88,17 |
| Mediana | 91 |
| Suma | 67.644.689 |
### Columna: `FECHA LECTURA`

- Tipo inferido: `fecha`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `240`
- Longitud mínima/máxima: `10` / `10`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 12/03/2025 | 20658 |
| 13/10/2025 | 18589 |
| 14/07/2025 | 18439 |
| 14/01/2025 | 17918 |
| 15/01/2025 | 16664 |
| 14/10/2025 | 16312 |
| 09/12/2025 | 16021 |
| 09/09/2025 | 15999 |
| 10/06/2025 | 15773 |
| 11/03/2025 | 15754 |

Rango temporal:

| Métrica | Valor |
| --- | --- |
| Primera fecha | 2024-12-27T00:00:00 |
| Última fecha | 2025-12-31T00:00:00 |
### Columna: `FECHA PREVISTA LECTURA`

- Tipo inferido: `fecha`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `140`
- Longitud mínima/máxima: `10` / `10`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 12/03/2025 | 20662 |
| 14/01/2025 | 18924 |
| 10/10/2025 | 18759 |
| 14/07/2025 | 18467 |
| 09/12/2025 | 16060 |
| 09/09/2025 | 16006 |
| 10/06/2025 | 15775 |
| 11/03/2025 | 15760 |
| 15/01/2025 | 15657 |
| 10/12/2025 | 14971 |

Rango temporal:

| Métrica | Valor |
| --- | --- |
| Primera fecha | 2024-12-27T00:00:00 |
| Última fecha | 2026-01-14T00:00:00 |
### Columna: `M3 A FACTURAR`

- Tipo inferido: `numérica`
- No vacíos: `767202`
- Vacíos: `0`
- Distintos: `1564`
- Longitud mínima/máxima: `1` / `6`

Valores más frecuentes:

| Valor | Frecuencia |
| --- | --- |
| 0 | 64190 |
| 1 | 29313 |
| 13 | 20604 |
| 12 | 20391 |
| 2 | 20334 |
| 15 | 20294 |
| 14 | 20270 |
| 16 | 20143 |
| 11 | 20141 |
| 10 | 20026 |

Estadísticas numéricas:

| Métrica | Valor |
| --- | --- |
| Mínimo | 0 |
| Máximo | 998 |
| Media | 22,17 |
| Mediana | 16 |
| Suma | 17.012.164,32 |

## Lectura analítica específica

### Volumen facturable agregado por periodo

| Periodo | Suma M3 a facturar |
| --- | --- |
| 2025 -  01 | 3.528.831,44 |
| 2025 -  02 | 3.665.097,37 |
| 2025 -  03 | 4.111.760,02 |
| 2025 -  04 | 3.868.002,28 |
| 2025 -  05 | 170.913,36 |
| 2025 -  06 | 209.746,66 |
| 2025 -  07 | 247.221,20 |
| 2025 -  08 | 259.829,40 |
| 2025 -  09 | 255.719,15 |
| 2025 -  10 | 238.659,35 |
| 2025 -  11 | 178.335,58 |
| 2025 -  12 | 173.612,21 |
| 2026 -  01 | 104.436,30 |

### Distribución de periodicidad

| Periodicidad | Registros |
| --- | --- |
| Trimestral | 740378 |
| Mensual | 26744 |
| (vacío) | 80 |

### Fechas de factura por mes

| Mes de factura | Número de registros |
| --- | --- |
| 2025-01 | 74197 |
| 2025-02 | 56656 |
| 2025-03 | 58625 |
| 2025-04 | 73104 |
| 2025-05 | 59488 |
| 2025-06 | 58899 |
| 2025-07 | 75189 |
| 2025-08 | 57993 |
| 2025-09 | 59967 |
| 2025-10 | 74926 |
| 2025-11 | 58577 |
| 2025-12 | 59581 |

### Indicadores operativos

| Indicador | Valor |
| --- | --- |
| Registros con `M3 A FACTURAR = 0` | 64190 |
| Porcentaje de ceros | 8.37% |
| Registros con consumo positivo | 703012 |
| Consumo máximo individual (m3) | 998 |
| Consumo medio individual (m3) | 22,17 |
| Consumo mediano individual (m3) | 16 |

### Diferencia entre fecha leída y fecha prevista

| Desfase en días (`prevista - lectura`) | Frecuencia |
| --- | --- |
| 0 | 710897 |
| -3 | 23351 |
| -1 | 19413 |
| 1 | 7491 |
| -2 | 4838 |
| 2 | 830 |
| 3 | 137 |
| 5 | 120 |
| 4 | 45 |
| -4 | 11 |
