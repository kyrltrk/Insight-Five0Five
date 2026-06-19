# Insight Five0Five: Monitor de Desarrollo Nacional

Bienvenido a **Insight Five0Five**, un proyecto de visualización de datos e inteligencia de negocios desarrollado en la clase de Administración de Sistemas de Información en la carrera de Ingeniería de Sistemas en la Universidad Nacional Heroes de San Jose de las Mulas en Rivas, Nicaragua.

Esta aplicación web extrae, procesa y visualiza indicadores macroeconómicos y de desarrollo social de Nicaragua (+505). Funciona en **modo híbrido**: con internet consume la API oficial del Banco Mundial en vivo; sin internet utiliza una base de datos SQLite local generada previamente.

## Objetivo del Proyecto

El propósito de este proyecto es demostrar la aplicación práctica de herramientas como **Streamlit**, **Pandas**, **NumPy**, **Matplotlib**, **Seaborn**, **SQLite** y el **consumo de APIs externas**, todo bajo un diseño modular y principios de arquitectura hexagonal.

### Conceptos Aplicados en el Código:

1. **Modo Híbrido API / SQLite:** Con internet, la app consulta el Banco Mundial vía `wbgapi`. Sin internet, lee desde una base de datos SQLite local, garantizando su funcionamiento offline.
2. **Pipeline ETL Modular:** El script `populate_db.py` separa responsabilidades en capas: conexión, esquema, catálogo, descarga API, transformación, validación e inserción.
3. **Validación de Datos (Calidad):** Verifica rangos válidos por indicador (porcentajes 0-100, esperanza de vida 20-100, inflación en rangos razonables) y convierte valores fuera de rango a NULL con advertencias.
4. **Logging Estructurado:** Reemplaza `print()` por logging con niveles INFO, WARNING y ERROR para mejor depuración en producción.
5. **Manejo de Errores Específico:** Captura excepciones por tipo (`FileNotFoundError`, `ValueError`, `RuntimeError`, `sqlite3.Error`, `ImportError`) en lugar de un `except Exception` genérico.
6. **Configuración por Variables de Entorno:** `WORLDBANK_DB`, `WORLDBANK_SCHEMA`, `WORLDBANK_PAIS`, `WORLDBANK_ANIOS` permiten personalizar sin modificar código.
7. **Procesamiento de Datos (Pandas):** Transformación de DataFrames de formato ancho a largo (`melt`), interpolación lineal de valores nulos y pivote a formato ancho para visualización.
8. **Análisis Estadístico (NumPy):** Implementación de algoritmos matemáticos para calcular deltas interanuales y un motor simple de detección de anomalías (identificación de outliers históricos que superan las 2 desviaciones estándar de la media de crecimiento).
9. **Optimización de Recursos:** Uso de memoria caché en el servidor (`@st.cache_data`) para minimizar peticiones HTTP redundantes a la API, ahorrando ancho de banda y garantizando un tiempo de carga algorítmico de O(1) en los re-renders.

## Requisitos Técnicos y Entorno Virtual

Para garantizar la reproducibilidad del entorno de desarrollo y evitar conflictos de versiones, se recomienda el uso de entornos virtuales (`venv`).

### Instrucciones de Instalación

1. Clona el repositorio y navega hasta el directorio del proyecto (`Insight Five0Five`).

2. Instala las dependencias definidas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Crea la base de datos local (requiere internet):**
   ```bash
   python populate_db.py
   ```
   Esto descarga los 8 indicadores socioeconómicos de Nicaragua y los almacena en `worldbank.db`.

4. Despliega el servidor local:
   ```bash
   streamlit run app.py
   ```
   - Con internet: usa la API del Banco Mundial en vivo.
   - Sin internet: usa los datos guardados en SQLite (requiere paso 3).

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

## Arquitectura del Proyecto

```
Insight Five0Five/
├── app.py                         # Composition Root (Streamlit)
├── populate_db.py                 # Composition Root (ETL)
├── schema.sql                     # Esquema SQL (tablas, índices, vistas)
├── requirements.txt               # Dependencias del proyecto
│
├── domain/                        # CAPA DE DOMINIO (el hexágono)
│   ├── entities.py                # Entidades puras (Indicator, IndicatorValue)
│   ├── exceptions.py              # Excepciones del dominio
│   ├── ports.py                   # Puertos (interfaces abstractas)
│   └── use_cases.py               # Casos de uso (GetIndicators, PopulateDatabase)
│
├── application/                   # CAPA DE APLICACIÓN (servicios)
│   ├── transformer.py             # Transformaciones (melt, interpolate, pivot)
│   └── validator.py               # Validación de rangos
│
├── infrastructure/                # CAPA DE INFRAESTRUCTURA (adaptadores)
│   ├── api/
│   │   └── worldbank.py           # WorldBankSource (wbgapi)
│   ├── persistence/
│   │   └── sqlite.py              # SQLiteRepository (sqlite3)
│   └── presentation/
│       └── streamlit.py           # StreamlitUI
│
├── config/                        # CONFIGURACIÓN
│   └── settings.py                # Constantes unificadas
│
├── tests/                         # Tests unitarios con fakes
│   ├── fakes.py
│   └── test_use_cases.py
│
├── cambios/                       # Registro de cambios
│   └── cambios_realizados.txt
│
└── Hexagonal/                     # Documentación de arquitectura
    └── documentacion.md
```

