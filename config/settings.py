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
    "Uso de Internet (%)": "Mide la adopcion digital en Nicaragua. Representa el porcentaje de la poblacion que ha utilizado la red en los ultimos 3 meses, reflejando el progreso en conectividad, inclusion tecnologica y acceso a la informacion.",
    "Remesas (% del PIB)": "Indica el peso de las transferencias monetarias enviadas por nicaraguenses en el extranjero sobre la economia nacional. Un valor alto subraya la gran dependencia de estos flujos externos para el sustento de los hogares locales.",
    "Acceso a Electricidad (%)": "Evalua el porcentaje de habitantes conectados a la red electrica tanto en zonas urbanas como rurales. Es un pilar fundamental para el desarrollo de infraestructuras basicas, la productividad comercial y el confort moderno.",
    "Inversion en Educacion (% PIB)": "Muestra el gasto consolidado del gobierno en el sistema educativo respecto al tamano de la economia. Las caidas abruptas a 0 o lineas planas prolongadas en la grafica se deben frecuentemente a lagunas de reporte oficial (data gaps) en los servidores del Banco Mundial, no necesariamente a un recorte real del presupuesto interno.",
    "Esperanza de Vida (Años)": "Promedio de años que se espera que viva un recien nacido manteniendo los patrones actuales de mortalidad. Funciona como el indicador sintetico mas completo sobre las condiciones socioeconomicas y la calidad de vida en el pais.",
    "Gasto en Salud (% PIB)": "Proporcion de la riqueza nacional destinada al sistema sanitario. Refleja directamente la capacidad del pais para brindar cobertura medica. Periodos sin variacion pueden indicar falta de actualizacion anual en las auditorias internacionales.",
    "Inflacion (% Anual)": "Mide la tasa de variacion anual de los precios al consumidor. Refleja el incremento del costo de vida y la perdida de poder adquisitivo de la moneda local, siendo un indicador clave de estabilidad macroeconomica.",
    "Desempleo (%)": "Porcentaje de la poblacion economicamente activa que se encuentra sin trabajo pero esta disponible y buscando empleo activamente. Las variaciones atipicas o curvas muy suavizadas suelen ser resultado de estimaciones estadisticas modeladas por la OIT ante la ausencia de censos laborales continuos.",
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
