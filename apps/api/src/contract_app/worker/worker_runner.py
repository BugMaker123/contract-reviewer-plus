import asyncio
import os
from contract_app.infrastructure.persistence.repositories import repo_store
from contract_app.modules.reviews.domain.review_state import ReviewStatus
from contract_app.modules.reviews.application.run_pipeline import run_pipeline_use_case
from contract_app.bootstrap.config import settings

class WorkerRunner:
    def __init__(self, worker_name: str = f"worker_{os.getpid()}"):
        self.worker_name = worker_name
        self._running = False

    async def start(self):
        self._running = True
        print(f"[*] Contract Review Worker started: {self.worker_name}")
        while self._running:
            try:
                # Scan queued runs
                for run in list(repo_store.review_runs.values()):
                    if run.status == ReviewStatus.QUEUED:
                        if run.claim_lease(self.worker_name, settings.worker_lease_seconds):
                            await repo_store.save_review_run(run)
                            print(f"[*] Worker claimed task {run.id} (epoch {run.execution_epoch})")
                            await run_pipeline_use_case.execute(run.id)
                await asyncio.sleep(1.0)
            except Exception as e:
                print(f"[!] Worker exception: {e}")
                await asyncio.sleep(2.0)

    def stop(self):
        self._running = False

if __name__ == "__main__":
    runner = WorkerRunner()
    asyncio.run(runner.start())
