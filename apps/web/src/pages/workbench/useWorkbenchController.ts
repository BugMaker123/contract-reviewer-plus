import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/shared/http/client';
import { SSEClient } from '@/shared/events/sseClient';
import type {
  Contract,
  DocumentVersion,
  DocumentBlock,
  IssueGroup,
  RevisionOperation
} from '@/shared/types';

export function useWorkbenchController(contractId: string) {
  const contract = ref<Contract | null>(null);
  const headVersion = ref<DocumentVersion | null>(null);
  const versions = ref<DocumentVersion[]>([]);
  const blocks = ref<DocumentBlock[]>([]);
  const issues = ref<IssueGroup[]>([]);
  const operations = ref<RevisionOperation[]>([]);
  const activeAnchor = ref<string>('');

  const isLoading = ref(true);
  const isSaving = ref(false);
  const isReviewing = ref(false);
  const isCancelling = ref(false);

  // Review Dialog State
  const showReviewDialog = ref(false);
  const reviewStage = ref('prepare_snapshot');
  const reviewComplete = ref(false);
  const reviewFailed = ref(false);
  const reviewError = ref('');
  const provisionalFindings = ref<any[]>([]);
  const executionLogs = ref<any[]>([]);

  // Modals
  const showExportModal = ref(false);
  const showHistoryModal = ref(false);
  const showSettingsModal = ref(false);
  const showFollowupModal = ref(false);
  const followupMode = ref<'comment' | 'followup'>('comment');
  const activeIssue = ref<IssueGroup | null>(null);

  let sseClient: SSEClient | null = null;

  const loadContractData = async () => {
    isLoading.value = true;
    try {
      const res: any = await api.get(`/contracts/${contractId}`);
      contract.value = res.contract;
      headVersion.value = res.head_version;

      if (headVersion.value) {
        const structRes: any = await api.get(`/documents/${headVersion.value.id}/structure`);
        blocks.value = structRes.blocks;
      }

      if (contract.value?.latest_review_run_id) {
        await loadReviewResults(contract.value.latest_review_run_id);
      }
      await loadVersions();
    } catch (err) {
      console.error('Failed to load contract', err);
    } finally {
      isLoading.value = false;
    }
  };

  const loadVersions = async () => {
    const res: any = await api.get(`/contracts/${contractId}/versions`);
    versions.value = res.versions;
  };

  const loadReviewResults = async (runId: string) => {
    try {
      const res: any = await api.get(`/review-runs/${runId}/issue-groups`);
      issues.value = res.issue_groups;
      if (res.plan) {
        operations.value = res.plan.operations;
      }
    } catch (err) {
      console.error('Failed to load review results', err);
    }
  };

  const startReview = async (focusAreas?: string[]) => {
    if (!contract.value || !headVersion.value) return;
    isReviewing.value = true;
    reviewComplete.value = false;
    reviewFailed.value = false;
    reviewError.value = '';
    provisionalFindings.value = [];
    executionLogs.value = [];
    showReviewDialog.value = true;

    try {
      const res: any = await api.post('/review-runs', {
        contract_id: contractId,
        input_version_id: headVersion.value.id,
        stance: contract.value.stance,
        focus_areas: focusAreas
      });

      const runId = res.run_id;
      sseClient?.close();
      sseClient = new SSEClient(runId, {
        onEvent: (type, payload, seq) => {
          executionLogs.value.unshift({
            seq,
            time: new Date().toISOString(),
            type,
            message: JSON.stringify(payload)
          });

          if (type === 'stage_started') {
            reviewStage.value = payload.stage;
          } else if (type === 'analysis_provisional') {
            provisionalFindings.value.unshift(payload);
          } else if (type === 'succeeded') {
            reviewComplete.value = true;
            isReviewing.value = false;
          } else if (type === 'failed') {
            reviewFailed.value = true;
            reviewError.value = payload.error;
            isReviewing.value = false;
          }
        },
        onError: () => {
          executionLogs.value.unshift({
            seq: executionLogs.value.length + 1,
            time: new Date().toISOString(),
            type: 'error',
            message: 'SSE 网络连接中断，系统将尝试自动保持后台任务...'
          });
        }
      });
      sseClient.connect();
    } catch (err: any) {
      reviewFailed.value = true;
      reviewError.value = err.message;
      isReviewing.value = false;
    }
  };

  const cancelReview = async () => {
    if (!contract.value?.latest_review_run_id) return;
    isCancelling.value = true;
    try {
      await api.post(`/review-runs/${contract.value.latest_review_run_id}/cancel`);
    } finally {
      isCancelling.value = false;
    }
  };

  const applyDecision = async (action: 'accept' | 'reject' | 'reset', opIds: string[]) => {
    if (!contract.value || !headVersion.value) return;
    try {
      await api.post('/decision-commands', {
        contract_id: contractId,
        expected_version_id: headVersion.value.id,
        operation_ids: opIds,
        action
      });
      await loadContractData();
    } catch (err: any) {
      alert(`复核操作冲突或失败: ${err.message}`);
    }
  };

  const locateAnchor = (anchor: string) => {
    activeAnchor.value = anchor;
    const el = document.getElementById(`block-${anchor}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  onMounted(loadContractData);
  onUnmounted(() => {
    sseClient?.close();
  });

  return {
    contract,
    headVersion,
    versions,
    blocks,
    issues,
    operations,
    activeAnchor,
    isLoading,
    isSaving,
    isReviewing,
    isCancelling,
    showReviewDialog,
    reviewStage,
    reviewComplete,
    reviewFailed,
    reviewError,
    provisionalFindings,
    executionLogs,
    showExportModal,
    showHistoryModal,
    showSettingsModal,
    showFollowupModal,
    followupMode,
    activeIssue,
    loadContractData,
    startReview,
    cancelReview,
    applyDecision,
    locateAnchor
  };
}
