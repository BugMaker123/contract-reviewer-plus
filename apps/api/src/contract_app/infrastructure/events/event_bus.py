import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional
from contract_app.shared.clock import now_iso, now_utc

@dataclass
class ReviewEvent:
    run_id: str
    seq: int
    type: str
    time: str = field(default_factory=now_iso)
    attempt: int = 1
    payload: dict = field(default_factory=dict)

    def to_sse_chunk(self) -> str:
        data_str = json.dumps(self.payload, ensure_ascii=False)
        return f"id: {self.seq}\nevent: {self.type}\ndata: {data_str}\n\n"

class EventBus:
    def __init__(self):
        self._history: Dict[str, List[ReviewEvent]] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, run_id: str, event_type: str, payload: dict, attempt: int = 1):
        async with self._lock:
            if run_id not in self._history:
                self._history[run_id] = []
            seq = len(self._history[run_id]) + 1
            event = ReviewEvent(
                run_id=run_id,
                seq=seq,
                type=event_type,
                time=now_iso(),
                attempt=attempt,
                payload=payload
            )
            self._history[run_id].append(event)
            queues = self._subscribers.get(run_id, [])
            for q in queues:
                await q.put(event)

    async def subscribe(self, run_id: str, last_event_id: Optional[int] = None) -> AsyncGenerator[str, None]:
        q: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            if run_id not in self._subscribers:
                self._subscribers[run_id] = []
            self._subscribers[run_id].append(q)

            # Replay historical missed events
            history = self._history.get(run_id, [])
            start_idx = last_event_id or 0
            missed = [ev for ev in history if ev.seq > start_idx]

        for ev in missed:
            yield ev.to_sse_chunk()

        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield event.to_sse_chunk()
                    if event.type in ("succeeded", "failed", "cancelled"):
                        break
                except asyncio.TimeoutError:
                    # Heartbeat comment per design: no seq, does not pollute history
                    yield ": heartbeat\n\n"
        finally:
            async with self._lock:
                if run_id in self._subscribers and q in self._subscribers[run_id]:
                    self._subscribers[run_id].remove(q)

    def get_events(self, run_id: str) -> List[ReviewEvent]:
        return list(self._history.get(run_id, []))

event_bus = EventBus()
