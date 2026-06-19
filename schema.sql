-- worldbank schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS indicadores (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    UNIQUE(codigo)
);

CREATE TABLE IF NOT EXISTS valores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT NOT NULL,
    indicador_codigo TEXT NOT NULL,
    anio INTEGER NOT NULL CHECK(anio >= 1990),
    valor REAL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (indicador_codigo)
        REFERENCES indicadores(codigo)
        ON DELETE CASCADE,
    UNIQUE(pais, indicador_codigo, anio)
);

CREATE INDEX IF NOT EXISTS idx_valores_pais ON valores(pais);
CREATE INDEX IF NOT EXISTS idx_valores_indicador ON valores(indicador_codigo);
CREATE INDEX IF NOT EXISTS idx_valores_anio ON valores(anio);
CREATE INDEX IF NOT EXISTS idx_valores_busqueda
    ON valores(pais, indicador_codigo, anio);

CREATE VIEW IF NOT EXISTS vista_indicadores_recientes AS
SELECT
    i.codigo,
    i.nombre,
    v.pais,
    v.anio,
    v.valor
FROM indicadores i
LEFT JOIN valores v ON i.codigo = v.indicador_codigo
WHERE v.anio = (SELECT MAX(anio) FROM valores v2
                WHERE v2.indicador_codigo = i.codigo);
