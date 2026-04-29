from __future__ import annotations

import csv
import math
import re
import statistics
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "reales"
OUTPUT_DIR = BASE_DIR / "analisis_reales"


DATE_FORMATS = ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S")
NUMBER_RE = re.compile(r"^[+-]?(?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d+)?$")


@dataclass
class ColumnStats:
    name: str
    non_empty: int = 0
    empty: int = 0
    unique_counter: Counter[str] | None = None
    numeric_values: list[float] | None = None
    date_values: list[datetime] | None = None
    sample_values: list[str] | None = None
    min_length: int | None = None
    max_length: int | None = None

    def __post_init__(self) -> None:
        self.unique_counter = Counter()
        self.numeric_values = []
        self.date_values = []
        self.sample_values = []


def safe_read_text(path: Path) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace"), "unknown"


def detect_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def try_parse_number(raw: str) -> float | None:
    value = raw.strip()
    if not value or not NUMBER_RE.match(value):
        return None
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        parts = value.split(",")
        if len(parts) == 2 and len(parts[1]) in (1, 2, 3):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    return float(value)


def try_parse_date(raw: str) -> datetime | None:
    value = raw.strip()
    if not value:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def format_number(value: float) -> str:
    if math.isfinite(value) and abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):,}".replace(",", ".")
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def md_table(headers: list[str], rows: Iterable[Iterable[str]]) -> str:
    rows = list(rows)
    if not rows:
        return "_Sin filas para mostrar._"
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def month_key_from_period(period: str) -> tuple[int, int] | None:
    match = re.match(r"^\s*(\d{4})\s*-\s*(\d{2})\s*$", period)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def build_csv_specific_sections(path: Path, rows: list[dict[str, str]], headers: list[str]) -> list[str]:
    stem = path.name.lower()
    sections: list[str] = []

    if "agua-registrada-trimestral" in stem:
        yearly = Counter()
        quarterly_rows = []
        values = []
        for row in rows:
            year = int(row["AÑO"])
            quarter = int(row["TRIMESTRE"])
            volume = try_parse_number(row["TOTAL Volumen agua potable registrada (m³)"]) or 0.0
            yearly[year] += volume
            quarterly_rows.append([str(year), str(quarter), format_number(volume)])
            values.append((year, quarter, volume))
        peak = max(values, key=lambda item: item[2])
        low = min(values, key=lambda item: item[2])
        sections.extend(
            [
                "## Lectura analítica específica",
                "",
                "### Totales anuales de agua registrada",
                "",
                md_table(
                    ["Año", "Volumen total (m³)"],
                    [[str(year), format_number(total)] for year, total in sorted(yearly.items())],
                ),
                "",
                f"- Trimestre con mayor volumen: `{peak[0]} T{peak[1]}` con `{format_number(peak[2])}` m³.",
                f"- Trimestre con menor volumen: `{low[0]} T{low[1]}` con `{format_number(low[2])}` m³.",
            ]
        )

    elif "longitud-red-abastecimiento" in stem:
        details = []
        prev_red = None
        for row in rows:
            year = row["AÑO"]
            red = try_parse_number(row["LONGITUD RED ABASTECIMIENTO (km)"]) or 0.0
            inspeccion = try_parse_number(row["LONGITUD RED ABASTECIMIENTO INSPECCIONADA BUSCAFUGAS (km)"]) or 0.0
            ratio = (inspeccion / red * 100) if red else 0.0
            delta = "-" if prev_red is None else format_number(red - prev_red)
            details.append([year, format_number(red), format_number(inspeccion), f"{ratio:.2f}%", delta])
            prev_red = red
        sections.extend(
            [
                "## Lectura analítica específica",
                "",
                "### Evolución anual y esfuerzo de inspección",
                "",
                md_table(
                    ["Año", "Red total (km)", "Red inspeccionada (km)", "% inspeccionado sobre red", "Variación anual red (km)"],
                    details,
                ),
                "",
                "- El porcentaje puede superar el 100% si en el año se inspeccionan tramos repetidos o campañas sobre la misma red.",
            ]
        )

    elif "m3-registrados_facturados" in stem:
        by_period = Counter()
        by_periodicity = Counter()
        zero_count = 0
        positive_count = 0
        planned_gap_counter = Counter()
        factura_by_month = Counter()
        m3_values: list[float] = []
        for row in rows:
            period = row["PERIODO"]
            periodicity = row["PERIODICIDAD"] or "(vacío)"
            m3 = try_parse_number(row["M3 A FACTURAR"]) or 0.0
            by_period[period] += m3
            by_periodicity[periodicity] += 1
            m3_values.append(m3)
            if m3 == 0:
                zero_count += 1
            else:
                positive_count += 1
            lectura = try_parse_date(row["FECHA LECTURA"])
            prevista = try_parse_date(row["FECHA PREVISTA LECTURA"])
            factura = try_parse_date(row["FECHA FACTURA"])
            if lectura and prevista:
                planned_gap_counter[(prevista - lectura).days] += 1
            if factura:
                factura_by_month[(factura.year, factura.month)] += 1

        top_periods = sorted(
            ((month_key_from_period(period), period, total) for period, total in by_period.items()),
            key=lambda item: (item[0] is None, item[0] or (9999, 99)),
        )
        top_periods_rows = [[period, format_number(total)] for _, period, total in top_periods]
        monthly_invoice_rows = [
            [f"{year}-{month:02d}", str(count)]
            for (year, month), count in sorted(factura_by_month.items())
        ]
        sections.extend(
            [
                "## Lectura analítica específica",
                "",
                "### Volumen facturable agregado por periodo",
                "",
                md_table(["Periodo", "Suma M3 a facturar"], top_periods_rows),
                "",
                "### Distribución de periodicidad",
                "",
                md_table(["Periodicidad", "Registros"], [[k, str(v)] for k, v in by_periodicity.most_common()]),
                "",
                "### Fechas de factura por mes",
                "",
                md_table(["Mes de factura", "Número de registros"], monthly_invoice_rows),
                "",
                "### Indicadores operativos",
                "",
                md_table(
                    ["Indicador", "Valor"],
                    [
                        ["Registros con `M3 A FACTURAR = 0`", str(zero_count)],
                        ["Porcentaje de ceros", f"{(zero_count / len(rows)):.2%}" if rows else "0.00%"],
                        ["Registros con consumo positivo", str(positive_count)],
                        ["Consumo máximo individual (m3)", format_number(max(m3_values) if m3_values else 0)],
                        ["Consumo medio individual (m3)", format_number(statistics.fmean(m3_values) if m3_values else 0)],
                        ["Consumo mediano individual (m3)", format_number(statistics.median(m3_values) if m3_values else 0)],
                    ],
                ),
                "",
                "### Diferencia entre fecha leída y fecha prevista",
                "",
                md_table(
                    ["Desfase en días (`prevista - lectura`)", "Frecuencia"],
                    [[str(days), str(count)] for days, count in planned_gap_counter.most_common(10)],
                ),
            ]
        )

    return sections


