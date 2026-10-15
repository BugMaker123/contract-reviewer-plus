export interface Contract {
  id: string;
  title: string;
  head_version_id?: string;
  latest_review_run_id?: string;
  revision: number;
  stance: string;
  review_status: 'unreviewed' | 'reviewing' | 'reviewed' | 'verified';
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  contract_id: string;
  parent_id?: string;
  kind: 'original' | 'user_saved' | 'review_baseline' | 'ai_proposal' | 'verified';
  object_key: string;
  content_hash: string;
  created_by: string;
  review_run_id?: string;
  summary: string;
  revision_count: number;
  created_at: string;
}

export interface DocumentBlock {
  block_id: string;
  clause_id: string;
  text: string;
  length: number;
}

export interface EditorSession {
  id: string;
  contract_id: string;
  base_version_id: string;
  provider: string;
  document_key: string;
  generation: number;
  status: string;
}

export interface ReviewRun {
  id: string;
  contract_id: string;
  input_version_id: string;
  stance: string;
  focus_areas: string[];
  status: 'queued' | 'running' | 'succeeded' | 'failed' | 'cancel_requested' | 'cancelled' | 'timed_out';
  current_stage: string;
  deadline: string;
  attempt: number;
  result_version_id?: string;
  plan_id?: string;
  error_code?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewEvent {
  run_id: string;
  seq: number;
  type: string;
  time: string;
  attempt: number;
  payload: any;
}

export interface IssueComment {
  id: string;
  author: string;
  content: string;
  created_at: string;
}

export interface IssueFollowup {
  id: string;
  question: string;
  answer: string;
  created_at: string;
}

export interface IssueGroup {
  id: string;
  run_id: string;
  clause_title: string;
  severity: 'high' | 'medium' | 'low';
  risk_points: string[];
  evidence: string;
  public_analysis: string;
  proposal: string;
  anchors: string[];
  status: 'unreviewed' | 'accepted' | 'rejected' | 'partially_accepted';
  comments: IssueComment[];
  followups: IssueFollowup[];
  created_at: string;
  updated_at: string;
}

export interface RevisionOperation {
  id: string;
  plan_id: string;
  issue_group_id: string;
  kind: 'insert' | 'delete' | 'replace' | 'comment';
  anchor: string;
  expected_text: string;
  replacement_text: string;
  author: string;
  public_reason: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface RevisionPlan {
  id: string;
  review_run_id: string;
  base_version_id: string;
  operations: RevisionOperation[];
}

export interface DecisionCommand {
  id: string;
  contract_id: string;
  expected_version_id: string;
  operation_ids: string[];
  action: 'accept' | 'reject' | 'reset';
  status: 'requested' | 'executing' | 'awaiting_save' | 'confirmed' | 'failed';
  confirmed_version_id?: string;
  error_message?: string;
}

export interface ExportJob {
  id: string;
  contract_id: string;
  source_version_id: string;
  kind: 'clean_draft' | 'track_changes' | 'review_report';
  status: 'pending' | 'processing' | 'succeeded' | 'failed';
  artifact_key?: string;
  file_name?: string;
}
