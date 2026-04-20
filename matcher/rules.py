from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegexRule:
    pattern: str
    required_groups: tuple[str, ...] = ()
    description: str = ""
    sample: str = ""
    flags: tuple[str, ...] = ()


class RuleConfigError(Exception):
    """Ошибка конфигурации regex-правил."""
    pass