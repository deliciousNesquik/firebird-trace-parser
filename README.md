# Firebird Trace Log Parser

Библиотека для парсинга и анализа trace логов Firebird Database.

## Описание

FBT (Firebird Trace) — это Python-библиотека для обработки логов трассировки Firebird. Парсер преобразует текстовые логи в структурированные Python объекты, что позволяет проводить анализ производительности, отслеживать SQL-запросы и выявлять узкие места в работе с БД.

## Возможности

- Парсинг всех* типов событий trace лога
- Извлечение метрик производительности
- Анализ параметров SQL-запросов
- Типизированные модели данных (dataclasses)
- Гибкая система обработчиков событий

\* Поддерживается определенные типы событий, по мере обновлений список расширяется!
## Установка

```bash
# Клонирование репозитория
git clone https://github.com/deliciousNesquik/firebird-trace-parser.git
cd firebird-trace-parser

# Установка зависимостей (если используете uv)
uv sync
```

## Быстрый старт

```python
from parser import TraceLogParser
from models import StatementFinishEvent

# Создание парсера
parser = TraceLogParser()

# Парсинг файла
events = parser.parse_file("examples/trace.log")

# Анализ событий
for event in events:
    if isinstance(event, StatementFinishEvent):
        print(f"SQL: {event.sql}")
        print(f"Время выполнения: {event.performance.execute_ms} мс")
        print(f"Записей получено: {event.performance.fetch_count}")
```

## Примеры использования

### Анализ медленных запросов

```python
from parser import TraceLogParser
from models import StatementFinishEvent

parser = TraceLogParser()
events = parser.parse_file("trace.log")

# Найти запросы выполняющиеся дольше 1 секунды
slow_queries = [
    event for event in events
    if isinstance(event, StatementFinishEvent)
    and event.performance.execute_ms > 1000
]

for query in slow_queries:
    print(f"Время: {query.performance.execute_ms} мс")
    print(f"SQL: {query.sql[:100]}...")
    print("-" * 50)
```

### Статистика вызовов триггеров

```python
from collections import Counter
from parser import TraceLogParser
from models import TriggerFinishEvent

parser = TraceLogParser()
events = parser.parse_file("trace.log")

# Подсчет вызовов триггеров
trigger_names = [
    event.trigger_name
    for event in events
    if isinstance(event, TriggerFinishEvent)
]

stats = Counter(trigger_names).most_common()

print("Топ-10 самых вызываемых триггеров:")
for trigger, count in stats[:10]:
    print(f"{trigger}: {count} раз")
```

### Анализ производительности хранимых процедур

```python
from parser import TraceLogParser
from models import ProcedureFinishEvent

parser = TraceLogParser()
events = parser.parse_file("trace.log")

# Группировка по процедурам
procedures = {}
for event in events:
    if isinstance(event, ProcedureFinishEvent):
        name = event.procedure_name
        if name not in procedures:
            procedures[name] = []
        procedures[name].append(event.performance.execute_ms)

# Средние значения
for proc_name, times in procedures.items():
    avg_time = sum(times) / len(times)
    print(f"{proc_name}:")
    print(f"  Вызовов: {len(times)}")
    print(f"  Среднее время: {avg_time:.2f} мс")
    print(f"  Макс. время: {max(times)} мс")
```

### Мониторинг подключений

```python
from parser import TraceLogParser
from models import AttachDatabaseEvent, DetachDatabaseEvent

parser = TraceLogParser()
events = parser.parse_file("trace.log")

# Анализ подключений
attachments = [e for e in events if isinstance(e, AttachDatabaseEvent)]
detachments = [e for e in events if isinstance(e, DetachDatabaseEvent)]

print(f"Всего подключений: {len(attachments)}")
print(f"Всего отключений: {len(detachments)}")

# Группировка по пользователям
users = {}
for attach in attachments:
    user = attach.attachment.user
    users[user] = users.get(user, 0) + 1

print("\nПодключения по пользователям:")
for user, count in sorted(users.items(), key=lambda x: -x[1]):
    print(f"  {user}: {count}")
```

## Структура проекта

```
.
├── main.py         # Пример использования
├── matcher         # Регулярные выражения для парсинга
│   ├── __init__.py
│   └── rules.py    # Регулярные выражения
├── models          # Модели данных и enums
│   ├── __init__.py
│   ├── enums.py    # Enum событий
│   └── models.py   # Модели событий
├── parser          # Движок парсера
│   ├── __init__.py
│   ├── engine.py   # Парсер
│   ├── handlers.py # Обработчик
│   └── utils.py    # Вспомогательные функции
├── pyproject.toml  # Конфигурация проекта
├── README.md       # Документация
```

## Поддерживаемые типы событий

| Событие | Описание |
|---------|----------|
| `TRACE_INIT` | Инициализация trace сессии |
| `TRACE_FINI` | Завершение trace сессии |
| `ATTACH_DATABASE` | Подключение к БД |
| `DETACH_DATABASE` | Отключение от БД |
| `EXECUTE_STATEMENT_START` | Начало выполнения SQL |
| `EXECUTE_STATEMENT_FINISH` | Завершение выполнения SQL |
| `EXECUTE_PROCEDURE_START` | Начало выполнения процедуры |
| `EXECUTE_PROCEDURE_FINISH` | Завершение выполнения процедуры |
| `EXECUTE_TRIGGER_START` | Начало выполнения триггера |
| `EXECUTE_TRIGGER_FINISH` | Завершение выполнения триггера |

## Модели данных

Все события наследуются от базового класса `EventBase`:

```python
@dataclass
class EventBase:
    timestamp: datetime        # Время события
    trace_id: int             # ID trace сессии
    hex_trace_id: str         # ID в hex формате
    event_type: EventType     # Тип события
```

### Дополнительные модели

- **AttachmentInfo** — информация о подключении (пользователь, адрес, процесс)
- **TransactionInfo** — параметры транзакции (изоляция, режим блокировки)
- **SqlParam** — параметры SQL запроса
- **PerformanceInfo** — метрики производительности (время, чтения, записи)

## Продвинутое использование

### Кастомный обработчик событий

```python
from parser import EventHandler, TraceLogParser
from models import StatementFinishEvent

class MyCustomHandler(EventHandler):
    def _handle_statement_finish(self, block_header, body_lines):
        event = super()._handle_statement_finish(block_header, body_lines)
        
        # Ваша дополнительная логика
        if event and event.performance.execute_ms > 5000:
            print(f"⚠️  Медленный запрос обнаружен: {event.sql[:50]}...")
        
        return event

# Использование
parser = TraceLogParser(handler=MyCustomHandler())
parser.parse_file("trace.log")
```

### Потоковая обработка больших файлов

```python
from parser import TraceLogParser

parser = TraceLogParser()

# Обработка файла построчно (экономия памяти)
with open("huge_trace.log", "r", encoding="utf-8") as f:
    for event in parser.parse_stream(f):
        # Обработка события сразу без накопления в памяти
        process_event(event)
```

## Производительность

Парсер оптимизирован для работы с большими логами:

- Использование `regex` для эффективного поиска
- Ленивая обработка через генераторы
- Минимальное потребление памяти в stream режиме
- `slots=True` в dataclass для экономии памяти

## Roadmap

- [ ] CLI утилита для анализа и статистики
- [ ] Экспорт статистики в JSON/CSV
- [ ] Поддержка real-time мониторинга

## Лицензия

MIT License

## Автор

<div align="center">

**Создано с ❤️ для Firebird комьюнити и РЭЙД-21 :)**

</div>