# Resultados del proyecto

Esta carpeta contiene las salidas generadas mediante la ejecución reproducible del notebook y las funciones externas del proyecto.

## Archivos generados

- `dashboard_aqualimpia.html`: dashboard exploratorio interactivo con comparaciones operacionales y ambientales. El archivo incorpora Plotly y puede abrirse sin conexión a internet.
- `reporte_operaciones.xlsx`: detalle destinado a Operaciones con fecha, planta, caudal, DBO de entrada y salida, eficiencia de remoción, energía de aireación y generación de lodos.
- `reporte_gestion_ambiental.xlsx`: detalle destinado a Gestión Ambiental con fecha, planta, DBO de salida y cumplimiento registrado en el dataset.
- `resumen_resultados.joblib`: objeto serializado con el periodo analizado, cantidad de registros, número de plantas y resumen comparativo por instalación.

## Reproducción y uso

Los archivos se generan desde `analisis_aqualimpia.ipynb` mediante funciones definidas en `codigo/funciones_analisis.py`. No deben editarse manualmente. Si cambia el dataset o el análisis, corresponde ejecutar nuevamente el flujo para mantener la coherencia entre código, resultados y documentación.

El archivo Joblib solo debe cargarse desde una fuente confiable, porque los formatos de serialización de objetos pueden ejecutar contenido durante su lectura.