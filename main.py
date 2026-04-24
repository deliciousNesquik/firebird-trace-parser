import os

from parser import TraceLogParser
from matcher import loader

rules = loader.load_rules(
    "C:\\Users\\BERDIN.A\\PycharmProjects\\firebird-trace-parser\\matcher\\rules.toml"
)
parser = TraceLogParser(rules)


users = {}
# Обработка файла построчно (экономия памяти)
files = os.listdir("examples/")

for file in files[4:6]:
    with open(f"examples/{file}", "r", errors="ignore", encoding="utf-8") as f:
        for event in parser.parse_stream(f):
            pass
