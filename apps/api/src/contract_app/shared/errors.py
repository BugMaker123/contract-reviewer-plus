from typing import Any, Dict, Optional

class DomainError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.retryable = retryable

class VersionConflictError(DomainError):
    def __init__(self, current_version_id: str, message: str = "文档已产生新版本，请核对后重试"):
        super().__init__(
            code="DOCUMENT_VERSION_CONFLICT",
            message=message,
            details={"current_version_id": current_version_id},
            retryable=False
        )

class AnchorAmbiguousError(DomainError):
    def __init__(self, anchor: str, message: str = "条款定位歧义，无法唯一对应原文"):
        super().__init__(
            code="ANCHOR_AMBIGUOUS",
            message=message,
            details={"anchor": anchor},
            retryable=False
        )

class SaveUnconfirmedError(DomainError):
    def __init__(self, session_id: str, message: str = "文档保存未完成确认"):
        super().__init__(
            code="SAVE_UNCONFIRMED",
            message=message,
            details={"session_id": session_id},
            retryable=True
        )

class ReviewCancelledError(DomainError):
    def __init__(self, run_id: str, message: str = "审查任务已被用户取消"):
        super().__init__(
            code="REVIEW_CANCELLED",
            message=message,
            details={"run_id": run_id},
            retryable=False
        )

class ReviewTimeoutError(DomainError):
    def __init__(self, run_id: str, message: str = "审查执行超出时限"):
        super().__init__(
            code="REVIEW_DEADLINE_EXCEEDED",
            message=message,
            details={"run_id": run_id},
            retryable=False
        )
