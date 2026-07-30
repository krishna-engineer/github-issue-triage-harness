from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

class IssueType(str, Enum):
    """
    No ordering between values
    """
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    OTHER="other"

class Urgency(str, Enum):
    """
    Values have ordering and direction between them
    """
    CRITICAL = "critical"
    NORMAL = "normal"
    LOW = "low"

class ErrorStatus(str, Enum):
    OK = "ok"
    MALFORMED_JSON = "malformed_json"
    MISSING_OUTPUT_FIELD = "missing_output_field"
    INVALID_ENUM_VALUE = "invalid_enum_value"
    TRUNCATED = "truncated"
    API_FAILURE = "api_failure"


URGENCY_ORDER: dict[Urgency, int] = {
    Urgency.LOW: 0,
    Urgency.NORMAL: 1,
    Urgency.CRITICAL: 2
}

class GitIssue(BaseModel):
    """
    A raw GitHub issue. Service takes title+body, not a URL.
    """
    issue_id: str
    title: str
    body: str
    context: Optional[str] = None

class TriageDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue_type: IssueType
    urgency: Urgency
    needs_human: bool
    rationale: Optional[str] = None

class RunConfig(BaseModel):
    model_name: str
    temperature: float
    max_completion_tokens: int
    prompt_version: str

class ServiceResponse(BaseModel):
    issue_id: str
    decision: Optional[TriageDecision] = None
    raw_llm_response: Optional[str] = None
    usage: Optional[dict]
    latency_ms: float
    finish_reason: Optional[str] = None
    run_config: RunConfig
    error_status: ErrorStatus
    error_msg: Optional[str] = None