### Diagrama de Arquitectura Hexagonal

```
                       app.py (Composition Root)
                               |
                     ┌─────────▼──────────┐
                     │   StreamlitUI      │
                     │ (Infrastructure)   │
                     └─────────┬──────────┘
                               │ llama a
                     ┌─────────▼──────────┐
                     │GetIndicatorsUseCase│
                     │   (Caso de uso)    │
                     │                    │
                     │ ┌─ Intenta API ──┐ │
                     │ │   ¿Falla?      │ │
                     │ │   Sí──▼──┐     │ │
                     │ │   Lee DB │     │ │
                     │ └─────────┘     │ │
                     │      ▼           │ │
                     │ Transformar datos│ │
                     └──┬──────────┬────┘ │
                        │          │
               ┌────────▼──┐  ┌───▼──────────┐
               │WorldBank  │  │  SQLite      │
               │Source     │  │ Repository   │
               │(wbgapi)   │  │ (sqlite3)    │
               └───────────┘  └──────────────┘
               Infrastructure   Infrastructure
               (API)            (Persistence)

               FLUJO NORMAL ──►    FLUJO FALLBACK ──►
```

**Flujo normal:** `StreamlitUI → GetIndicatorsUseCase → WorldBankSource → datos transformados → UI`

**Flujo fallback (sin internet):** `StreamlitUI → GetIndicatorsUseCase → WorldBankSource(FALLA) → SQLiteRepository → datos transformados → UI`

### Capas de la Arquitectura

1. **domain/ — Capa de Dominio:** El corazón de la aplicación. Contiene entidades puras (`entities.py`), puertos o interfaces abstractas (`ports.py`), casos de uso (`use_cases.py`) y excepciones de negocio (`exceptions.py`). No importa nada de infraestructura (ni sqlite3, ni requests, ni streamlit).

2. **application/ — Capa de Aplicación:** Servicios que transforman y validan datos. `DataTransformer` realiza operaciones pandas (melt, interpolate, pivot). `DataValidator` verifica rangos válidos por indicador.

3. **infrastructure/ — Capa de Infraestructura:** Adaptadores concretos que implementan los puertos del dominio. `WorldBankSource` traduce llamadas a la API del Banco Mundial, `SQLiteRepository` maneja la persistencia, y `StreamlitUI` renderiza el dashboard.

4. **config/ — Configuración:** Constantes centralizadas como indicadores, rangos de validación y variables de entorno.

### Principios de Diseño Aplicados

1. **Dominio puro:** Las entidades (`domain/entities.py`) son dataclasses sin imports de infraestructura. Los casos de uso (`domain/use_cases.py`) orquestan la lógica sin conocer detalles técnicos.
2. **Puertos e interfaces:** Los adaptadores implementan contratos abstractos (`domain/ports.py`), permitiendo intercambiar tecnologías sin modificar el núcleo.
3. **Inversión de dependencias:** Los Composition Roots (`app.py`, `populate_db.py`) son el único lugar donde se crean instancias concretas y se inyectan dependencias.
4. **Fallback automático:** El caso de uso `GetIndicatorsUseCase` intenta la API del Banco Mundial primero; si falla, lee desde SQLite local. El usuario nunca ve el cambio de origen.
5. **Excepciones de dominio:** Errores como `ApiCaidaError` o `DatosNoEncontradosError` encapsulan problemas técnicos en términos del negocio.

## Posibles Mejoras a Futuro (Roadmap Estudiantil)

- [ ] Integrar algoritmos de *Machine Learning* (ej. Regresión Lineal con `scikit-learn`) para realizar análisis predictivo del próximo año fiscal.
- [ ] Implementar un botón dinámico (`st.download_button`) para que los usuarios puedan descargar el DataFrame ya procesado y limpio en formato CSV.
- [ ] Agregar batería de pruebas unitarias y de integración para el pipeline ETL y la capa de visualización.

---
