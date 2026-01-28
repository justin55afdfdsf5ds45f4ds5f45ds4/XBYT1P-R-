"""
Data Models for XBYT1P&%R$@
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class StackFrame(BaseModel):
    """Single frame in a stack trace"""
    file: str
    line: int
    function: Optional[str] = None
    code: Optional[str] = None


class FileRelation(BaseModel):
    """Relationship between files"""
    file: str
    line: int
    depends_on: str
    depends_on_line: int
    relationship_type: str  # "calls", "imports", etc.


class ErrorReport(BaseModel):
    """Structured error information"""
    error_type: str
    error_message: str
    file_path: str
    line_number: int
    function_name: Optional[str] = None
    stack_trace: List[StackFrame]
    file_content: Optional[str] = None
    related_files: List[FileRelation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FixResult(BaseModel):
    """Result of fix generation"""
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool
    message: Optional[str] = None
    error_report: Optional[ErrorReport] = None
    fixed_code: Optional[str] = None
    diff: Optional[str] = None
    cost: float = 0.0
    model_used: Optional[str] = None
    fix_strategy: Optional[str] = None


class TestResult(BaseModel):
    """Result of sandbox testing"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class LearnedFix(BaseModel):
    """A fix stored in memory"""
    error_signature: str  # Hash of error type + context
    error_type: str
    file_pattern: str  # e.g., "*.py", "api/*.py"
    fix_strategy: str
    fixed_code: Optional[str] = None  # Store actual fixed code
    success_count: int = 0
    failure_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
