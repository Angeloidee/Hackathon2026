# Correlaciones detectadas y propuesta de modelo sintético

## Resumen ejecutivo

Los datos sí muestran patrones correlacionables, pero no todos tienen la misma fuerza ni el mismo nivel de fiabilidad. La relación más sólida aparece entre:

- Volumen trimestral registrado de agua potable.
- Volumen trimestral agregado de `M3 A FACTURAR` en 2025.
- Consumo medio por registro en 2025.
- Porcentaje de registros a cero, con relación inversa respecto al volumen.

Los RDF no aportan variables numéricas útiles para correlación directa. Funcionan como metadatos semánticos de contexto: cobertura temporal, frecuencia de actualización, licencia, tema y distribución.

## Patrones con mayor correlación

### 1. Agua registrada trimestral vs agua facturable trimestral en 2025

Cruce entre el CSV trimestral de agua registrada y el CSV masivo de facturación, agregado por trimestre de 2025:

| Año | Trimestre | M3 facturados | M3 registrados | Ratio facturado / registrado |
| --- | --- | --- | --- | --- |
| 2025 | 1 | 3.882.388,94 | 5.252.813 | 0,7391 |
| 2025 | 2 | 4.145.903,84 | 5.400.161 | 0,7677 |
| 2025 | 3 | 4.781.280,40 | 6.640.346 | 0,7200 |
| 2025 | 4 | 4.202.591,15 | 5.960.744 | 0,7050 |

Hallazgos:

- Correlación entre `registered_m3` y `billed_m3`: `0,9519`.
- Correlación entre `registered_m3` y `billed_mean`: `0,9403`.
- Correlación entre `registered_m3` y `billed_zero_share`: `-0,9270`.
- El tercer trimestre es el pico tanto en agua registrada como en agua facturable.
- La caída en Q4 es consistente en ambos datasets.
- El ratio facturado/registrado está en una banda relativamente estable, entre `0,705` y `0,768`, lo que sugiere una relación estructural útil para modelado.

Interpretación:

El comportamiento estacional del agua registrada parece trasladarse de forma bastante clara al agua facturada. Eso convierte al dataset trimestral de agua registrada en una buena variable condicionante para generar sintéticos realistas de facturación agregada.

### 2. Intensidad de consumo vs porcentaje de registros a cero

En 2025:

- Correlación trimestral entre `billed_mean` y `billed_zero_share`: `-0,9510`.
- Correlación trimestral entre `billed_m3` y `billed_zero_share`: `-0,9671`.
- En el dataset completo, el porcentaje de ceros es `8,37%`.

Interpretación:

Cuando sube el consumo medio o el volumen total facturado, cae el porcentaje de registros con `M3 A FACTURAR = 0`. Este patrón es muy valioso para generación sintética porque evita producir tablas incoherentes donde sube el total facturado pero también crecen demasiado los consumos nulos.

### 3. Efecto de la periodicidad de lectura/facturación

Distribución observada en 2025:

- `Trimestral`: `740.378` registros.
- `Mensual`: `26.744` registros.
- Vacíos: `80` registros.

Correlaciones mensuales:

- `monthly_share` con `billed_mean`: `0,5815`.
- `monthly_share` con `billed_median`: `0,4544`.
- `monthly_share` con `days_mean`: `-0,6856`.
- `quarterly_share` con `days_mean`: `0,6738`.

Interpretación:

- Cuando aumenta la proporción de lecturas mensuales, baja la duración media del ciclo de lectura.
- Los consumos medios por registro tienden a ser más altos en meses con más peso relativo de lecturas mensuales, aunque esta señal es moderada y debe tratarse con cautela.
- La periodicidad sí es una variable explicativa relevante y debería entrar como variable categórica o condicional en el modelo.

### 4. Tamaño de red vs agua registrada

Comparación anual 2020-2025:

- Correlación entre `registered_year_m3` y `network_km`: `0,8574`.
- Correlación entre `registered_year_m3` e `inspected_km`: `0,5587`.
- Correlación entre `registered_year_m3` e `inspected_ratio`: `0,5387`.

Interpretación:

- El tamaño de la red parece acompañar el crecimiento del volumen registrado.
- La longitud inspeccionada también crece en general, pero la muestra es muy corta (`6` años), así que aquí hay riesgo de sobreinterpretar una tendencia temporal simple.
- Estas variables pueden servir como contexto anual, pero no como verdad fuerte para inferencia causal.

## Variables que sí parecen correlacionables

### Núcleo fuerte

- `registered_m3` trimestral.
- `billed_m3` trimestral o mensual agregado.
- `billed_mean`.
- `billed_zero_share`.
- `records`.
- `PERIODICIDAD`.
- `DIAS LECTURA`.

### Contexto útil pero más débil

- `network_km`.
- `inspected_km`.
- `inspected_ratio`.
- `planned_gap_days`.

### Metadatos semánticos útiles solo como contexto

- Cobertura temporal del dataset.
- Frecuencia declarada.
- Tema y licencia.
- Recurso de distribución.

Estos últimos sirven para catalogación, trazabilidad o enriquecimiento del pipeline, no para correlación estadística directa.

