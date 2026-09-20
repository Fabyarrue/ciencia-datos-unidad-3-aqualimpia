"""Funciones reutilizables para el análisis de AquaLimpia."""

from pathlib import Path
import pandas as pd
import joblib


COLUMNAS_REQUERIDAS = {
    "fecha_registro",
    "planta",
    "caudal_entrada_m3_d",
    "DBO_entrada_mg_L",
    "energia_aeracion_kWh",
    "lodos_generados_kg_d",
    "DBO_salida_mg_L",
    "cumplimiento_norma",
}


def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Valida las columnas principales y crea variables derivadas.

    Parameters
    ----------
    df:
        Dataset original de AquaLimpia.

    Returns
    -------
    pd.DataFrame
        Copia preparada con fechas convertidas, eficiencia de remoción
        y generación específica de lodos.
    """
    columnas_faltantes = sorted(
        COLUMNAS_REQUERIDAS.difference(df.columns)
    )

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas requeridas: "
            + ", ".join(columnas_faltantes)
        )

    datos = df.copy()

    datos["fecha_registro"] = pd.to_datetime(
        datos["fecha_registro"],
        errors="coerce"
    )

    fechas_invalidas = datos["fecha_registro"].isna().sum()

    if fechas_invalidas > 0:
        raise ValueError(
            f"Se encontraron {fechas_invalidas} fechas inválidas."
        )

    if (datos["DBO_entrada_mg_L"] <= 0).any():
        raise ValueError(
            "La DBO de entrada debe ser mayor que cero."
        )

    if (datos["caudal_entrada_m3_d"] <= 0).any():
        raise ValueError(
            "El caudal de entrada debe ser mayor que cero."
        )

    datos["eficiencia_remocion_DBO_pct"] = (
        (
            datos["DBO_entrada_mg_L"]
            - datos["DBO_salida_mg_L"]
        )
        / datos["DBO_entrada_mg_L"]
        * 100
    )

    datos["lodos_especificos_kg_m3"] = (
        datos["lodos_generados_kg_d"]
        / datos["caudal_entrada_m3_d"]
    )

    if not datos[
        "eficiencia_remocion_DBO_pct"
    ].between(0, 100).all():
        raise ValueError(
            "Se detectaron eficiencias fuera del rango "
            "de 0 % a 100 %."
        )

    return datos

def crear_reporte_operaciones(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Construye el reporte destinado al equipo de Operaciones.
    """
    datos = preparar_datos(df)

    columnas_operaciones = [
        "fecha_registro",
        "planta",
        "caudal_entrada_m3_d",
        "DBO_entrada_mg_L",
        "DBO_salida_mg_L",
        "eficiencia_remocion_DBO_pct",
        "energia_aeracion_kWh",
        "lodos_generados_kg_d",
        "lodos_especificos_kg_m3"
    ]

    reporte = (
        datos[columnas_operaciones]
        .sort_values(
            ["fecha_registro", "planta"]
        )
        .reset_index(drop=True)
    )

    return reporte


def crear_reporte_gestion_ambiental(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Construye el reporte destinado a Gestión Ambiental.
    """
    datos = preparar_datos(df)

    reporte = datos[
        [
            "fecha_registro",
            "planta",
            "DBO_salida_mg_L",
            "cumplimiento_norma"
        ]
    ].copy()

    reporte["cumplimiento_registrado"] = (
        reporte["cumplimiento_norma"]
        .map({
            0: "Incumplimiento registrado",
            1: "Cumplimiento registrado"
        })
    )

    reporte = (
        reporte
        .sort_values(
            ["fecha_registro", "planta"]
        )
        .reset_index(drop=True)
    )

    return reporte

def guardar_reportes_excel(
    df: pd.DataFrame,
    carpeta_salida: str | Path
) -> dict[str, Path]:
    """
    Genera y guarda los reportes de Operaciones y Gestión Ambiental.
    """
    destino = Path(carpeta_salida)
    destino.mkdir(
        parents=True,
        exist_ok=True
    )

    reporte_operaciones = (
        crear_reporte_operaciones(df)
    )

    reporte_gestion_ambiental = (
        crear_reporte_gestion_ambiental(df)
    )

    rutas = {
        "operaciones":
            destino / "reporte_operaciones.xlsx",
        "gestion_ambiental":
            destino / "reporte_gestion_ambiental.xlsx"
    }

    reporte_operaciones.to_excel(
        rutas["operaciones"],
        index=False,
        engine="openpyxl"
    )

    reporte_gestion_ambiental.to_excel(
        rutas["gestion_ambiental"],
        index=False,
        engine="openpyxl"
    )

    return rutas

def crear_resumen_resultados(
    df: pd.DataFrame
) -> dict:
    """
    Construye un resumen reutilizable de los resultados principales.
    """
    datos = preparar_datos(df)

    resumen_por_planta = (
        datos.groupby(
            "planta",
            as_index=False
        )
        .agg(
            registros=(
                "planta",
                "size"
            ),
            DBO_salida_promedio_mg_L=(
                "DBO_salida_mg_L",
                "mean"
            ),
            eficiencia_promedio_pct=(
                "eficiencia_remocion_DBO_pct",
                "mean"
            ),
            eficiencia_mediana_pct=(
                "eficiencia_remocion_DBO_pct",
                "median"
            ),
            cumplimiento_registrado_pct=(
                "cumplimiento_norma",
                lambda serie: serie.mean() * 100
            )
        )
    )

    return {
        "cantidad_registros": len(datos),
        "cantidad_plantas": datos["planta"].nunique(),
        "fecha_inicial": datos["fecha_registro"].min(),
        "fecha_final": datos["fecha_registro"].max(),
        "resumen_por_planta": resumen_por_planta
    }


def guardar_resumen_joblib(
    df: pd.DataFrame,
    ruta_salida: str | Path
) -> Path:
    """
    Guarda el resumen de resultados en un archivo Joblib.
    """
    ruta = Path(ruta_salida)

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    resumen = crear_resumen_resultados(df)

    joblib.dump(
        resumen,
        ruta
    )

    return ruta


def cargar_resumen_joblib(
    ruta_entrada: str | Path
) -> dict:
    """
    Recupera un resumen previamente guardado con Joblib.
    """
    ruta = Path(ruta_entrada)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta}"
        )

    return joblib.load(ruta)