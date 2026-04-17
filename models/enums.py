# models/enums.py

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class EventType(str, Enum):
    """Тип события trace log firebird"""

    TRACE_INIT = "TRACE_INIT"  #: Инициализация trace сессии
    TRACE_FINI = "TRACE_FINI"  #: Завершение trace сессии

    ATTACH_DATABASE = "ATTACH_DATABASE"  #: Подключение к базе данных
    DETACH_DATABASE = "DETACH_DATABASE"  #: Отключение от базы данных

    EXECUTE_STATEMENT_START = "EXECUTE_STATEMENT_START"  #: Запуск statement
    EXECUTE_STATEMENT_FINISH = "EXECUTE_STATEMENT_FINISH"  #: Завершение statement

    EXECUTE_PROCEDURE_START = "EXECUTE_PROCEDURE_START"  #: Запуск procedure
    EXECUTE_PROCEDURE_FINISH = "EXECUTE_PROCEDURE_FINISH"  #: Завершение procedure

    EXECUTE_TRIGGER_START = "EXECUTE_TRIGGER_START"  #: Запуск trigger
    EXECUTE_TRIGGER_FINISH = "EXECUTE_TRIGGER_FINISH"  #: Завершение trigger

    FAILED_EXECUTE_STATEMENT_FINISH = (
        "FAILED EXECUTE_STATEMENT_FINISH"  #: Ошибка завершения выполнения statement
    )
    FAILED_EXECUTE_PROCEDURE_FINISH = (
        "FAILED EXECUTE_PROCEDURE_FINISH"  #: Ошибка завершения выполнения procedure
    )
    FAILED_EXECUTE_TRIGGER_FINISH = (
        "FAILED EXECUTE_TRIGGER_FINISH"  #: Ошибка завершения выполнения trigger
    )

    ERROR_AT_JR = (
        "ERROR AT JR"  #: Ошибка ERROR AT JResultSet::fetchNext (в большинстве случаев)
    )
    ERROR_AT_JS = "ERROR AT JS"  #: Ошибка ERROR AT JStatement::execute и ERROR AT JStatement::openCursor


@dataclass(slots=True)
class EventBase:
    timestamp: datetime  #: Время в формате timestamp
    trace_id: int  #: Идентификатор текущей trace сессии
    hex_trace_id: (
        str  #: Идентификатор текущей trace сессии в 16'ричной системе счисления
    )
    event_type: EventType  #: Тип события представленном в enum EventType


@dataclass(slots=True)
class TraceSessionInfo:
    session_id: int  #: Идентификатор глобальной trace сессии


@dataclass(slots=True)
class AttachmentInfo:
    database_path: (
        str  #: Путь до базы данных или псевдоним использованный для подключения
    )
    attachment_id: int  #: Идентификатор подключения пользователя к базе данных
    user: str  #: Имя пользователя подключаемого к базе данных
    role: str  #: Роль пользователя подключаемого к базе данных
    charset: str  #: Кодировка используемая для подключения к базе данных
    protocol: str  #: Протокол по которому подключается пользователь
    address: str  #: Адрес пользователя подключаемого к базе данных
    port: int  #: Сетевой порт пользователя
    process_path: (
        str  #: Путь до исполняемого файла через который выполняется подключение
    )
    process_id: (
        int  #: Идентификатор процесса исполняемого файла который выполняет подключение
    )


@dataclass(slots=True)
class TransactionInfo:
    transaction_id: int  #: Идентификатор транзакции
    isolation_level: str  #: Уровень изоляции транзакции
    consistency_mode: str  #: Уровень доступа
    lock_mode: str  #: Режим блокировки транзакции
    access_mode: str  #: Режим доступа транзакции


@dataclass(slots=True)
class SqlParam:
    name: str  #: Номер параметра
    dtype: str  #: Тип параметра
    value: str  #: Значение параметра


@dataclass(slots=True)
class PerformanceInfo:
    execute_ms: int  #: Время выполнения запроса
    fetch_count: int  #: Количество выданных данных
    read_count: int  #: Количество чтений
    write_count: int  #: Количество записей
    mark_count: int  #: Количество ...


@dataclass(slots=True)
class PerfomanceTableItem:
    table_name: str  #: Имя затронутой таблицы
    natural_count: int  #: Количество последовательно пройденных записей с первой
    index_count: int  #: Количество выбраных индексов
    update_count: int  #: Количество обновленных записей
    insert_count: int  #: Количество вставленных записей
    delete_count: int  #: Количество удаленных записей
    backout_count: int  #: Не известно
    purge_count: int  #: Не известно
    expunge_count: int  #: Не известно


@dataclass(slots=True)
class PerfomanceTable:
    table = Optional[List[PerfomanceTableItem] | None]
