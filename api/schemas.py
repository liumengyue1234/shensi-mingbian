"""
请求/响应 Schema 定义（使用 dataclass 保持轻量）
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ChatRequest:
    query: str
    session_id: str = "default"


@dataclass
class CaseSearchRequest:
    keywords: Optional[List[str]] = None
    long_text: Optional[str] = None
    page_no: int = 1
    page_size: int = 5
    court_level: Optional[List[str]] = None
    case_year_start: Optional[str] = None
    case_year_end: Optional[str] = None


@dataclass
class LawSearchRequest:
    keywords: List[str] = field(default_factory=list)
    field_name: str = "semantic"   # semantic | title
    page_no: int = 1
    page_size: int = 5


@dataclass
class StrategyRequest:
    complaint_text: str
    case_type: str = "civil"       # civil | criminal | administrative


@dataclass
class ExportRequest:
    title: str
    content: str
