export interface SSEOptions {
  onEvent: (type: string, payload: any, seq: number) => void;
  onError?: (err: any) => void;
  onOpen?: () => void;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private lastSeq: number = 0;
  private isManualClosed = false;

  constructor(private runId: string, private options: SSEOptions) {}

  public connect() {
    this.isManualClosed = false;
    const url = `/api/review-runs/${this.runId}/events`;
    this.eventSource = new EventSource(url);

    this.eventSource.onopen = () => {
      this.options.onOpen?.();
    };

    // Register event listeners
    const eventTypes = [
      'stage_started',
      'stage_completed',
      'analysis_provisional',
      'retry_scheduled',
      'succeeded',
      'failed',
      'cancelled'
    ];

    eventTypes.forEach((type) => {
      this.eventSource?.addEventListener(type, (e: MessageEvent) => {
        try {
          const seq = parseInt(e.lastEventId || '0', 10);
          if (seq > this.lastSeq) {
            this.lastSeq = seq;
          }
          const payload = JSON.parse(e.data);
          this.options.onEvent(type, payload, seq);
          if (type === 'succeeded' || type === 'failed' || type === 'cancelled') {
            this.close();
          }
        } catch (err) {
          console.error('[SSE] parse error', err);
        }
      });
    });

    this.eventSource.onerror = (err) => {
      if (!this.isManualClosed) {
        this.options.onError?.(err);
      }
    };
  }

  public close() {
    this.isManualClosed = true;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
