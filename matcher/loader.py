
from pathlib import Path
import tomllib
import warnings

import regex

from matcher.rules import RegexRule, RuleConfigError


FLAG_MAP = {
    "IGNORECASE": regex.IGNORECASE,
    "MULTILINE": regex.MULTILINE,
    "DOTALL": regex.DOTALL,
    "VERBOSE": regex.VERBOSE,
}

DEFAULT_FLAGS = ("VERBOSE",)


def _resolve_flags(flag_names: tuple[str, ...]) -> int:
    flags = 0
    names = flag_names or DEFAULT_FLAGS

    for name in names:
        key = name.upper()
        if key not in FLAG_MAP:
            raise RuleConfigError(f"Неизвестный флаг regex: {name}")
        flags |= FLAG_MAP[key]

    return flags


def load_rules(config_path: str | Path, strict: bool = True) -> dict[str, regex.Pattern]:
    """
    Загружает regex-правила из TOML, валидирует их, компилирует и возвращает словарь:
        {rule_name: compiled_regex}
    """

    path = Path(config_path)

    if not path.is_file():
        raise RuleConfigError(f"Файл конфигурации не найден: {path}")

    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise RuleConfigError(f"Ошибка TOML в файле {path}: {exc}") from exc

    schema_version = data.get("schema_version")
    if schema_version != 1:
        raise RuleConfigError(f"Неподдерживаемая schema_version: {schema_version}")

    raw_rules = data.get("rules")
    if not isinstance(raw_rules, dict) or not raw_rules:
        raise RuleConfigError("В конфигурации отсутствует секция [rules]")

    compiled: dict[str, regex.Pattern] = {}

    for rule_name, rule_data in raw_rules.items():
        try:
            if "pattern" not in rule_data:
                raise RuleConfigError(f"У правила '{rule_name}' отсутствует поле 'pattern'")

            spec = RegexRule(
                pattern=rule_data["pattern"],
                description=rule_data.get("description", ""),
                sample=rule_data.get("sample", ""),
                required_groups=tuple(rule_data.get("required_groups", ())),
                flags=tuple(rule_data.get("flags", DEFAULT_FLAGS)),
            )

            rx = regex.compile(spec.pattern, _resolve_flags(spec.flags))

            missing = set(spec.required_groups) - set(rx.groupindex)
            if missing:
                raise RuleConfigError(
                    f"Правило '{rule_name}' не содержит группы: {', '.join(sorted(missing))}"
                )

            if spec.sample and rx.search(spec.sample) is None:
                raise RuleConfigError(
                    f"Правило '{rule_name}' не совпадает с sample"
                )

            compiled[rule_name] = rx

        except Exception as exc:
            if strict:
                if isinstance(exc, RuleConfigError):
                    raise
                raise RuleConfigError(f"Ошибка в правиле '{rule_name}': {exc}") from exc

            warnings.warn(f"Правило '{rule_name}' пропущено: {exc}", stacklevel=2)

    return compiled


if __name__ == "__main__":
    rules = load_rules("rules.toml")
    print(rules.keys())