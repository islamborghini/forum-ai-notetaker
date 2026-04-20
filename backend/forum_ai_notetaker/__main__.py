import logging

from .db import init_db

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    db_path = init_db()
    logger.info("Initialized SQLite database at %s", db_path)


if __name__ == "__main__":
    main()
