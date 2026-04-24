# Insight Five0Five: Monitor de Desarrollo Nacional

Bienvenido a **Insight Five0Five**, un proyecto de visualización de datos e inteligencia de negocios desarrollado en la clase de Administración de Sistemas de Información en la carrera de Ingeniería de Sistemas en la Universidad Nacional Heroes de San Jose de las Mulas en Rivas, Nicaragua.

Esta aplicación web extrae, procesa y visualiza indicadores macroeconómicos y de desarrollo social de Nicaragua (+505), consumiendo directamente la base de datos oficial del Banco Mundial.

## Objetivo del Proyecto

El propósito de este proyecto es demostrar la aplicación práctica de herramientas como **Streamlit**, **Pandas**, **NumPy**, **Matplotlib**, **Seaborn** y el**Consumo de APIs Externas**.

### Conceptos Aplicados en el Código:
1. **Integración de APIs (Middleware):** Uso de la librería `wbgapi` para conectarse a los servidores del Banco Mundial sin depender de datasets estáticos obsoletos (CSV/Excel).
2. **Procesamiento de Datos (Pandas):** 
   - Transformación de DataFrames de formato *Long* a *Wide* usando `pivot_table`.
   - Limpieza de datos espurios y manejo de valores nulos (NaNs) mediante **interpolación lineal** (`interpolate`).
3. **Análisis Estadístico (NumPy):** Implementación de algoritmos matemáticos para calcular deltas interanuales y un motor simple de **detección de anomalías** (identificación de *outliers* históricos que superan las 2 desviaciones estándar de la media de crecimiento).
4. **Optimización de Recursos:** Uso de memoria caché en el servidor (`@st.cache_data`) para minimizar peticiones HTTP redundantes a la API, ahorrando ancho de banda y garantizando un tiempo de carga algorítmico de O(1) en los re-renders.

## Requisitos Técnicos y Entorno Virtual

Para garantizar la reproducibilidad del entorno de desarrollo y evitar conflictos de versiones, se recomienda el uso de entornos virtuales (`venv`).

### Instrucciones de Instalación

1. Clona el repositorio y navega hasta el directorio del proyecto (`Insight Five0Five`).

2. Instala las dependencias estrictas definidas en el archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Despliega el servidor local:
   ```bash
   streamlit run app.py
   ```

## Diccionario de Datos (Indicadores Analizados)

El pipeline de datos consulta actualmente 8 métricas estructurales:

1. **Uso de Internet (% de la población):** Penetración de la conectividad digital en los hogares.
2. **Remesas recibidas (% del PIB):** Dependencia macroeconómica de los flujos monetarios internacionales.
3. **Acceso a la electricidad (% de la población):** Indicador base de desarrollo de infraestructura urbana y rural.
4. **Inversión en Educación (% PIB):** Gasto público estructural en formación de capital humano.
5. **Esperanza de Vida (Años):** Métrica sintética de la eficacia del ecosistema de salud y condiciones de vida.
6. **Gasto en Salud (% PIB):** Proporción de la economía destinada a cobertura y prevención médica.
7. **Inflación (% Anual):** Aumento sostenido del costo de la canasta básica e índice de precios al consumidor.
8. **Desempleo (%):** Población económicamente activa cesante y buscando inserción laboral (Datos modelados por la OIT).

> **Nota Metodológica (Data Gaps):** Como ingenieros y analistas, debemos ser críticos con las fuentes de datos. Al utilizar la aplicación, se observará que algunas gráficas (como la Inversión en Educación) presentan líneas planas o nulas en años recientes. El algoritmo de Python no está fallando; esto ocurre debido a **lagunas de reporte estadístico oficial (data gaps)** por parte del Estado hacia los organismos internacionales.

## Posibles Mejoras a Futuro (Roadmap Estudiantil)

- [ ] Integrar algoritmos de *Machine Learning* (ej. Regresión Lineal con `scikit-learn`) para realizar análisis predictivo del próximo año fiscal.
- [ ] Implementar un botón dinámico (`st.download_button`) para que los usuarios puedan descargar el DataFrame ya procesado y limpio en formato CSV.
- [ ] Construir un manejador global de excepciones (Try/Except) más sofisticado para caídas severas por Timeouts en la API REST.

---
