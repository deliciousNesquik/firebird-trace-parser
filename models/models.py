from dataclasses import dataclass

from models import EventBase
from models.enums import *
from typing import List


@dataclass(slots=True)
class TraceInitEvent(EventBase):
    """
    Событие начала trace‑сессии Firebird.

    Сигнализирует о старте глобальной сессии трассировки,
    после которой будут генерироваться другие события.
    """
    session: TraceSessionInfo
    """ Информация о глобальной trace‑сессии (идентификатор сессии). """


@dataclass(slots=True)
class TraceFinishEvent(EventBase):
    """
    Событие завершения trace‑сессии Firebird.

    Сигнализирует о завершении глобальной сессии трассировки
    и остановке сбора событий.
    """
    session: TraceSessionInfo
    """Информация о глобальной trace‑сессии (идентификатор сессии)."""


@dataclass(slots=True)
class AttachDatabaseEvent(EventBase):
    """
    Событие подключения к базе данных Firebird.

    Фиксирует факт подключения пользователя к базе данных
    в рамках trace‑сессии.
    """
    attachment: AttachmentInfo
    """Информация о подключении пользователя к базе данных."""

@dataclass(slots=True)
class DetachDatabaseEvent(EventBase):
    """
    Событие отключения от базы данных Firebird.

    Фиксирует факт завершения сессии подключения
    пользователя к базе данных.
    """
    attachment: AttachmentInfo
    """Информация о подключении пользователя к базе данных."""


@dataclass(slots=True)
class StatementEventBase(EventBase):
    """
    Базовая модель события SQL‑statement в trace‑механизме Firebird.

    Содержит общие поля для событий, связанных с выполнением
    SQL‑запросов (SELECT, INSERT, UPDATE, DELETE и т.п.).
    """
    attachment: AttachmentInfo
    """Информация о подключении пользователя к базе данных."""

    transaction: TransactionInfo
    """Информация о транзакции, в рамках которой выполняется statement."""

    statement_id: int
    """Идентификатор SQL‑statement (prepare‑идентификатор)."""

    sql: str
    """Текст SQL‑запроса."""

    params: List[SqlParam]
    """Список параметров SQL‑запроса."""

@dataclass(slots=True)
class ProcedureEventBase(EventBase):
    """
    Базовая модель события вызова хранимой процедуры Firebird.

    Содержит общие поля для событий, связанных с запуском
    хранимых процедур.
    """
    attachment: AttachmentInfo
    """Информация о подключении пользователя к базе данных."""

    transaction: TransactionInfo
    """Информация о транзакции, в рамках которой вызывается процедура."""

    procedure_name: str
    """Имя вызываемой хранимой процедуры."""

    params: List[SqlParam]
    """"Список параметров процедуры."""


@dataclass(slots=True)
class TriggerEventBase(EventBase):
    """
    Базовая модель события срабатывания триггера Firebird.

    Содержит общие поля для событий, связанных с выполнением
    триггеров на таблицах.
    """
    attachment: AttachmentInfo
    """Информация о подключении пользователя к базе данных."""

    transaction: TransactionInfo
    """Информация о транзакции, в рамках которой выполняется триггер."""

    trigger_name: str
    """Имя срабатывающего триггера."""

    table: str
    """Имя таблицы, на которой определён триггер."""

    timing: str
    """Время срабатывания триггера (BEFORE / AFTER)."""

    event: str
    """Событие, на которое срабатывает триггер (INSERT / UPDATE / DELETE)."""


@dataclass(slots=True)
class StatementStartEvent(StatementEventBase):
    """
    Событие начала выполнения SQL‑statement в Firebird.

    Фиксирует момент старта выполнения SQL‑запроса
    в рамках trace‑сессии.
    """


@dataclass(slots=True)
class StatementFinishEvent(StatementEventBase):
    """
    Событие завершения выполнения SQL‑statement в Firebird.

    Фиксирует момент завершения выполнения SQL‑запроса
    и содержит метрики производительности.
    """
    performance: PerformanceInfo
    """Общая информация о производительности выполнения SQL‑statement."""

    performance_table: PerformanceTable
    """Статистика по таблицам, затронутым SQL‑statement."""


@dataclass(slots=True)
class ProcedureStartEvent(ProcedureEventBase):
    """
    Событие начала выполнения хранимой процедуры в Firebird.

    Фиксирует момент старта выполнения хранимой процедуры
    в рамках trace‑сессии.
    """


@dataclass(slots=True)
class ProcedureFinishEvent(ProcedureEventBase):
    """
    Событие завершения выполнения хранимой процедуры в Firebird.

    Фиксирует момент завершения выполнения хранимой процедуры
    и содержит метрики производительности.
    """
    performance: PerformanceInfo
    """Общая информация о производительности выполнения хранимой процедуры."""

    performance_table: PerformanceTable
    """Статистика по таблицам, затронутым хранимой процедурой."""


@dataclass(slots=True)
class TriggerStartEvent(TriggerEventBase):
    """
    Событие начала выполнения триггера в Firebird.

    Фиксирует момент старта выполнения триггера
    в рамках trace‑сессии.
    """


@dataclass(slots=True)
class TriggerFinishEvent(TriggerEventBase):
    """
    Событие завершения выполнения триггера в Firebird.

    Фиксирует момент завершения выполнения триггера
    и содержит метрики производительности.
    """
    performance: PerformanceInfo
    """Общая информация о производительности выполнения триггера."""

    performance_table: PerformanceTable
    """Статистика по таблицам, затронутым триггером."""
