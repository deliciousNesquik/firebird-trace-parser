"""
Парсер trace логов Firebird.

Этот модуль предоставляет инструменты для парсинга
trace логов сервера Firebird.
"""

__description__ = "Firebird trace log parser"
__version__ = "0.1.0"

from parser.engine import TraceLogParser
from parser.handlers import EventHandler

__all__ = [
    "TraceLogParser",
    "EventHandler",
]
