# Resultados del proyecto

Esta carpeta contiene los productos obtenidos mediante la ejecución reproducible del proyecto y las capturas utilizadas en el informe académico.

## Archivos disponibles

- `dashboard_aqualimpia.html`: dashboard exploratorio interactivo con comparaciones operacionales y ambientales. El archivo incorpora Plotly y puede abrirse sin conexión a internet.
- `P1_Figura_1_dashboard_exploratorio_aqualimpia.png`: vista estática del dashboard utilizada en el informe académico y en el README principal.
- `P3_Figura_2_documentacion_tecnica_readme_aqualimpia.png`: captura de los objetivos y las preguntas de investigación documentados en el README principal.
- `P3_Figura_3_metodologia_resultados_readme_aqualimpia.png`: captura de la metodología y los resultados principales documentados en el README principal.
- `P6_Figura_4_repositorio_github_aqualimpia.png`: captura de la estructura del repositorio en GitHub utilizada en el informe académico.
- `reporte_operaciones.xlsx`: detalle destinado a Operaciones con fecha, planta, caudal, DBO de entrada y salida, eficiencia de remoción, energía de aireación y generación de lodos.
- `reporte_gestion_ambiental.xlsx`: detalle destinado a Gestión Ambiental con fecha, planta, DBO de salida y cumplimiento registrado en el dataset.
- `resumen_resultados.joblib`: objeto serializado con el periodo analizado, cantidad de registros, número de plantas y resumen comparativo por instalación.

## Reproducción y uso

El dashboard HTML se genera desde `analisis_aqualimpia.ipynb`. Los reportes Excel y el resumen Joblib pueden regenerarse desde el notebook o mediante `codigo/ejecutar_analisis.py`, utilizando las funciones definidas en `codigo/funciones_analisis.py`. Estos productos no deben editarse manualmente.

Las capturas PNG se obtienen manualmente a partir del dashboard, del README renderizado y de la página del repositorio en GitHub. Si cambia el análisis o la documentación representada, corresponde actualizar las capturas para mantener la coherencia con el informe académico.

El archivo Joblib solo debe cargarse desde una fuente confiable, porque los formatos de serialización de objetos pueden ejecutar contenido durante su lectura.
