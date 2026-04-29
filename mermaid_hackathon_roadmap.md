# Diagramas Mermaid para el hackathon

## 1. Flujo actual del pipeline de datos

```mermaid
flowchart TD
    A["Datos reales en /Hackathon-Aguas2026/reales"] --> B["CSV 1: Agua registrada trimestral"]
    A --> C["CSV 2: Longitud de red e inspeccion"]
    A --> D["CSV 3: Facturacion fila a fila"]
    A --> E["RDF: metadatos semanticos"]

    B --> F["Preparacion de datos"]
    C --> F
    D --> F
    E --> G["Contexto semantico y documentacion"]

    F --> H["Limpieza y normalizacion"]
    H --> I["Features temporales: ano, mes, trimestre"]
    H --> J["Features operativas: dias lectura, gap previsto-real, ceros"]
    H --> K["Features agregadas: consumo mensual/trimestral, ratio de ceros"]
    H --> L["Cruce con contexto de red: km red, km inspeccionados, ratio"]

    I --> M["Dataset enriquecido para modelado"]
    J --> M
    K --> M
    L --> M

    M --> N["CVAE tabular inicial"]
    N --> O["Generacion sintetica"]
    O --> P["Evaluacion rapida: medias, dispersion, correlaciones"]
```

## 2. Arquitectura objetivo con STGCN

```mermaid
flowchart TD
    A["Fuentes de datos"] --> B["Series temporales por zona o nodo"]
    B --> C["Construccion del grafo"]
    C --> D["Matriz de adyacencia"]

    A --> E["Variables objetivo"]
    E --> F["Consumo"]
    E --> G["Averias"]
    E --> H["Caudal"]

    A --> I["Variables exogenas"]
    I --> J["Calendario"]
    I --> K["Meteorologia o lluvia"]
    I --> L["Eventos o incidencias"]
    I --> M["Caracteristicas de red"]

    D --> N["STGCN"]
    F --> N
    G --> N
    H --> N
    J --> N
    K --> N
    L --> N
    M --> N

    N --> O["Prediccion futura por zona y tiempo"]
    O --> P["Dashboard"]
    P --> Q["Mapa por zonas"]
    P --> R["Series historicas y prediccion"]
    P --> S["Simulacion de escenarios"]
    P --> T["Alertas o anomalias"]
```

## 3. Plan recomendado del hackathon

```mermaid
flowchart LR
    A["Fase 1: MVP de datos"] --> B["Unificar datos en tabla maestra por zona y fecha"]
    B --> C["Fase 2: Dashboard visual"]
    C --> D["Fase 3: Baseline predictivo"]
    D --> E["Fase 4: STGCN si hay grafo suficiente"]
```

## 4. Estructura funcional del dashboard

```mermaid
flowchart TD
    A["Dashboard principal"] --> B["Panel 1: Historico"]
    A --> C["Panel 2: Prediccion"]
    A --> D["Panel 3: Simulacion"]
    A --> E["Panel 4: Mapa"]

    B --> B1["Serie temporal de consumo"]
    B --> B2["Serie temporal de caudal"]
    B --> B3["Incidencias o averias"]

    C --> C1["Prediccion proximos dias o semanas"]
    C --> C2["Bandas de incertidumbre"]
    C --> C3["Comparativa real vs predicho"]

    D --> D1["Escenario de alta demanda"]
    D --> D2["Escenario meteorologico"]
    D --> D3["Escenario de averia o corte"]

    E --> E1["Mapa por zonas"]
    E --> E2["Heatmap de consumo"]
    E --> E3["Alertas por zona"]
```

## 5. Reparto rapido de equipo

```mermaid
flowchart TD
    A["Equipo hackathon"] --> B["Persona 1: limpieza y tabla maestra"]
    A --> C["Persona 2: grafo y STGCN"]
    A --> D["Persona 3: baseline predictivo"]
    A --> E["Persona 4: dashboard y visualizacion"]
    A --> F["Persona 5: storytelling, metricas y demo"]
```
