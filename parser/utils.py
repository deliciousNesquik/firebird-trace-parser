"""Вспомогательные функции для парсера."""

from typing import Dict, List, Optional

import regex
from models import AttachmentInfo, TransactionInfo, SqlParam, PerformanceInfo


def parse_attachment_info(
    body_lines: List[str], rules: Dict[str, regex.Pattern]
) -> Optional[AttachmentInfo]:
    """
    Парсит информацию о подключении.

    Args:
        body_lines: Строки для парсинга
        rules: Словарь правил поиска

    Returns:
        AttachmentInfo или None
    """
    attachment = None
    process_path = None
    process_id = None

    for line in body_lines:
        # Attachment
        m = rules["attachment"].match(line)
        if m:
            attachment = AttachmentInfo(
                database_path=m.group("database_path"),
                attachment_id=int(m.group("attachment_id")),
                user=m.group("user"),
                role=m.group("role"),
                charset=m.group("charset"),
                protocol=m.group("protocol").strip(),
                address=m.group("address"),
                port=int(m.group("port")) if m.group("port") else None,
                process_path=None,
                process_id=None,
            )
            continue

        # Process
        m = rules["process"].match(line)
        if m:
            process_path = m.group("process_path")
            process_id = int(m.group("process_id"))

    # Дополняем attachment процессом
    if attachment and (process_path or process_id):
        object.__setattr__(attachment, "process_path", process_path)
        object.__setattr__(attachment, "process_id", process_id)

    return attachment


def parse_transaction_info(
    body_lines: List[str], rules: Dict[str, regex.Pattern]
) -> Optional["TransactionInfo"]:
    for line in body_lines:
        # Быстрый фильтр без regex
        if "(TRA_" not in line:
            continue

        # Извлекаем ID и сырую строку параметров
        match = rules['transaction'].match(line)
        if not match:
            continue

        tid = int(match.group(1))
        raw_params = match.group(2)

        # Разбиваем по '|', чистим, отбрасываем явные None/пустоты
        parts = [
            p.strip().upper()
            for p in raw_params.split('|')
            if p.strip() and p.strip().upper() not in ('NONE', '(NONE)')
        ]

        # Гарантируем ровно 4 позиции (FB5 порядок фиксирован)
        parts += [None] * (4 - len(parts))

        return TransactionInfo(
            transaction_id=tid,
            isolation_level=parts[0],
            consistency_mode=parts[1],
            lock_mode=parts[2],
            access_mode=parts[3],
        )
    return None


def parse_params(
    body_lines: List[str], rules: Dict[str, regex.Pattern]
) -> List[SqlParam]:
    """
    Парсит SQL параметры.

    Args:
        body_lines: Строки для парсинга
        rules: Словарь регулярных выражений

    Returns:
        Список SqlParam
    """
    params = []

    for line in body_lines:
        m = rules["parameters"].match(line)
        if m:
            params.append(
                SqlParam(
                    name=m.group("name"),
                    dtype=m.group("dtype"),
                    value=m.group("value"),
                )
            )

    return params


def parse_performance(
    body_lines: List[str], rules: Dict[str, regex.Pattern]
) -> Optional[PerformanceInfo]:
    """
    Парсит информацию о производительности.

    Args:
        body_lines: Строки для парсинга
        rules: Словарь регулярных выражений

    Returns:
        PerformanceInfo или None
    """
    fetch_count = 0

    for line in body_lines:
        # Fetched count
        m = rules["fetched"].match(line)
        if m:
            fetch_count = int(m.group("fetch_count"))

        # Performance metrics
        m = rules["performance"].match(line)
        if m:
            return PerformanceInfo(
                execute_ms=int(m.group("execute_ms")),
                fetch_count=fetch_count,
                read_count=int(m.group("read") or 0),
                write_count=int(m.group("write") or 0),
                mark_count=int(m.group("mark") or 0),
            )

    return None
