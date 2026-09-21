"""Ejecuta el flujo principal de resultados de AquaLimpia."""

from pathlib import Path

import pandas as pd

from funciones_analisis import (
    guardar_reportes_excel,
    guardar_resumen_joblib,
    preparar_datos,
)


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]

RUTA_DATOS = (
    RAIZ_PROYECTO
    / "datos"
    / "dataset_set_A_aguas_residuales.xlsx"
)

RUTA_RESULTADOS = (
    RAIZ_PROYECTO
    / "resultados"
)


def main() -> None:
    """
    Valida el dataset y genera los reportes y el resumen Joblib.
    """
    if not RUTA_DATOS.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {RUTA_DATOS}"
        )

    datos_originales = pd.read_excel(
        RUTA_DATOS
    )

    datos_preparados = preparar_datos(
        datos_originales
    )

    rutas_reportes = guardar_reportes_excel(
        datos_preparados,
        RUTA_RESULTADOS
    )

    ruta_joblib = guardar_resumen_joblib(
        datos_preparados,
        RUTA_RESULTADOS
        / "resumen_resultados.joblib"
    )

    print(
        "Proceso completado correctamente."
    )

    print(
        "Registros procesados:",
        len(datos_preparados)
    )

    for nombre, ruta in rutas_reportes.items():
        print(
            f"{nombre}: "
            f"{ruta.relative_to(RAIZ_PROYECTO)}"
        )

    print(
        "resumen_joblib:",
        ruta_joblib.relative_to(
            RAIZ_PROYECTO
        )
    )


if __name__ == "__main__":
    main()