import logging
import sys

from application.transformer import DataTransformer
from application.validator import DataValidator
from config.settings import (
    ANIOS_HISTORIA,
    DB_NAME,
    INDICATORS,
    PAIS,
    RANGOS_VALIDOS,
    SCHEMA_FILE,
)
from domain.exceptions import DomainError
from domain.use_cases import PopulateDatabaseUseCase
from infrastructure.api.worldbank import WorldBankSource
from infrastructure.persistence.sqlite import SQLiteRepository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("populate_db")


def main() -> None:
    source = WorldBankSource()
    # SRP & LSP: SQLiteRepository se inicializa con la ruta del archivo de base de datos
    repo = SQLiteRepository(DB_NAME)
    transformer = DataTransformer()
    validator = DataValidator()
    
    # OCP & DIP: Componemos el caso de uso inyectando todas las dependencias concretas
    # y los parámetros de configuración correspondientes.
    use_case = PopulateDatabaseUseCase(
        source=source,
        repo=repo,
        transformer=transformer,
        validator=validator,
        indicators=INDICATORS,
        country=PAIS,
        db_name=DB_NAME,
        schema_file=SCHEMA_FILE,
        anios_historia=ANIOS_HISTORIA,
        rangos_validos=RANGOS_VALIDOS,
    )

    try:
        use_case.execute()
    except DomainError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error("Error inesperado: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

