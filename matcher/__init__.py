# matcher/__init__.py

__description__: str = "Класс, содержащий правила поиска регулярными выражениями, а также способный переопределиться пользовательскими правилами."
__version__: str = "0.0.1"

from matcher.rules import (
    RE_BLOCK_HEADER,
    RE_SESSION,
    RE_PROCESS,
    RE_ATTACHMENT,
    RE_FETCHED,
    RE_PARAM,
    RE_PERFORMANCE,
    RE_SQL_BLOCK,
    RE_STATEMENT_HEADER,
    RE_TABLE_ROW,
    RE_TRANSACTION,
    RE_PROCEDURE_HEADER,
    RE_TRIGGER_HEADER,
)

__all__ = [
    "RE_BLOCK_HEADER",
    "RE_SESSION",
    "RE_PROCESS",
    "RE_ATTACHMENT",
    "RE_FETCHED",
    "RE_PARAM",
    "RE_PERFORMANCE",
    "RE_SQL_BLOCK",
    "RE_STATEMENT_HEADER",
    "RE_TABLE_ROW",
    "RE_TRANSACTION",
    "RE_PROCEDURE_HEADER",
    "RE_TRIGGER_HEADER",
]
