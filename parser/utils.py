"""Вспомогательные функции для парсера."""

from typing import List, Optional
from models import AttachmentInfo, TransactionInfo, SqlParam, PerformanceInfo
from matcher import *


def parse_attachment_info(body_lines: List[str]) -> Optional[AttachmentInfo]:
    """
    Парсит информацию о подключении.
    
    Args:
        body_lines: Строки для парсинга
        
    Returns:
        AttachmentInfo или None
    """
    attachment = None
    process_path = None
    process_id = None
    
    for line in body_lines:
        # Attachment
        m = RE_ATTACHMENT.match(line)
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
        m = RE_PROCESS.match(line)
        if m:
            process_path = m.group("process_path")
            process_id = int(m.group("process_id"))
    
    # Дополняем attachment процессом
    if attachment and (process_path or process_id):
        object.__setattr__(attachment, "process_path", process_path)
        object.__setattr__(attachment, "process_id", process_id)
    
    return attachment


def parse_transaction_info(body_lines: List[str]) -> Optional[TransactionInfo]:
    """
    Парсит информацию о транзакции.
    
    Args:
        body_lines: Строки для парсинга
        
    Returns:
        TransactionInfo или None
    """
    for line in body_lines:
        m = RE_TRANSACTION.match(line)
        if m:
            return TransactionInfo(
                transaction_id=int(m.group("transaction_id")),
                isolation_level=(m.group("isolation") or "").strip(),
                consistency_mode=(m.group("consistency") or "").strip() or None,
                lock_mode=(m.group("lock") or "").strip() or None,
                access_mode=(m.group("access") or "").strip() or None,
            )
    return None


def parse_params(body_lines: List[str]) -> List[SqlParam]:
    """
    Парсит SQL параметры.
    
    Args:
        body_lines: Строки для парсинга
        
    Returns:
        Список SqlParam
    """
    params = []
    
    for line in body_lines:
        m = RE_PARAM.match(line)
        if m:
            params.append(
                SqlParam(
                    name=m.group("name"),
                    dtype=m.group("dtype"),
                    value=m.group("value"),
                )
            )
    
    return params


def parse_performance(body_lines: List[str]) -> Optional[PerformanceInfo]:
    """
    Парсит информацию о производительности.
    
    Args:
        body_lines: Строки для парсинга
        
    Returns:
        PerformanceInfo или None
    """
    fetch_count = 0
    
    for line in body_lines:
        # Fetched count
        m = RE_FETCHED.match(line)
        if m:
            fetch_count = int(m.group("fetch_count"))
        
        # Performance metrics
        m = RE_PERFORMANCE.match(line)
        if m:
            return PerformanceInfo(
                execute_ms=int(m.group("execute_ms")),
                fetch_count=fetch_count,
                read_count=int(m.group("read") or 0),
                write_count=int(m.group("write") or 0),
                mark_count=int(m.group("mark") or 0),
            )
    
    return None