## Propuesta de red neuronal para extracción de correlaciones y generación sintética

## ¿Podría ser un VAE?

Sí, pero no un VAE genérico sin adaptar. Para este caso encaja mejor un **VAE tabular condicional**, idealmente un **TVAE** o un **Conditional VAE** para datos mixtos.

Motivos:

- Los datos son tabulares, no imágenes ni series largas puras.
- Hay mezcla de variables continuas, discretas, categóricas y temporales derivadas.
- Queremos aprender dependencias entre variables y después muestrear nuevas observaciones sintéticas coherentes.
- Podemos condicionar la generación por `trimestre`, `mes`, `periodicidad`, `registered_m3` agregado y contexto anual de red.

## Arquitectura recomendada

### Nivel de modelado

Usaría dos niveles:

1. Modelo agregador temporal.
   Genera o predice señales agregadas mensuales/trimestrales:
   - `registered_m3`
   - `billed_m3`
   - `billed_zero_share`
   - `records`
   - `monthly_share`
   - `days_mean`

2. Modelo micro-tabular.
   Genera filas sintéticas de facturación condicionadas por el estado agregado del periodo:
   - `PERIODICIDAD`
   - `DIAS LECTURA`
   - `planned_gap_days`
   - `M3 A FACTURAR`
   - banderas derivadas como `is_zero`
   - calendario: `month`, `quarter`

### Entrada sugerida al encoder

- Variables continuas normalizadas:
  - `M3 A FACTURAR`
  - `DIAS LECTURA`
  - `planned_gap_days`
  - `registered_m3_period`
  - `network_km`
  - `inspected_km`
  - `inspected_ratio`
- Variables categóricas:
  - `PERIODICIDAD`
  - `month`
  - `quarter`
- Variables binarias derivadas:
  - `is_zero`
  - `is_monthly`

### Salidas del decoder

- Reconstrucción de variables continuas con pérdidas gaussianas o log-normales en las muy sesgadas.
- Reconstrucción de categóricas con softmax.
- Restricciones o postproceso para:
  - `M3 A FACTURAR >= 0`
  - coherencia entre `PERIODICIDAD` y `DIAS LECTURA`
  - mantenimiento aproximado de la tasa de ceros por periodo

## Esquema concreto de modelo

### Opción A: Conditional TVAE

La opción más equilibrada.

- Encoder MLP:
  - Entrada tabular embebida.
  - Capas: `256 -> 128 -> 64`.
- Espacio latente:
  - `z_dim = 16` o `32`.
- Decoder MLP:
  - `64 -> 128 -> 256`.
- Condiciones:
  - `quarter`, `month`, `PERIODICIDAD`, `registered_m3_period`, `network_km`, `inspected_ratio`.

Ventajas:

- Muy adecuado para tablas mixtas.
- Más estable que un GAN en datasets tabulares con muchas repeticiones y categorías dominantes.
- Permite controlar la generación por condiciones externas.

### Opción B: VAE jerárquico temporal + tabular

Más potente si queréis realismo a nivel calendario.

- Primer VAE o pequeño modelo secuencial para generar estados mensuales/trimestrales.
- Segundo VAE tabular condicionado al estado generado.

Ventajas:

- Separa dinámica temporal de generación fila a fila.
- Produce sintéticos más coherentes a nivel macro y micro.

Inconveniente:

- Más coste de entrenamiento y validación.

## Preprocesado recomendado

Antes de entrenar:

- Parsear fechas y derivar:
  - `year`
  - `month`
  - `quarter`
  - `planned_gap_days`
- Crear:
  - `is_zero = (M3 A FACTURAR == 0)`
  - `log_m3 = log1p(M3 A FACTURAR)` para suavizar sesgo
- Estandarizar numéricas.
- One-hot o embeddings para categóricas.
- Tratar los `80` vacíos de `PERIODICIDAD`.
- Incluir pesos o muestreo estratificado para no distorsionar la minoría mensual.

## Cómo validaría los sintéticos

- Comparar distribuciones marginales por variable.
- Comparar correlaciones reales vs sintéticas.
- Comparar:
  - tasa de ceros
  - medias y medianas por mes/trimestre
  - proporción mensual/trimestral
  - ratio `facturado / registrado`
- Medir si los sintéticos conservan el patrón de pico en Q3 y descenso en Q4.
- Revisar privacidad:
  - distancia a vecinos más cercanos
  - memorization check
  - filtrado de duplicados casi exactos

## Recomendación final

Sí, **un VAE puede funcionar**, pero mi recomendación no sería un VAE simple. Iría a:

- **Primera opción**: `Conditional TVAE`.
- **Segunda opción**: `CVAE` tabular con dos niveles, macro y micro.

No confiaría solo en los RDF para la parte generativa. Los usaría como metadatos de gobierno del dato y no como fuente principal de señal.

La hipótesis central a explotar en el modelo es esta:

- La estacionalidad trimestral del agua registrada condiciona el volumen facturable.
- La intensidad de facturación condiciona inversamente la tasa de ceros.
- La periodicidad de lectura explica parte de la duración del ciclo y parte de la forma de la distribución de consumo.