def summarize_csv(path: Path) -> str:
    raw_text, encoding = safe_read_text(path)
    delimiter = detect_delimiter(raw_text[:8192])
    lines = raw_text.splitlines()
    reader = csv.DictReader(lines, delimiter=delimiter)
    headers = reader.fieldnames or []
    rows_seen = 0
    duplicate_counter = Counter()
    first_rows: list[dict[str, str]] = []
    last_rows: list[dict[str, str]] = []
    columns = {header: ColumnStats(header) for header in headers}

    for row in reader:
        rows_seen += 1
        row_tuple = tuple((row.get(header) or "").strip() for header in headers)
        duplicate_counter[row_tuple] += 1
        if len(first_rows) < 5:
            first_rows.append(row)
        last_rows.append(row)
        if len(last_rows) > 5:
            last_rows.pop(0)

        for header in headers:
            raw = (row.get(header) or "").strip()
            stats = columns[header]
            if not raw:
                stats.empty += 1
                continue
            stats.non_empty += 1
            stats.unique_counter[raw] += 1
            if len(stats.sample_values) < 5 and raw not in stats.sample_values:
                stats.sample_values.append(raw)
            str_len = len(raw)
            stats.min_length = str_len if stats.min_length is None else min(stats.min_length, str_len)
            stats.max_length = str_len if stats.max_length is None else max(stats.max_length, str_len)

            num = try_parse_number(raw)
            if num is not None:
                stats.numeric_values.append(num)

            date_val = try_parse_date(raw)
            if date_val is not None:
                stats.date_values.append(date_val)

    duplicate_rows = sum(count - 1 for count in duplicate_counter.values() if count > 1)
    duplicate_groups = sum(1 for count in duplicate_counter.values() if count > 1)

    inferred_types: dict[str, str] = {}
    observations: list[str] = []
    for header, stats in columns.items():
        if stats.non_empty == 0:
            inferred = "vacía"
        elif len(stats.numeric_values) == stats.non_empty:
            inferred = "numérica"
        elif len(stats.date_values) == stats.non_empty:
            inferred = "fecha"
        elif len(stats.unique_counter) == stats.non_empty:
            inferred = "texto identificador"
        else:
            inferred = "texto categórico"
        inferred_types[header] = inferred

        if "Ã" in header or any("Ã" in v for v in stats.sample_values):
            observations.append(f"Posible problema de codificación detectado en la columna `{header}`.")
        if stats.empty:
            observations.append(
                f"La columna `{header}` tiene {stats.empty} valores vacíos ({stats.empty / rows_seen:.2%} del total)."
            )
        if stats.non_empty and len(stats.unique_counter) == 1:
            observations.append(f"La columna `{header}` es constante: siempre vale `{next(iter(stats.unique_counter))}`.")

    header_rows = []
    for header, stats in columns.items():
        unique_count = len(stats.unique_counter)
        unique_pct = (unique_count / rows_seen) if rows_seen else 0
        header_rows.append([
            header,
            inferred_types[header],
            str(stats.non_empty),
            str(stats.empty),
            str(unique_count),
            f"{unique_pct:.2%}",
            ", ".join(stats.sample_values[:5]) if stats.sample_values else "-",
        ])

    per_column_details = []
    for header, stats in columns.items():
        lines_out = [f"### Columna: `{header}`", ""]
        lines_out.append(f"- Tipo inferido: `{inferred_types[header]}`")
        lines_out.append(f"- No vacíos: `{stats.non_empty}`")
        lines_out.append(f"- Vacíos: `{stats.empty}`")
        lines_out.append(f"- Distintos: `{len(stats.unique_counter)}`")
        if stats.min_length is not None:
            lines_out.append(f"- Longitud mínima/máxima: `{stats.min_length}` / `{stats.max_length}`")
        if stats.unique_counter:
            top_values = stats.unique_counter.most_common(10)
            top_table = md_table(
                ["Valor", "Frecuencia"],
                [[value, str(count)] for value, count in top_values],
            )
            lines_out.extend(["", "Valores más frecuentes:", "", top_table])
        if stats.numeric_values:
            numeric = stats.numeric_values
            lines_out.extend(
                [
                    "",
                    "Estadísticas numéricas:",
                    "",
                    md_table(
                        ["Métrica", "Valor"],
                        [
                            ["Mínimo", format_number(min(numeric))],
                            ["Máximo", format_number(max(numeric))],
                            ["Media", format_number(statistics.fmean(numeric))],
                            ["Mediana", format_number(statistics.median(numeric))],
                            ["Suma", format_number(sum(numeric))],
                        ],
                    ),
                ]
            )
        if stats.date_values:
            date_values = sorted(stats.date_values)
            lines_out.extend(
                [
                    "",
                    "Rango temporal:",
                    "",
                    md_table(
                        ["Métrica", "Valor"],
                        [
                            ["Primera fecha", date_values[0].isoformat()],
                            ["Última fecha", date_values[-1].isoformat()],
                        ],
                    ),
                ]
            )
        per_column_details.append("\n".join(lines_out))

    preview_rows = first_rows if rows_seen <= 10 else first_rows + last_rows
    preview_title = "Vista completa" if rows_seen <= 10 else "Primeras y últimas filas"
    preview_table = md_table(headers, [[row.get(h, "") for h in headers] for row in preview_rows])

    summary_lines = [
        f"# Análisis del archivo `{path.name}`",
        "",
        "## Metadatos básicos",
        "",
        md_table(
            ["Campo", "Valor"],
            [
                ["Ruta", str(path)],
                ["Extensión", path.suffix],
                ["Tamaño (bytes)", str(path.stat().st_size)],
                ["Codificación detectada", encoding],
                ["Delimitador", repr(delimiter)],
                ["Filas de datos", str(rows_seen)],
                ["Columnas", str(len(headers))],
                ["Grupos de filas exactamente idénticas", str(duplicate_groups)],
                ["Filas idénticas adicionales", str(duplicate_rows)],
            ],
        ),
        "",
        "## Estructura del dataset",
        "",
        md_table(
            ["Columna", "Tipo inferido", "No vacíos", "Vacíos", "Distintos", "% distintos", "Muestras"],
            header_rows,
        ),
        "",
        f"## {preview_title}",
        "",
        preview_table,
        "",
        "## Observaciones destacadas",
        "",
    ]
    if observations:
        summary_lines.extend([f"- {obs}" for obs in dict.fromkeys(observations)])
    else:
        summary_lines.append("- No se han detectado incidencias evidentes de completitud o constancia en el escaneo general.")

    summary_lines.extend(["", "## Detalle por columna", ""])
    summary_lines.extend(per_column_details)

    if rows_seen <= 1000000:
        replay_reader = list(csv.DictReader(lines, delimiter=delimiter))
        extra_sections = build_csv_specific_sections(path, replay_reader, headers)
        if extra_sections:
            summary_lines.extend(["", *extra_sections])
    return "\n".join(summary_lines) + "\n"


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def summarize_rdf(path: Path) -> str:
    text, encoding = safe_read_text(path)
    root = ET.fromstring(text)
    namespaces = dict(re.findall(r'xmlns:([A-Za-z0-9_]+)="([^"]+)"', text))

    all_nodes = list(root.iter())
    tag_counter = Counter(local_name(node.tag) for node in all_nodes)
    subjects = []
    triples_like = 0
    dataset_rows: list[list[str]] = []
    nested_rows: list[list[str]] = []
    blank_nodes = 0
    resource_objects = 0
    literal_objects = 0
    observations: list[str] = []

    for child in list(root):
        about = child.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        node_id = child.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID", "")
        subjects.append(about or f"_:{node_id}" if node_id else "(sin identificador)")
        for prop in list(child):
            triples_like += 1
            pred = local_name(prop.tag)
            resource = prop.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource")
            nodeid = prop.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID")
            dtype = prop.attrib.get("{http://www.w3.org/2001/XMLSchema#}datatype", "")
            text_value = (prop.text or "").strip()
            if nodeid:
                blank_nodes += 1
                obj = f"_:{nodeid}"
            elif resource:
                resource_objects += 1
                obj = resource
            elif list(prop):
                children = list(prop)
                obj = f"Contenedor de {len(children)} nodo(s) anidados"
                for nested in children:
                    nested_subject = local_name(prop.tag)
                    nested_predicate = local_name(nested.tag)
                    nested_resource = nested.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource")
                    nested_nodeid = nested.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}nodeID")
                    nested_text = (nested.text or "").strip()
                    nested_object = nested_resource or (f"_:{nested_nodeid}" if nested_nodeid else nested_text or "(vacío)")
                    nested_rows.append([nested_subject, nested_predicate, nested_object])
            else:
                literal_objects += 1
                obj = text_value or "(literal vacío)"
            dataset_rows.append([about or "(sin about)", pred, obj, dtype or "-"])
            if "Ã" in text_value:
                observations.append(f"Posible problema de codificación en el valor literal de `{pred}`.")

    if "<dcat:Dataset" in text and triples_like <= 1:
        observations.append("El RDF parece incompleto o minimalista: solo declara el recurso `dcat:Dataset` sin metadatos descriptivos.")

    summary_lines = [
        f"# Análisis del archivo `{path.name}`",
        "",
        "## Metadatos básicos",
        "",
        md_table(
            ["Campo", "Valor"],
            [
                ["Ruta", str(path)],
                ["Extensión", path.suffix],
                ["Tamaño (bytes)", str(path.stat().st_size)],
                ["Codificación detectada", encoding],
                ["Elemento raíz", local_name(root.tag)],
                ["Elementos XML totales", str(len(all_nodes))],
                ["Sujetos de primer nivel", str(len(list(root)))],
                ["Relaciones directas detectadas", str(triples_like)],
                ["Objetos con `rdf:resource`", str(resource_objects)],
                ["Referencias a nodos en blanco", str(blank_nodes)],
                ["Literales simples", str(literal_objects)],
            ],
        ),
        "",
        "## Namespaces declarados",
        "",
        md_table(["Prefijo", "URI"], [[k, v] for k, v in namespaces.items()]) if namespaces else "_No se detectaron namespaces._",
        "",
        "## Etiquetas presentes",
        "",
        md_table(["Etiqueta", "Frecuencia"], [[tag, str(count)] for tag, count in tag_counter.most_common()]),
        "",
        "## Sujetos de nivel superior",
        "",
        md_table(["Sujeto"], [[s] for s in subjects]) if subjects else "_No hay sujetos de primer nivel._",
        "",
        "## Relaciones detectadas",
        "",
        md_table(["Sujeto", "Predicado", "Objeto", "Datatype"], dataset_rows[:50]) if dataset_rows else "_No se han detectado relaciones._",
        "",
        "## Nodos anidados relevantes",
        "",
        md_table(["Contenedor", "Predicado interno", "Valor"], nested_rows[:50]) if nested_rows else "_No hay nodos anidados de interés._",
        "",
        "## Observaciones destacadas",
        "",
    ]
    if observations:
        summary_lines.extend([f"- {obs}" for obs in dict.fromkeys(observations)])
    else:
        summary_lines.append("- El RDF es sintácticamente válido y no presenta incidencias obvias en esta inspección estructural.")

    return "\n".join(summary_lines) + "\n"


def build_output_name(path: Path) -> Path:
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem)
    return OUTPUT_DIR / f"{safe_stem}.md"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.suffix.lower() == ".csv":
            content = summarize_csv(path)
        elif path.suffix.lower() == ".rdf":
            content = summarize_rdf(path)
        else:
            continue
        output_path = build_output_name(path)
        output_path.write_text(content, encoding="utf-8")
        generated.append(output_path)

    index_lines = [
        "# Índice de análisis",
        "",
        "Se han generado los siguientes informes individuales:",
        "",
    ]
    for report in generated:
        index_lines.append(f"- `{report.name}`")
    (OUTPUT_DIR / "README.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
