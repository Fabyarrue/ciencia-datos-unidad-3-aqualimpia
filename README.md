# Proyecto analítico AquaLimpia

Proyecto correspondiente a la Unidad 3 de la asignatura Ciencia de Datos.

## Descripción

Este proyecto desarrolla un análisis reproducible de los datos operacionales y ambientales proporcionados para el caso AquaLimpia S. A. El flujo utiliza Python para validar la estructura y calidad del dataset, construir indicadores derivados, comparar el comportamiento observado de las plantas y generar productos diferenciados para Operaciones y Gestión Ambiental.

La entrega fue elaborada individualmente. Git y GitHub se utilizan para mantener trazabilidad, control de versiones, revisión de cambios y una estructura preparada para colaboración futura.

## Objetivo

Describir y comparar el desempeño operacional y ambiental observado de las plantas de AquaLimpia S. A., mediante el análisis reproducible de las variables disponibles, con el propósito de identificar diferencias, asociaciones, patrones temporales y registros que requieran revisión.

## Preguntas de investigación

1. ¿Qué diferencias presentan las plantas en la eficiencia de remoción de demanda biológica de oxígeno (DBO), la DBO de salida, la generación específica de lodos y el cumplimiento registrado?
2. ¿Qué relación se observa entre la DBO de entrada y la DBO de salida, y entre el caudal de entrada y la DBO de salida?
3. ¿Qué asociación existe entre el caudal de entrada y la energía de aireación en cada planta?
4. ¿Qué patrones temporales, candidatos atípicos y limitaciones de calidad deben considerarse antes de utilizar los resultados para apoyar decisiones?

## Alcance

No se desarrolla una solución predictiva orientada a anticipar riesgos regulatorios, porque `cumplimiento_norma` no documenta el criterio utilizado y cinco valores de DBO de salida aparecen asociados con ambas clasificaciones. A ello se suman la cobertura temporal limitada y la ausencia de variables operacionales y contextuales necesarias para sustentar una predicción confiable.

El análisis no permite establecer causalidad ni verificar cumplimiento legal. Su alcance es descriptivo, exploratorio y comparativo, y busca organizar evidencia para orientar revisiones posteriores.

## Estructura del proyecto

- `analisis_aqualimpia.ipynb`: notebook principal con carga, validación, análisis, visualizaciones y generación de resultados.
- `codigo/__init__.py`: archivo que permite utilizar `codigo` como paquete de Python.
- `codigo/funciones_analisis.py`: funciones reutilizables para preparar los datos, auditar su calidad, detectar candidatos atípicos con NumPy, calcular correlaciones con SciPy, construir reportes y persistir resultados.
- `codigo/ejecutar_analisis.py`: script ejecutable que valida el dataset y regenera los reportes Excel y el resumen Joblib.
- `datos/dataset_set_A_aguas_residuales.xlsx`: dataset original proporcionado para la tarea.
- `datos/README.md`: documentación del origen, integridad y tratamiento del dataset.
- `resultados/dashboard_aqualimpia.html`: dashboard exploratorio interactivo.
- `resultados/P1_Figura_1_dashboard_exploratorio_aqualimpia.png`: captura del dashboard utilizada en el informe académico.
- `resultados/reporte_operaciones.xlsx`: reporte detallado para Operaciones.
- `resultados/reporte_gestion_ambiental.xlsx`: reporte detallado para Gestión Ambiental.
- `resultados/resumen_resultados.joblib`: resumen serializado para reutilización programática.
- `resultados/README.md`: descripción y condiciones de uso de los productos generados.
- `requirements.txt`: dependencias necesarias para reproducir el proyecto.

## Requisitos

- Python 3.14
- Dependencias indicadas en `requirements.txt`
- Entorno compatible con Jupyter Notebook

Para instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

1. Clonar o descargar el repositorio.
2. Crear y activar un entorno virtual de Python.
3. Instalar las dependencias desde `requirements.txt`.
4. Abrir `analisis_aqualimpia.ipynb`.
5. Seleccionar el entorno como kernel.
6. Reiniciar el kernel y ejecutar todas las celdas en orden.

Los reportes Excel y el resumen Joblib también pueden regenerarse desde la terminal:

```powershell
python .\codigo\ejecutar_analisis.py
```

El script valida el dataset, utiliza las funciones externas y guarda los resultados mediante rutas relativas. El dashboard HTML se genera desde el notebook porque depende de las visualizaciones interactivas construidas durante el análisis.

El flujo utiliza rutas relativas. El dataset debe permanecer en `datos/` con el nombre documentado. Los archivos de `resultados/` se regeneran durante la ejecución y no deben editarse manualmente.

## Productos generados

### Dashboard exploratorio

El dashboard integra cinco vistas:

- eficiencia promedio y mediana de remoción de DBO;
- proporción de cumplimiento registrado;
- relación entre caudal de entrada y energía de aireación;
- distribución de la DBO de salida;
- evolución temporal de la eficiencia mediana.

El archivo HTML incorpora Plotly, mantiene su interactividad sin conexión a internet y utiliza colores constantes para identificar las plantas en todos los paneles.

### Reporte de Operaciones

Incluye fecha, planta, caudal de entrada, DBO de entrada y salida, eficiencia de remoción, energía de aireación, lodos generados y generación específica de lodos.

### Reporte de Gestión Ambiental

Incluye fecha, planta, DBO de salida, código original de cumplimiento y una etiqueta descriptiva de cumplimiento registrado.

### Resumen Joblib

Conserva el periodo analizado, la cantidad de registros, el número de plantas y el resumen comparativo por instalación. Debe cargarse únicamente desde una fuente confiable.

## Limitaciones principales

- El periodo observado abarca 120 días y partes de cuatro meses calendario, aunque el caso lo presenta como el último trimestre.
- El dataset contiene 98 fechas distintas dentro del periodo observado. Esta cobertura no permite asumir una frecuencia diaria obligatoria ni afirmar que existan fechas faltantes.
- Existen varias observaciones para una misma planta y fecha, pero no se dispone de hora ni identificador de muestra.
- El dataset no documenta la regla utilizada para asignar `cumplimiento_norma`.
- Cinco valores iguales de DBO de salida aparecen asociados tanto a cumplimiento como a incumplimiento.
- La variable de energía no especifica el periodo del consumo, por lo que no se calcula energía específica en kWh/m³.
- No se incluyen metas operacionales, capacidades de diseño ni rangos técnicos que permitan clasificar automáticamente el desempeño de las plantas.
- Los candidatos atípicos detectados mediante el rango intercuartílico se conservan, porque el criterio estadístico no demuestra que sean errores.

Estas limitaciones no impiden describir la muestra, pero restringen las conclusiones y deben considerarse antes de utilizar los resultados para decisiones operacionales o ambientales.

## Repositorio

[GitHub: ciencia-datos-unidad-3-aqualimpia](https://github.com/Fabyarrue/ciencia-datos-unidad-3-aqualimpia)

## Estado

El análisis principal, el dashboard, las funciones reutilizables, las preguntas de investigación y los reportes diferenciados se encuentran implementados y verificados. La documentación académica y la revisión final de la entrega continúan en desarrollo.