"""Funciones reutilizables para el análisis de AquaLimpia."""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from scipy.stats import pearsonr, spearmanr


COLUMNAS_REQUERIDAS = {
    "fecha_registro",
    "planta",
    "caudal_entrada_m3_d",
    "DBO_entrada_mg_L",
    "SST_entrada_mg_L",
    "pH_entrada",
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

def calcular_correlaciones_por_planta(
    df: pd.DataFrame,
    variable_x: str,
    variable_y: str
) -> pd.DataFrame:
    """
    Calcula correlaciones de Pearson y Spearman por planta.

    Parameters
    ----------
    df:
        Dataset original de AquaLimpia.
    variable_x:
        Nombre de la primera variable numérica.
    variable_y:
        Nombre de la segunda variable numérica.

    Returns
    -------
    pd.DataFrame
        Tabla con el número de observaciones, los coeficientes
        de correlación y sus valores p para cada planta.
    """
    datos = preparar_datos(df)

    variables_faltantes = [
        variable
        for variable in [variable_x, variable_y]
        if variable not in datos.columns
    ]

    if variables_faltantes:
        raise ValueError(
            "No se encontraron las variables: "
            + ", ".join(variables_faltantes)
        )

    resultados = []

    for planta, grupo in datos.groupby("planta"):
        pares_validos = grupo[
            [variable_x, variable_y]
        ].dropna()

        if len(pares_validos) < 2:
            raise ValueError(
                f"La planta {planta} no tiene suficientes "
                "observaciones válidas."
            )

        if (
            pares_validos[variable_x].nunique() < 2
            or pares_validos[variable_y].nunique() < 2
        ):
            raise ValueError(
                f"La planta {planta} presenta una variable "
                "sin variación."
            )

        resultado_pearson = pearsonr(
            pares_validos[variable_x],
            pares_validos[variable_y]
        )

        resultado_spearman = spearmanr(
            pares_validos[variable_x],
            pares_validos[variable_y]
        )

        resultados.append({
            "planta": planta,
            "observaciones": len(pares_validos),
            "pearson": resultado_pearson.statistic,
            "pearson_valor_p": resultado_pearson.pvalue,
            "spearman": resultado_spearman.statistic,
            "spearman_valor_p": resultado_spearman.pvalue
        })

    return pd.DataFrame(resultados)

def detectar_candidatos_atipicos_iqr(
    df: pd.DataFrame,
    columnas: list[str],
    agrupar_por: str | None = "planta"
) -> dict[str, pd.DataFrame]:
    """
    Detecta candidatos atípicos mediante el rango intercuartílico.

    Parameters
    ----------
    df:
        Dataset original de AquaLimpia.
    columnas:
        Variables numéricas que se deben evaluar.
    agrupar_por:
        Columna utilizada para calcular límites independientes.
        Por defecto, los límites se calculan por planta. Si se
        utiliza None, el cálculo se realiza sobre todo el dataset.

    Returns
    -------
    dict[str, pd.DataFrame]
        Resumen de límites IQR y registros identificados como
        candidatos atípicos.
    """
    datos = preparar_datos(df)

    columnas_revision = columnas.copy()

    if agrupar_por is not None:
        columnas_revision.append(agrupar_por)

    columnas_faltantes = [
        columna
        for columna in columnas_revision
        if columna not in datos.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "No se encontraron las columnas: "
            + ", ".join(columnas_faltantes)
        )

    for columna in columnas:
        if not pd.api.types.is_numeric_dtype(datos[columna]):
            raise TypeError(
                f"La columna {columna} debe ser numérica."
            )

    if agrupar_por is None:
        grupos = [("Conjunto total", datos)]
    else:
        grupos = datos.groupby(
            agrupar_por,
            sort=True
        )

    resumen = []
    candidatos = []

    for nombre_grupo, grupo in grupos:
        for columna in columnas:
            serie = grupo[columna].dropna()

            if serie.empty:
                raise ValueError(
                    f"La columna {columna} no contiene valores "
                    f"válidos en el grupo {nombre_grupo}."
                )

            q1, q3 = np.percentile(
                serie,
                [25, 75]
            )

            rango_intercuartil = q3 - q1
            limite_inferior = (
                q1 - 1.5 * rango_intercuartil
            )
            limite_superior = (
                q3 + 1.5 * rango_intercuartil
            )

            mascara = (
                (grupo[columna] < limite_inferior)
                | (grupo[columna] > limite_superior)
            )

            registros_columna = grupo.loc[
                mascara
            ].copy()

            registros_columna["grupo_analisis"] = (
                nombre_grupo
            )
            registros_columna["variable"] = columna
            registros_columna["valor"] = (
                registros_columna[columna]
            )
            registros_columna["limite_inferior"] = (
                limite_inferior
            )
            registros_columna["limite_superior"] = (
                limite_superior
            )

            resumen.append({
                "grupo_analisis": nombre_grupo,
                "variable": columna,
                "q1": q1,
                "q3": q3,
                "rango_intercuartil": rango_intercuartil,
                "limite_inferior": limite_inferior,
                "limite_superior": limite_superior,
                "cantidad_candidatos": int(mascara.sum())
            })

            if not registros_columna.empty:
                candidatos.append(
                    registros_columna
                )

    columnas_candidatos = list(datos.columns) + [
        "grupo_analisis",
        "variable",
        "valor",
        "limite_inferior",
        "limite_superior"
    ]

    candidatos_df = (
        pd.concat(
            candidatos,
            ignore_index=True
        )
        if candidatos
        else pd.DataFrame(
            columns=columnas_candidatos
        )
    )

    return {
        "resumen": pd.DataFrame(resumen),
        "candidatos": candidatos_df
    }

def auditar_calidad_datos(
    df: pd.DataFrame,
    columnas_numericas: list[str] | None = None
) -> dict[str, pd.DataFrame]:
    """
    Audita integridad, consistencia y valores extremos del dataset.

    Parameters
    ----------
    df:
        Dataset original de AquaLimpia.
    columnas_numericas:
        Variables numéricas que se evaluarán mediante el método IQR.
        Si no se indican, se utilizan las variables operacionales
        originales del dataset.

    Returns
    -------
    dict[str, pd.DataFrame]
        Tablas con el resumen general, valores nulos, controles de
        consistencia, límites IQR y candidatos atípicos.
    """
    datos = preparar_datos(df)

    if columnas_numericas is None:
        columnas_numericas = [
            "caudal_entrada_m3_d",
            "DBO_entrada_mg_L",
            "SST_entrada_mg_L",
            "pH_entrada",
            "energia_aeracion_kWh",
            "lodos_generados_kg_d",
            "DBO_salida_mg_L"
        ]

    resultado_atipicos = detectar_candidatos_atipicos_iqr(
        datos,
        columnas_numericas
    )

    cantidad_dias_periodo = (
        datos["fecha_registro"].max()
        - datos["fecha_registro"].min()
    ).days + 1

    registros_por_fecha_planta = (
        datos.groupby(
            ["fecha_registro", "planta"]
        )
        .size()
        .reset_index(name="cantidad_registros")
    )

    combinaciones_repetidas = (
        registros_por_fecha_planta[
            registros_por_fecha_planta[
                "cantidad_registros"
            ] > 1
        ]
        .copy()
    )

    registros_adicionales = int(
        (
            combinaciones_repetidas[
                "cantidad_registros"
            ] - 1
        ).sum()
    )

    resumen_general = pd.DataFrame({
        "indicador": [
            "cantidad_filas",
            "cantidad_columnas_originales",
            "cantidad_columnas_preparadas",
            "filas_duplicadas",
            "combinaciones_fecha_planta_repetidas",
            "max_registros_misma_fecha_planta",
            "registros_adicionales_en_combinaciones",
            "fecha_inicial",
            "fecha_final",
            "dias_del_periodo",
            "fechas_con_registros",
            "cantidad_plantas"
        ],
        "valor": [
            len(datos),
            len(df.columns),
            len(datos.columns),
            int(datos.duplicated().sum()),
            len(combinaciones_repetidas),
            int(
                registros_por_fecha_planta[
                    "cantidad_registros"
                ].max()
            ),
            registros_adicionales,
            datos["fecha_registro"].min(),
            datos["fecha_registro"].max(),
            cantidad_dias_periodo,
            datos["fecha_registro"].nunique(),
            datos["planta"].nunique()
        ]
    })

    nulos_por_columna = (
        datos.isna()
        .sum()
        .rename("cantidad_nulos")
        .reset_index()
        .rename(columns={"index": "columna"})
    )

    controles_consistencia = pd.DataFrame({
        "control": [
            "caudal no positivo",
            "DBO de entrada no positiva",
            "SST de entrada no positivo",
            "pH fuera del rango físico de 0 a 14",
            "DBO de salida negativa",
            "energía de aireación negativa",
            "lodos generados negativos",
            "DBO de salida mayor que DBO de entrada",
            "cumplimiento fuera de 0 y 1"
        ],
        "cantidad_registros": [
            int((datos["caudal_entrada_m3_d"] <= 0).sum()),
            int((datos["DBO_entrada_mg_L"] <= 0).sum()),
            int((datos["SST_entrada_mg_L"] <= 0).sum()),
            int(
                (
                    ~datos["pH_entrada"].between(0, 14)
                ).sum()
            ),
            int((datos["DBO_salida_mg_L"] < 0).sum()),
            int((datos["energia_aeracion_kWh"] < 0).sum()),
            int((datos["lodos_generados_kg_d"] < 0).sum()),
            int(
                (
                    datos["DBO_salida_mg_L"]
                    > datos["DBO_entrada_mg_L"]
                ).sum()
            ),
            int(
                (
                    ~datos["cumplimiento_norma"].isin([0, 1])
                ).sum()
            )
        ]
    })

    return {
        "resumen_general": resumen_general,
        "nulos_por_columna": nulos_por_columna,
        "controles_consistencia": controles_consistencia,
        "combinaciones_fecha_planta_repetidas":
            combinaciones_repetidas,
        "resumen_atipicos":
            resultado_atipicos["resumen"],
        "candidatos_atipicos":
            resultado_atipicos["candidatos"]
    }

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
            caudal_promedio_m3_d=(
                "caudal_entrada_m3_d",
                "mean"
            ),
            DBO_salida_promedio_mg_L=(
                "DBO_salida_mg_L",
                "mean"
            ),
            DBO_salida_mediana_mg_L=(
                "DBO_salida_mg_L",
                "median"
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
            ),
            lodos_especificos_mediana_kg_m3=(
                "lodos_especificos_kg_m3",
                "median"
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