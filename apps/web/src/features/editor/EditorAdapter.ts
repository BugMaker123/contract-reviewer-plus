export interface RevisionAnchor {
  clauseId: string;
  paragraphIndex?: number;
}

export interface LocateResult {
  found: boolean;
  elementId?: string;
}

export interface EditorCapabilities {
  canTrackChanges: boolean;
  canComment: boolean;
  canAcceptReject: boolean;
  canDirectEdit: boolean;
}

export interface EditorAdapter {
  mount(container: HTMLElement, sessionKey: string): Promise<void>;
  flush(): Promise<{ saved: boolean; versionId?: string }>;
  locate(anchor: RevisionAnchor): Promise<LocateResult>;
  getCapabilities(): EditorCapabilities;
  dispose(): Promise<void>;
}
