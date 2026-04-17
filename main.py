from parser import TraceLogParser
from models import StatementFinishEvent

parser = TraceLogParser()
events = parser.parse_file("examples/trace.log")

# Найти запросы выполняющиеся дольше 1 секунды
slow_queries = [
    event for event in events
    if isinstance(event, StatementFinishEvent)
    and event.performance.execute_ms > 100000
]

for query in slow_queries:
    print(f"Время: {query.performance.execute_ms} мс")
    print(f"SQL: {query.sql[:100]}...")
    print("-" * 50)