from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from contract_app.shared.clock import now_utc
from contract_app.shared.ids import issue_group_id

@dataclass
class IssueComment:
    id: str
    author: str
    content: str
    created_at: datetime = field(default_factory=now_utc)

@dataclass
class IssueFollowup:
    id: str
    question: str
    answer: str
    created_at: datetime = field(default_factory=now_utc)

@dataclass
class IssueGroup:
    id: str = field(default_factory=issue_group_id)
    run_id: str = ""
    clause_title: str = ""
    severity: str = "medium"  # high, medium, low
    risk_points: List[str] = field(default_factory=list)
    evidence: str = ""
    public_analysis: str = ""
    proposal: str = ""
    anchors: List[str] = field(default_factory=list)
    status: str = "unreviewed"  # unreviewed, accepted, rejected, partially_accepted
    comments: List[Dict[str, Any]] = field(default_factory=list)
    followups: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=now_utc)
    updated_at: datetime = field(default_factory=now_utc)

    def add_comment(self, author: str, content: str):
        self.comments.append({
            "id": f"cmt_{len(self.comments)+1}",
            "author": author,
            "content": content,
            "created_at": now_utc().isoformat()
        })
        self.updated_at = now_utc()

    def add_followup(self, question: str, answer: str):
        self.followups.append({
            "id": f"flw_{len(self.followups)+1}",
            "question": question,
            "answer": answer,
            "created_at": now_utc().isoformat()
        })
        self.updated_at = now_utc()
