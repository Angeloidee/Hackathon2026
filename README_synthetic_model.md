# Pipeline sintético con CVAE tabular

Este proyecto incluye un primer generador sintético para los datos de `Hackathon-Aguas2026\reales`, implementado sin dependencias de deep learning externas, usando `numpy`, `pandas` y un `Conditional VAE` tabular ligero.

## Archivo principal

- `C:\Users\xngel\Desktop\ProyectosCodex\Hackathon-Aguas2026\synthetic_cvae_pipeline.py`

## Qué hace

1. Prepara un dataset correlacionable a nivel fila a partir del CSV masivo de facturación.
2. Enriquecer cada fila con contexto trimestral y anual:
   - agua registrada trimestral
   - longitud de red
   - km inspeccionados
   - ratio de inspección
   - agregados mensuales y trimestrales
3. Entrena un `CVAE` tabular para modelar:
   - `m3_to_bill`
   - `days_reading`
   - `planned_gap_days`
   - `is_zero`
   - días del calendario asociados
4. Genera filas sintéticas condicionadas por contextos reales muestreados.

## Comandos

Preparar el dataset:

```powershell
python .\Hackathon-Aguas2026\synthetic_cvae_pipeline.py prepare --max-rows 50000
```

Entrenar y generar una preview sintética:

```powershell
python .\Hackathon-Aguas2026\synthetic_cvae_pipeline.py train --max-rows 50000 --epochs 35 --batch-size 256
```

Generar un CSV sintético nuevo a partir del modelo entrenado:

```powershell
python .\Hackathon-Aguas2026\synthetic_cvae_pipeline.py generate --num-rows 10000 --output-name synthetic_generated.csv
```

## Salidas

Se escriben en:

- `C:\Users\xngel\Desktop\ProyectosCodex\Hackathon-Aguas2026\synthetic_outputs`

Archivos principales:

- `prepared_training_data.csv`: dataset enriquecido listo para entrenamiento
- `prepared_summary.json`: resumen de muestreo
- `synthetic_preview.csv`: muestra sintética generada tras entrenar
- `evaluation.md`: comparación rápida real vs sintético
- `model\weights.npz`: pesos del modelo
- `model\bundle_metadata.json`: metadatos de escalado y categorías
- `model\train_history.json`: historial de entrenamiento

## Lectura de la calidad actual

Esta primera versión ya conserva razonablemente:

- la tasa global de ceros
- parte de la relación inversa entre consumo y ceros
- el contexto temporal y operativo del periodo

Todavía mejora poco:

- la correlación entre `m3_to_bill` y `days_reading`
- la dispersión completa de `days_reading`
- el realismo fino de la cola alta del consumo

## Siguiente iteración recomendada

Si queréis subir nivel para el hackathon, el siguiente paso natural sería:

1. Separar un modelo macro temporal y otro micro tabular.
2. Añadir embeddings categóricos y pérdidas diferenciadas por variable.
3. Sobremuestrear el segmento `MENSUAL`.
4. Evaluar privacidad y memorization con nearest-neighbor checks.
