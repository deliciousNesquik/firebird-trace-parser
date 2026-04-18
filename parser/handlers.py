"""Обработчики событий trace лога."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from models import *
from matcher import *
from parser.utils import (
    parse_attachment_info,
    parse_transaction_info,
    parse_params,
    parse_performance,
)


class EventHandler:
    """Базовый обработчик событий trace лога."""
    
    def handle(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[EventBase]:
        """
        Обрабатывает блок события.
        
        Args:
            block_header: Заголовок блока
            body_lines: Строки тела блока
            
        Returns:
            Объект события или None
        """
        event_type = block_header["event_type"].strip()
        
        # Маршрутизация по типу события
        handlers = {
            EventType.TRACE_INIT: self._handle_trace_init,
            EventType.TRACE_FINI: self._handle_trace_fini,
            EventType.ATTACH_DATABASE: self._handle_attach,
            EventType.DETACH_DATABASE: self._handle_detach,
            EventType.EXECUTE_STATEMENT_START: self._handle_statement_start,
            EventType.EXECUTE_STATEMENT_FINISH: self._handle_statement_finish,
            EventType.EXECUTE_PROCEDURE_START: self._handle_procedure_start,
            EventType.EXECUTE_PROCEDURE_FINISH: self._handle_procedure_finish,
            EventType.EXECUTE_TRIGGER_START: self._handle_trigger_start,
            EventType.EXECUTE_TRIGGER_FINISH: self._handle_trigger_finish,
        }
        
        handler_func = handlers.get(EventType(event_type))
        if handler_func:
            return handler_func(block_header, body_lines)
        
        return None
    
    def _create_base_kwargs(self, block_header: Dict[str, Any]) -> Dict[str, Any]:
        """Создает базовые аргументы для события."""
        return {
            "timestamp": datetime.fromisoformat(block_header["ts"]),
            "trace_id": int(block_header["trace_id"]),
            "hex_trace_id": block_header["hex_trace_id"],
            "event_type": EventType(block_header["event_type"].strip()),
        }
    
    def _handle_trace_init(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[TraceInitEvent]:
        """Обработка TRACE_INIT."""
        base_kwargs = self._create_base_kwargs(block_header)
        session_info = self._parse_session_info(body_lines)
        
        return TraceInitEvent(**base_kwargs, session=session_info)
    
    def _handle_trace_fini(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[TraceFinishEvent]:
        """Обработка TRACE_FINI."""
        base_kwargs = self._create_base_kwargs(block_header)
        session_info = self._parse_session_info(body_lines)
        
        return TraceFinishEvent(**base_kwargs, session=session_info)
    
    def _handle_attach(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[AttachDatabaseEvent]:
        """Обработка ATTACH_DATABASE."""
        base_kwargs = self._create_base_kwargs(block_header)
        attachment = parse_attachment_info(body_lines)
        
        return AttachDatabaseEvent(**base_kwargs, attachment=attachment)
    
    def _handle_detach(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[DetachDatabaseEvent]:
        """Обработка DETACH_DATABASE."""
        base_kwargs = self._create_base_kwargs(block_header)
        attachment = parse_attachment_info(body_lines)
        
        return DetachDatabaseEvent(**base_kwargs, attachment=attachment)
    
    def _handle_statement_start(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[StatementStartEvent]:
        """Обработка EXECUTE_STATEMENT_START."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_statement_data(body_lines)
        
        return StatementStartEvent(**base_kwargs, **data)
    
    def _handle_statement_finish(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[StatementFinishEvent]:
        """Обработка EXECUTE_STATEMENT_FINISH."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_statement_data(body_lines, include_performance=True)
        
        return StatementFinishEvent(**base_kwargs, **data)
    
    def _handle_procedure_start(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[ProcedureStartEvent]:
        """Обработка EXECUTE_PROCEDURE_START."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_procedure_data(body_lines)
        
        return ProcedureStartEvent(**base_kwargs, **data)
    
    def _handle_procedure_finish(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[ProcedureFinishEvent]:
        """Обработка EXECUTE_PROCEDURE_FINISH."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_procedure_data(body_lines, include_performance=True)
        
        return ProcedureFinishEvent(**base_kwargs, **data)
    
    def _handle_trigger_start(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[TriggerStartEvent]:
        """Обработка EXECUTE_TRIGGER_START."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_trigger_data(body_lines)
        
        return TriggerStartEvent(**base_kwargs, **data)
    
    def _handle_trigger_finish(
        self,
        block_header: Dict[str, Any],
        body_lines: List[str]
    ) -> Optional[TriggerFinishEvent]:
        """Обработка EXECUTE_TRIGGER_FINISH."""
        base_kwargs = self._create_base_kwargs(block_header)
        data = self._parse_trigger_data(body_lines, include_performance=True)
        
        return TriggerFinishEvent(**base_kwargs, **data)
    
    def _parse_session_info(self, body_lines: List[str]) -> Optional[TraceSessionInfo]:
        """Парсит информацию о сессии."""
        for line in body_lines:
            m = RE_SESSION.match(line)
            if m:
                return TraceSessionInfo(
                    session_id=int(m.group("session_id"))
                )
        return None
    
    def _parse_statement_data(
        self,
        body_lines: List[str],
        include_performance: bool = False
    ) -> Dict[str, Any]:
        """Парсит данные statement."""
        attachment = None
        transaction = None
        statement_id = None
        sql = None
        params = []
        performance = None
        performance_table = None
        
        i = 0
        while i < len(body_lines):
            line = body_lines[i]
            
            # Attachment
            if attachment is None:
                attachment = parse_attachment_info([line])
                if attachment:
                    i += 1
                    continue
            
            # Process (дополнение attachment)
            m = RE_PROCESS.match(line)
            if m and attachment:
                attachment.process_path = m.group("process_path")
                attachment.process_id = int(m.group("process_id"))
                i += 1
                continue
            
            # Transaction
            if transaction is None:
                transaction = parse_transaction_info([line])
                if transaction:
                    i += 1
                    continue
            
            # Statement ID
            m = RE_STATEMENT_HEADER.match(line)
            if m:
                statement_id = int(m.group("statement_id"))
                i += 1
                continue
            
            # SQL block
            if line.strip().startswith("-----"):
                sql_lines = []
                i += 1
                while i < len(body_lines):
                    l = body_lines[i]
                    if RE_PARAM.match(l) or RE_FETCHED.match(l):
                        break
                    sql_lines.append(l)
                    i += 1
                sql = "".join(sql_lines).strip()
                continue
            
            # Params
            param = parse_params([line])
            if param:
                params.extend(param)
                i += 1
                continue
            
            # Performance
            if include_performance and performance is None:
                performance = parse_performance(body_lines[i:])
                if performance:
                    i += 1
                    continue
            
            i += 1
        
        result = {
            "attachment": attachment,
            "transaction": transaction,
            "statement_id": statement_id,
            "sql": sql,
            "params": params,
        }
        
        if include_performance:
            result["performance"] = performance
            result["performance_table"] = performance_table
        
        return result
    
    def _parse_procedure_data(
        self,
        body_lines: List[str],
        include_performance: bool = False
    ) -> Dict[str, Any]:
        """Парсит данные procedure."""
        attachment = parse_attachment_info(body_lines)
        transaction = parse_transaction_info(body_lines)
        params = parse_params(body_lines)
        
        procedure_name = None
        for line in body_lines:
            m = RE_PROCEDURE_HEADER.match(line)
            if m:
                procedure_name = m.group("procedure_name")
                break
        
        result = {
            "attachment": attachment,
            "transaction": transaction,
            "procedure_name": procedure_name,
            "params": params,
        }
        
        if include_performance:
            result["performance"] = parse_performance(body_lines)
            result["performance_table"] = None
        
        return result
    
    def _parse_trigger_data(
        self,
        body_lines: List[str],
        include_performance: bool = False
    ) -> Dict[str, Any]:
        """Парсит данные trigger."""
        attachment = parse_attachment_info(body_lines)
        transaction = parse_transaction_info(body_lines)
        
        trigger_name = None
        table = None
        timing = None
        event = None
        
        for line in body_lines:
            m = RE_TRIGGER_HEADER.match(line)
            if m:
                trigger_name = m.group("trigger_name")
                table = m.group("table")
                timing = m.group("timing")
                event = m.group("event")
                break
        
        result = {
            "attachment": attachment,
            "transaction": transaction,
            "trigger_name": trigger_name,
            "table": table,
            "timing": timing,
            "event": event,
        }
        
        if include_performance:
            result["performance"] = parse_performance(body_lines)
            result["performance_table"] = None
        
        return result