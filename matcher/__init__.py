# matcher/__init__.py

__description__: str = (
    "Модуль сопоставления для обработки событий трассировки на основе заданных правил."
)
__version__: str = "0.1.0"

from matcher.loader import load_rules

__all__ = [
    "load_rules",
]
