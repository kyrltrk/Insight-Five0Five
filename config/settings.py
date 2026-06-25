import os
from typing import Dict, Optional, Tuple


DB_NAME: str = os.environ.get("WORLDBANK_DB", "worldbank.db")
SCHEMA_FILE: str = os.environ.get("WORLDBANK_SCHEMA", "schema.sql")
PAIS: str = os.environ.get("WORLDBANK_PAIS", "NIC")
ANIOS_HISTORIA: int = int(os.environ.get("WORLDBANK_ANIOS", "30"))

INDICATORS: Dict[str, str] = {
    "IT.NET.USER.ZS": "Uso de Internet (%)",
    "BX.TRF.PWKR.DT.GD.ZS": "Remesas (% del PIB)",
    "EG.ELC.ACCS.ZS": "Acceso a Electricidad (%)",
    "SE.XPD.TOTL.GD.ZS": "Inversión en Educación (% PIB)",
    "SP.DYN.LE00.IN": "Esperanza de Vida (Años)",
    "SH.XPD.CHEX.GD.ZS": "Gasto en Salud (% PIB)",
    "FP.CPI.TOTL.ZG": "Inflación (% Anual)",
    "SL.UEM.TOTL.ZS": "Desempleo (%)",
}

INDICATOR_DESCRIPTIONS: Dict[str, str] = {
    "Uso de Internet (%)": "Mide la adopción digital en Nicaragua. Representa el porcentaje de la población que ha utilizado la red en los últimos 3 meses, reflejando el progreso en conectividad, inclusión tecnológica y acceso a la información.",
    "Remesas (% del PIB)": "Indica el peso de las transferencias monetarias enviadas por nicaragüenses en el extranjero sobre la economía nacional. Un valor alto subraya la gran dependencia de estos flujos externos para el sustento de los hogares locales.",
    "Acceso a Electricidad (%)": "Evalúa el porcentaje de habitantes conectados a la red eléctrica tanto en zonas urbanas como rurales. Es un pilar fundamental para el desarrollo de infraestructuras básicas, la productividad comercial y el confort moderno.",
    "Inversión en Educación (% PIB)": "Muestra el gasto consolidado del gobierno en el sistema educativo respecto al tamaño de la economía. Las caídas abruptas a 0 o líneas planas prolongadas en la gráfica se deben frecuentemente a lagunas de reporte oficial (data gaps) en los servidores del Banco Mundial, no necesariamente a un recorte real del presupuesto interno.",
    "Esperanza de Vida (Años)": "Promedio de años que se espera que viva un recién nacido manteniendo los patrones actuales de mortalidad. Funciona como el indicador sintético más completo sobre las condiciones socioeconómicas y la calidad de vida en el país.",
    "Gasto en Salud (% PIB)": "Proporción de la riqueza nacional destinada al sistema sanitario. Refleja directamente la capacidad del país para brindar cobertura médica. Periodos sin variación pueden indicar falta de actualización anual en las auditorías internacionales.",
    "Inflación (% Anual)": "Mide la tasa de variación anual de los precios al consumidor. Refleja el incremento del costo de vida y la pérdida de poder adquisitivo de la moneda local, siendo un indicador clave de estabilidad macroeconómica.",
    "Desempleo (%)": "Porcentaje de la población económicamente activa que se encuentra sin trabajo pero está disponible y buscando empleo activamente. Las variaciones atípicas o curvas muy suavizadas suelen ser resultado de estimaciones estadísticas modeladas por la OIT ante la ausencia de censos laborales continuos.",
}

RANGOS_VALIDOS: Dict[str, Tuple[Optional[float], Optional[float]]] = {
    "IT.NET.USER.ZS": (0, 100),
    "BX.TRF.PWKR.DT.GD.ZS": (0, 100),
    "EG.ELC.ACCS.ZS": (0, 100),
    "SE.XPD.TOTL.GD.ZS": (0, 100),
    "SP.DYN.LE00.IN": (20, 100),
    "SH.XPD.CHEX.GD.ZS": (0, 100),
    "FP.CPI.TOTL.ZG": (-50, 500),
    "SL.UEM.TOTL.ZS": (0, 100),
}
