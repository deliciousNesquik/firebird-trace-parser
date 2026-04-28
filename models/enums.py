from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class EventType(str, Enum):
    """
    Типы событий, передаваемых через механизм 'trace' базы данных Firebird.

    Каждый элемент перечисления соответствует определённому событию в логирование/трассировке Firebird.

    Пример использования:
        >>> event = EventType.TRACE_INIT
        >>> isinstance(event, str)
        True
        >>> event.name
        'TRACE_INIT'
    """

    TRACE_INIT = "TRACE_INIT"
    """ Инициализация trace‑сессии """

    TRACE_FINI = "TRACE_FINI"
    """ Завершение trace‑сессии """

    ATTACH_DATABASE = "ATTACH_DATABASE"
    """ Подключение к базе данных """

    DETACH_DATABASE = "DETACH_DATABASE"
    """ Отключение от базы данных """

    EXECUTE_STATEMENT_START = "EXECUTE_STATEMENT_START"
    """ Начало выполнения statement """

    EXECUTE_STATEMENT_FINISH = "EXECUTE_STATEMENT_FINISH"
    """ Завершение выполнения statement """

    EXECUTE_PROCEDURE_START = "EXECUTE_PROCEDURE_START"
    """ Начало выполнения процедуры """

    EXECUTE_PROCEDURE_FINISH = "EXECUTE_PROCEDURE_FINISH"
    """ Завершение выполнения процедуры """

    EXECUTE_TRIGGER_START = "EXECUTE_TRIGGER_START"
    """ Начало выполнения триггера """

    EXECUTE_TRIGGER_FINISH = "EXECUTE_TRIGGER_FINISH"
    """ Завершение выполнения триггера """

    FAILED_EXECUTE_STATEMENT_FINISH = "FAILED EXECUTE_STATEMENT_FINISH"
    """ Ошибка завершения выполнения statement """

    FAILED_EXECUTE_PROCEDURE_FINISH = "FAILED EXECUTE_PROCEDURE_FINISH"
    """ Ошибка завершения выполнения процедуры """

    FAILED_EXECUTE_TRIGGER_FINISH = "FAILED EXECUTE_TRIGGER_FINISH"
    """ Ошибка завершения выполнения триггера """

    ERROR_AT_JR = "ERROR AT JR"
    """ Ошибка ERROR AT JResultSet::fetchNext (в большинстве случаев) """

    ERROR_AT_JS = "ERROR AT JS"
    """ Ошибка ERROR AT JStatement::execute и ERROR AT JStatement::openCursor """


@dataclass(slots=True)
class EventBase:
    """
    Базовая модель события трассировки Firebird.

    Содержит общие поля, присутствующие во всех типах событий,
    передаваемых через механизм 'trace' базы данных Firebird.
    """

    timestamp: datetime
    """ Время события в формате timestamp 2026-01-01T00:00:00.0000 """

    trace_id: int
    """ Идентификатор текущей trace‑сессии """

    hex_trace_id: str
    """ Идентификатор trace‑сессии в 16‑ричной системе счисления """

    event_type: EventType
    """ Тип события, представленный в enum EventType """


@dataclass(slots=True)
class TraceSessionInfo:
    """
    Информация о глобальной сессии трассировки Firebird.

    Описывает основной контекст trace‑сессии, в рамках которой
    будут фиксироваться события подключений, транзакций и запросов.
    """

    session_id: int
    """ Идентификатор глобальной trace‑сессии """


@dataclass(slots=True)
class AttachmentInfo:
    """
    Информация о подключении пользователя к базе данных Firebird.

    Содержит реквизиты подключения, которые используются в trace‑событиях
    ATTACH_DATABASE / DETACH_DATABASE и в связанных с ними запросах.
    """

    database_path: str
    """ Путь до базы данных или псевдоним, использованный для подключения """

    attachment_id: int
    """ Идентификатор подключения пользователя к базе данных """

    user: str
    """ Имя пользователя, подключаемого к базе данных """

    role: str
    """ Роль пользователя, подключаемого к базе данных """

    charset: str
    """ Кодировка, используемая для подключения к базе данных """

    protocol: str
    """ Протокол, по которому подключается пользователь """

    address: str
    """ Адрес пользователя, подключаемого к базе данных """

    port: int
    """ Сетевой порт пользователя """

    process_path: str|None
    """ Путь до исполняемого файла, через который выполняется подключение """

    process_id: int|None
    """ Идентификатор процесса, исполняемого файла, который выполняет подключение на стороне клиента """


@dataclass(slots=True)
class TransactionInfo:
    """
    Информация о транзакции в рамках trace‑сессии Firebird.

    Содержит параметры транзакции, которые сопровождают события
    начала/завершения транзакций и связанные с ними события.
    """

    transaction_id: int
    """ Идентификатор транзакции """

    isolation_level: str
    """ Уровень изоляции транзакции """

    consistency_mode: str
    """ Уровень доступа """

    lock_mode: str
    """ Режим блокировки транзакции """

    access_mode: str
    """ Режим доступа транзакции """


@dataclass(slots=True)
class SqlParam:
    """
    Описание одного параметра SQL‑запроса в trace‑механизме Firebird.

    Используется для отображения значений параметров при выполнении
    statement или procedure в трассировке.
    """

    name: str
    """ Номер параметра """

    dtype: str
    """ Тип параметра в терминах Firebird """

    value: str
    """ Значение параметра в строковом представлении """


@dataclass(slots=True)
class PerformanceInfo:
    """
    Общая информация о производительности выполнения SQL‑операции.

    Содержит суммарные метрики по времени и количеству операций
    для одного запроса или блока операций.
    """

    execute_ms: int
    """ Время выполнения запроса """

    fetch_count: int
    """ Количество выданных данных """

    read_count: int
    """ Количество чтений """

    write_count: int
    """ Количество записей """

    mark_count: int
    """ Количество внутренних отметок / маркеров (страниц, записей и т.п.) """


@dataclass(slots=True)
class PerformanceTableItem:
    """
    Статистика по одной таблице, затронутой в рамках операции.

    Описывает, сколько записей было прочитано, изменено, вставлено,
    удалено и т.п. для конкретной таблицы.
    """

    table_name: str
    """ Имя затронутой таблицы """

    natural_count: int
    """ Количество последовательно пройденных записей с первой """

    index_count: int
    """ Количество использований индексов """

    update_count: int
    """ Количество обновлённых записей """

    insert_count: int
    """ Количество вставленных записей """

    delete_count: int
    """ Количество удалённых записей """

    backout_count: int
    """ Количество отмененных изменений """

    purge_count: int
    """ Количество физических удалений """

    expunge_count: int
    """ Количество очищенных томов/записей """


@dataclass(slots=True)
class PerformanceTable:
    """
    Контейнер списка статистик по таблицам для trace‑операции.

    Содержит один список элементов `PerformanceTableItem`,
    представляющих затронутые таблицы и их статистику.
    """

    table = Optional[List[PerformanceTableItem] | None]
