# matcher/rules.py

import regex

"""
Регулярное выражение для парсинга заголовка блока события трассировки.

Пример целевой строки:
    2026-04-14T10:20:01.1620 (437236:0x7f3133ba1dc0) TRACE_INIT

Извлекаемые именованные группы:
    * `ts`           : Временная метка события (timestamp).
    * `trace_id`     : Идентификатор транзакции/трейса в десятичной системе счисления.
    * `hex_trace_id` : Идентификатор транзакции/трейса в шестнадцатеричной системе счисления.
    * `event_type`   : Тип зарегистрированного события (например, TRACE_INIT).
"""
RE_BLOCK_HEADER = regex.compile(
    r"^(?<ts>\d{4}-\d{2}-\d{2}T[\d:.]+)\s+"
    r"\((?<trace_id>\d+):(?<hex_trace_id>0x[0-9a-f]+)\)\s+"
    r"(?<event_type>[A-Z_ ]+)"
)


"""
Регулярное выражение для извлечения идентификатора сессии трассировки.

Идентификатор сессии уникален для каждого файла лога (например, 
для разных дат будут сформированы разные идентификаторы сессий).

Пример целевой строки:
    SESSION_994

Извлекаемые именованные группы:
    * `session_id` : Числовой идентификатор текущей сессии лог-файла.
"""
RE_SESSION = regex.compile(r"^\s+SESSION_(?<session_id>\d+)\s*$")


"""
Регулярное выражение для извлечения детализированной информации о подключении к БД.

Пример целевой строки:
    /interbas/reid_2022.gdb (ATT_11335646, REPL: NONE, WIN1251, TCPv4: 192.168.3.218/52931)

Извлекаемые именованные группы:
    * `database_path` : Абсолютный или относительный путь до файла базы данных.
    * `attachment_id` : Уникальный идентификатор соединения (например, 11335646).
    * `user`          : Имя пользователя, инициировавшего подключение.
    * `role`          : Роль пользователя в базе данных (например, NONE).
    * `charset`       : Используемая кодировка подключения (например, WIN1251).
    * `protocol`      : Сетевой протокол подключения (например, TCPv4).
    * `address`       : (Опционально) IP-адрес клиента.
    * `port`          : (Опционально) Сетевой порт клиента.
"""
RE_ATTACHMENT = regex.compile(
    r"^\s+(?<database_path>.+?)\s+"
    r"\((ATT_(?<attachment_id>\d+)),\s*"
    r"(?<user>[^:]+):(?<role>\S+),\s*"
    r"(?<charset>\S+),\s*"
    r"(?<protocol>[^:)]+)"
    r"(?::(?<address>[^/]+)"
    r"/(?<port>\d+))?\)"
)


"""
Регулярное выражение для извлечения информации о процессе клиентского приложения.

Пример целевой строки:
    C:\Python310-32\python.exe:2540

Извлекаемые именованные группы:
    * `process_path` : Полный путь до исполняемого файла приложения на стороне клиента.
    * `process_id`   : Идентификатор процесса (PID) в операционной системе клиента.
"""
RE_PROCESS = regex.compile(r"^\s+(?<process_path>.+):(?<process_id>\d+)\s*$")


"""
Регулярное выражение для извлечения идентификатора SQL-оператора.

Пример:
    Statement 556761380:

Группы:
    * statement_id : Уникальный идентификатор SQL-выражения
"""
RE_STATEMENT_HEADER = regex.compile(r"^Statement\s+(?<statement_id>\d+):\s*$")


"""
Регулярное выражение для извлечения SQL-текста.

Пример:
    -------------------------------------------------------------------------------
    select * from table where id = ?

Особенности:
    * SQL может быть многострочным
    * Завершается перед:
        - параметрами (paramX)
        - блоком статистики (records fetched)
        - концом блока

Группы:
    * sql : полный SQL текст
"""
RE_SQL_BLOCK = regex.compile(
    r"^-{10,}\n(?<sql>.*?)(?=\n\s*(param\d+\s*=|\d+\s+records\s+fetched|$))",
    regex.DOTALL,
    regex.S,
    regex.M,
)


"""
Регулярное выражение для извлечения параметров SQL.

Примеры:
    param0 = bigint, "195"
    param1 = varchar(50), ""
    param2 = double precision, "1"
    param3 = numeric(18,4), "20376.12"
    param4 = varchar(32000), "<NULL>"

Группы:
    * name  : имя параметра (param0, param1...)
    * dtype : тип данных (может содержать пробелы и параметры)
    * value : строковое значение параметра

Особенности:
    * dtype извлекается полностью до первой запятой
    * поддерживает сложные типы (double precision, numeric(18,4))
    * value всегда в кавычках
"""
RE_PARAM = regex.compile(
    r"^\s*(?<name>param\d+)\s*=\s*(?<dtype>[^,]+?)\s*,\s*(?:\"(?<value>.*?)\"|(?<value_null>NULL))\s*$"
)


