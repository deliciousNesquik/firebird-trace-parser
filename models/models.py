# models/models.py

from dataclasses import dataclass
from models.enums import *
from typing import List


@dataclass(slots=True)
class TraceInitEvent(EventBase):
    session: TraceSessionInfo


@dataclass(slots=True)
class TraceFinishEvent(EventBase):
    session: TraceSessionInfo


@dataclass(slots=True)
class AttachDatabaseEvent(EventBase):
    attachment: AttachmentInfo


@dataclass(slots=True)
class DetachDatabaseEvent(EventBase):
    attachment: AttachmentInfo


@dataclass(slots=True)
class StatementEventBase(EventBase):
    attachment: AttachmentInfo
    transaction: TransactionInfo
    statement_id: int
    sql: str
    params: List[SqlParam]


@dataclass(slots=True)
class ProcedureEventBase(EventBase):
    attachment: AttachmentInfo
    transaction: TransactionInfo
    statement_id: int
    procedure_name: str
    params: List[SqlParam]


@dataclass(slots=True)
class TriggerEventBase(EventBase):
    attachment: AttachmentInfo
    transaction: TransactionInfo
    statement_id: int
    trigger_name: str
    table: str
    timing: str
    event: str


@dataclass(slots=True)
class StatementStartEvent(StatementEventBase):
    pass


@dataclass(slots=True)
class StatementFinishEvent(StatementEventBase):
    performance: PerformanceInfo
    performance_table: PerfomanceTable


@dataclass(slots=True)
class ProcedureStartEvent(ProcedureEventBase):
    pass


@dataclass(slots=True)
class ProcedureFinishEvent(ProcedureEventBase):
    performance: PerformanceInfo
    performance_table: PerfomanceTable


@dataclass(slots=True)
class TriggerStartEvent(TriggerEventBase):
    pass


@dataclass(slots=True)
class TriggerFinishEvent(TriggerEventBase):
    performance: PerformanceInfo
    performance_table: PerfomanceTable
