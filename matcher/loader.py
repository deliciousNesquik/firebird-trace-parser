import tomllib
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any

import regex

from matcher.rules import RuleConfigError

FLAG_MAP = {
    "IGNORECASE": regex.IGNORECASE,
    "MULTILINE": regex.MULTILINE,
    "DOTALL": regex.DOTALL,
    "VERBOSE": regex.VERBOSE,
}

DEFAULT_FLAGS = ("VERBOSE",)
SCHEMA_VERSION = 1


@lru_cache(maxsize=128)
def _resolve_flags_cached(flag_names: tuple[str, ...]) -> int:
    """
    Преобразует имена флагов регулярных выражений в целочисленное значение битового поля.

    Функция предназначена для парсинга строковых имен флагов regex (например, 'VERBOSE', 'MULTILINE', 'DOTALL')
    и преобразования их в соответствующие битовые флаги Python re-модуля (re.IGNORECASE,
    re.MULTILINE и т.д.). Поддерживает комбинирование нескольких флагов через побитовое ИЛИ.

    Args:
        flag_names (tuple[str, ...]): Кортеж строковых имен флагов.
                                     Если пустой или None, используются DEFAULT_FLAGS.

    Returns:
        int: Целочисленное значение объединённых флагов для передачи в re.compile().

    Raises:
        RuleConfigError: Если указано неизвестное имя флага (отсутствует в FLAG_MAP).

    Примеры:
        >>> _resolve_flags_cached(('IGNORECASE', 'MULTILINE',))
        82  # re.IGNORECASE | re.MULTILINE (0x52)
        >>> _resolve_flags_cached(())
        значение DEFAULT_FLAGS  # зависит от глобальной константы
        >>> _resolve_flags_cached(('unknown',))
        RuleConfigError: Неизвестный флаг regex: unknown

    Зависимости:
        - Глобальные константы: FLAG_MAP (dict[str, int]), DEFAULT_FLAGS (tuple[str, ...])
        - Исключение: RuleConfigError

    Примечание:
        Используется в конфигурации правил валидации/парсинга, где флаги задаются
        в конфигурационных файлах или через аргументы CLI в строковом виде.
    """
    flags = 0  # Инициализируем нулевым значением битового поля

    # Используем DEFAULT_FLAGS как fallback для пустого входа
    names = flag_names or DEFAULT_FLAGS

    for name in names:
        # Нормализуем имя флага: переводим в верхний регистр для единообразия
        key = name.upper()

        # Проверяем валидность флага в словаре сопоставлений
        if key not in FLAG_MAP:
            raise RuleConfigError(f"Неизвестный флаг regex: {name}")

        # Добавляем флаг к общему значению через побитовое ИЛИ (поддержка множественных флагов)
        flags |= FLAG_MAP[key]

    return flags  # Возвращаем итоговое значение


def _load_toml_config(config_path: str | Path) -> dict[str, Any]:
    """
    Загружает TOML-конфигурацию в память.

    Args:
        config_path: Путь к TOML-файлу.

    Returns:
        dict[str, Any]: Данные конфигурации.

    Raises:
        RuleConfigError: Если файл не найден или ошибка парсинга TOML.
    """
    path = Path(config_path)

    if not path.is_file():
        raise RuleConfigError(f"Файл конфигурации не найден: {path}")

    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise RuleConfigError(f"Ошибка TOML в файле {path}: {exc}") from exc

    return data


def _validate_config(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Валидирует структуру TOML-конфигурации.

    Args:
        data: Загруженные данные TOML.

    Returns:
        dict[str, dict[str, Any]]: Валидированная секция rules.

    Raises:
        RuleConfigError: Если schema_version неверная или отсутствует/неверна секция rules.
    """
    schema_version = data.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise RuleConfigError(f"Неподдерживаемая schema_version: {schema_version}")

    raw_rules = data.get("rules")
    if not isinstance(raw_rules, dict) or not raw_rules:
        raise RuleConfigError("В конфигурации отсутствует секция [rules]")

    return raw_rules


def _compile_rules(
    raw_rules: dict[str, dict[str, Any]], strict: bool = True
) -> dict[str, regex.Pattern]:
    """Оптимизирована: кэш флагов, батчинг sample-тестов."""
    compiled: dict[str, regex.Pattern] = {}

    # Предкомпилируем все флаги заранее (экономия на повторных вызовах)
    flag_cache = {}

    for rule_name, rule_data in raw_rules.items():
        try:
            pattern = rule_data["pattern"]
            flags_tuple = tuple(rule_data.get("flags", DEFAULT_FLAGS))

            # Кэш флагов по tuple
            if flags_tuple not in flag_cache:
                flag_cache[flags_tuple] = _resolve_flags_cached(flags_tuple)
            flags = flag_cache[flags_tuple]

            # Компиляция — самая дорогая операция (verbose + multiline)
            rx = regex.compile(pattern, flags)

            # Валидация групп (set-операции быстрые)
            spec_groups = set(rule_data.get("required_groups", ()))
            missing = spec_groups - set(rx.groupindex)
            if missing:
                raise RuleConfigError(
                    f"Правило '{rule_name}' не содержит группу: {', '.join(sorted(missing))}"
                )

            # Тест sample (опционально, батчинг если много)
            sample = rule_data.get("sample")
            if sample and rx.search(sample) is None:
                raise RuleConfigError(f"Правило '{rule_name}' не совпадает с sample")

            compiled[rule_name] = rx

        except Exception as exc:
            if strict:
                raise RuleConfigError(f"Ошибка в правиле '{rule_name}': {exc}") from exc
            warnings.warn(f"Правило '{rule_name}' пропущено: {exc}", stacklevel=2)

    return compiled


def load_rules(
    config_path: str | Path, strict: bool = True
) -> dict[str, regex.Pattern]:
    """
    Загружает, валидирует и компилирует regex-правила из TOML.

    Args:
        config_path: Путь к TOML-файлу с правилами.
        strict: Если False, пропускает невалидные правила с предупреждением.

    Returns:
        dict[str, regex.Pattern]: Скомпилированные regex-правила {имя: Pattern}.

    Raises:
        RuleConfigError: Ошибки загрузки, валидации или компиляции (в strict-режиме).
    """

    data = _load_toml_config(config_path)
    raw_rules = _validate_config(data)
    return _compile_rules(raw_rules, strict)


# Кэшированная глобальная загрузка (для многократных вызовов)
@lru_cache(maxsize=1)  # Единственный файл — maxsize=1
def load_rules_cached(
    config_path: str | Path, strict: bool = True
) -> dict[str, regex.Pattern]:
    """Кэшированная версия для повторных загрузок (например, в тестах/сервисе)."""
    return load_rules(config_path, strict)


if __name__ == "__main__":
    rules = load_rules("rules.toml")
    print(rules.keys())