"""
Регулярное выражение для извлечения информации о транзакции.

Поддерживаемые форматы:
    (TRA_123, READ_COMMITTED | READ_CONSISTENCY | NOWAIT | READ_WRITE)
    (TRA_123, CONCURRENCY | WAIT | READ_WRITE)

Группы:
    * transaction_id : ID транзакции
    * isolation      : первый режим (всегда есть)
    * consistency    : второй режим (опционально)
    * lock           : третий режим (опционально)
    * access         : четвёртый режим (опционально)

Особенности:
    * количество режимов может быть 1–4
    * пробелы вокруг "|" игнорируются
    * порядок сохраняется как в логе
"""
RE_TRANSACTION = regex.compile(
    r"^\s*\(TRA_(?<transaction_id>\d+),\s*"
    r"(?<isolation>[^|)]+)"
    r"(?:\s*\|\s*(?<consistency>[^|)]+))?"
    r"(?:\s*\|\s*(?<lock>[^|)]+))?"
    r"(?:\s*\|\s*(?<access>[^|)]+))?"
    r"\s*\)"
)


"""
Регулярное выражение для извлечения метрик выполнения.

Пример:
    377 ms, 6 read(s), 469 write(s), 1446 fetch(es), 1440 mark(s)

Группы:
    * execute_ms
    * read
    * write
    * fetch
    * mark

Все группы кроме execute_ms — опциональны.
"""
RE_PERFORMANCE = regex.compile(
    r"^\s*(?<execute_ms>\d+)\s+ms,\s*"
    r"(?:(?<read>\d+)\s+read\(s\),\s*)?"
    r"(?:(?<write>\d+)\s+write\(s\),\s*)?"
    r"(?:(?<fetch>\d+)\s+fetch\(es\),\s*)?"
    r"(?:(?<mark>\d+)\s+mark\(s\))?"
)


"""
Регулярное выражение для извлечения количества полученных записей (fetch count).

Пример:
    6 records fetched
    60 records fetched

Группы:
    * fetch_count : количество извлечённых записей

Особенности:
    * строка может иметь отступы
    * всегда находится перед блоком performance (ms, read, fetch...)
"""
RE_FETCHED = regex.compile(r"^\s*(?<fetch_count>\d+)\s+records\s+fetched\s*$")


RE_TABLE_ROW = regex.compile(
    r"^\s*(?<table>\S+)\s+"
    r"(?<natural>\d+)?\s*"
    r"(?<index>\d+)?\s*"
    r"(?<update>\d+)?\s*"
    r"(?<insert>\d+)?\s*"
    r"(?<delete>\d+)?\s*"
    r"(?<backout>\d+)?\s*"
    r"(?<purge>\d+)?\s*"
    r"(?<expunge>\d+)?\s*$"
)


"""
Регулярное выражение для извлечения имени хранимой процедуры.

Примеры:
    Procedure TRT$CHECK_GISMT_ON_RASHOD:
    Procedure HIS$REG_TIMESTAMP:

Группы:
    * procedure_name : имя процедуры

Особенности:
    * имя может содержать символ '$'
    * имя не содержит пробелов
    * строка всегда заканчивается двоеточием
"""
RE_PROCEDURE_HEADER = regex.compile(r"^Procedure\s+(?<procedure_name>[^\s:]+)\s*:\s*$")

"""
Регулярное выражение для извлечения информации о триггере.

Примеры:
    Trigger NACLSPEC_AIU0 FOR NACLSPEC (AFTER INSERT):
    Trigger DELIVERYSPEC_PARTY_BIUD0 FOR DELIVERYSPEC_PARTY (BEFORE INSERT):
    Trigger KPK$SERVCHAINSHED_BU0 FOR KPK$SERVCHAINSHED (BEFORE UPDATE):

Извлекаемые именованные группы:
    * `trigger_name` : имя триггера
    * `table`        : имя таблицы, к которой привязан триггер
    * `timing`       : момент срабатывания триггера (BEFORE | AFTER)
    * `event`        : тип события (INSERT | UPDATE | DELETE)

Особенности:
    * имя триггера и таблицы не содержат пробелов
    * имя триггера может содержать символ '$'
    * блок (timing event) всегда заключён в круглые скобки
    * строка всегда заканчивается двоеточием
    * между элементами допускаются произвольные пробелы
"""
RE_TRIGGER_HEADER = regex.compile(
    r"^Trigger\s+"
    r"(?<trigger_name>[^\s]+)\s+FOR\s+"
    r"(?<table>[^\s]+)\s+"
    r"\((?<timing>BEFORE|AFTER)\s+(?<event>INSERT|UPDATE|DELETE)\)"
    r"\s*:\s*$"
)
