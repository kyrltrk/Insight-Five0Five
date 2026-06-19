import logging
import sys

from application.transformer import DataTransformer
from application.validator import DataValidator
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
    repo = SQLiteRepository()
    transformer = DataTransformer()
    validator = DataValidator()
    use_case = PopulateDatabaseUseCase(source, repo, transformer, validator)

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
