from datetime import datetime
from contract_app.shared.clock import now_utc

class RetryPolicy:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def should_retry(
        self,
        attempt: int,
        deadline: datetime,
        is_retryable_error: bool,
        is_cancelled: bool
    ) -> bool:
        if is_cancelled:
            return False
        if not is_retryable_error:
            return False
        if attempt > self.max_retries:
            return False
        if now_utc() >= deadline:
            return False
        return True
