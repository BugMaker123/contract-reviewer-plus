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

    @property
    def chinese_name(self) -> str:
        names = {
            PipelineStage.PREPARE_SNAPSHOT: "准备快照",
            PipelineStage.BUILD_CONTEXT: "解析上下文",
            PipelineStage.ANALYZE_CLAUSES: "条款研判",
            PipelineStage.VALIDATE_FINDINGS: "审查校验",
            PipelineStage.CONSOLIDATE_ISSUES: "聚合风险",
            PipelineStage.COMPOSE_REVISIONS: "生成修订方案",
            PipelineStage.PUBLISH_RESULT: "发布结果",
        }
        return names.get(self, self.value)

