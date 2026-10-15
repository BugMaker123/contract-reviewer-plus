from enum import Enum

class ReviewStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"

class PipelineStage(str, Enum):
    PREPARE_SNAPSHOT = "prepare_snapshot"
    BUILD_CONTEXT = "build_context"
    ANALYZE_CLAUSES = "analyze_clauses"
    VALIDATE_FINDINGS = "validate_findings"
    CONSOLIDATE_ISSUES = "consolidate_issues"
    COMPOSE_REVISIONS = "compose_revisions"
    PUBLISH_RESULT = "publish_result"
