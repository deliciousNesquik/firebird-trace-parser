"""Основной движок парсера trace логов."""

from pathlib import Path
from typing import List, Optional, Union, Iterator
from models import *
from matcher import *
from parser.handlers import EventHandler


class TraceLogParser:
    """
    Парсер trace логов Firebird.
    
    Примеры использования:
        >>> parser = TraceLogParser()
        >>> events = parser.parse_file("trace.log")
        >>> for event in events:
        ...     print(event.event_type)
        
        >>> # С пользовательским обработчиком
        >>> handler = MyCustomHandler()
        >>> parser = TraceLogParser(handler=handler)
        >>> parser.parse_file("trace.log")
    """
    
    def __init__(self, handler: Optional[EventHandler] = None):
        """
        Инициализация парсера.
        
        Args:
            handler: Обработчик событий (опционально)
        """
        self.handler = handler or EventHandler()
        self._current_block: Optional[dict] = None
        self._pending_lines: List[str] = []
        self._events: List[EventBase] = []
    
    def parse_file(
        self,
        filepath: Union[str, Path],
        encoding: str = "utf-8"
    ) -> List[EventBase]:
        """
        Парсит файл trace лога.
        
        Args:
            filepath: Путь к файлу лога
            encoding: Кодировка файла
            
        Returns:
            Список распарсенных событий
        """
        self._events = []
        
        with open(filepath, "r", encoding=encoding, errors="ignore") as f:
            for line in f:
                self._process_line(line)
        
        # Обработка последнего блока
        if self._current_block is not None:
            self._flush_block()
        
        return self._events
    
    def parse_lines(self, lines: List[str]) -> List[EventBase]:
        """
        Парсит список строк.
        
        Args:
            lines: Список строк лога
            
        Returns:
            Список распарсенных событий
        """
        self._events = []
        
        for line in lines:
            self._process_line(line)
        
        if self._current_block is not None:
            self._flush_block()
        
        return self._events
    
    def parse_stream(self, lines: Iterator[str]) -> Iterator[EventBase]:
        """
        Парсит поток строк (генератор).
        
        Args:
            lines: Итератор строк
            
        Yields:
            Распарсенные события по мере обработки
        """
        for line in lines:
            block_match = RE_BLOCK_HEADER.match(line)
            
            if block_match is not None:
                if self._current_block is not None:
                    event = self._flush_block()
                    if event:
                        yield event
                
                self._current_block = block_match.groupdict()
                self._pending_lines = []
            else:
                if self._current_block is not None and line.strip():
                    self._pending_lines.append(line)
        
        # Последний блок
        if self._current_block is not None:
            event = self._flush_block()
            if event:
                yield event
    
    def _process_line(self, line: str) -> None:
        """Обработка одной строки лога."""
        block_match = RE_BLOCK_HEADER.match(line)
        
        if block_match is not None:
            if self._current_block is not None:
                self._flush_block()
            
            self._current_block = block_match.groupdict()
            self._pending_lines = []
        else:
            if self._current_block is not None and line.strip():
                self._pending_lines.append(line)
    
    def _flush_block(self) -> Optional[EventBase]:
        """Обработка накопленного блока."""
        if self._current_block is None:
            return None
        
        event = self.handler.handle(
            self._current_block,
            self._pending_lines
        )
        
        if event:
            self._events.append(event)
        
        return event