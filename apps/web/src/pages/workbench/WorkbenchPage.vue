<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import { useWorkbenchController } from './useWorkbenchController';
import WorkbenchToolbar from './WorkbenchToolbar.vue';
import ContractOverviewPanel from '@/features/contracts/components/ContractOverviewPanel.vue';
import WebNativeRevisionViewer from '@/features/editor/WebNativeRevisionViewer.vue';
import IssueListSidebar from '@/features/issues/components/IssueListSidebar.vue';
import ReviewProgressDialog from '@/features/review/components/ReviewProgressDialog.vue';
import IssueFollowupModal from '@/features/issues/components/IssueFollowupModal.vue';
import ExportModal from '@/features/exports/components/ExportModal.vue';
import VersionHistoryModal from '@/features/versions/components/VersionHistoryModal.vue';
import ReviewSettingsDrawer from '@/features/settings/components/ReviewSettingsDrawer.vue';
import api from '@/shared/http/client';
import { PanelLeftClose, PanelRightClose, PanelLeftOpen, PanelRightOpen } from 'lucide-vue-next';

const route = useRoute();
const contractId = route.params.id as string;
const leftOpen = ref(true);
const rightOpen = ref(true);

const {
  contract, headVersion, versions, blocks, issues, operations, activeAnchor,
  isSaving, isReviewing, isCancelling,
  showReviewDialog, reviewStage, reviewComplete, reviewFailed, reviewError,
  provisionalFindings, executionLogs,
  showExportModal, showHistoryModal, showSettingsModal, showFollowupModal,
  followupMode, activeIssue,
  loadContractData, startReview, cancelReview, applyDecision, locateAnchor
} = useWorkbenchController(contractId);

const handleExport = async (kind: string) => {
  const res: any = await api.post('/exports', { contract_id: contractId, kind });
  window.open(`/api/exports/${res.export_job.id}/download`, '_blank');
  showExportModal.value = false;
};

const handleSaveDoc = async () => {
  await api.post('/editor-sessions/ses_active/save-requests', {});
  await loadContractData();
};
</script>

<template>
  <div v-if="contract" class="workbench-viewport">
    <WorkbenchToolbar
      :contract="contract"
      :head-version="headVersion || undefined"
      :is-saving="isSaving"
      :is-reviewing="isReviewing"
      @start-review="startReview()"
      @save="handleSaveDoc"
      @open-export="showExportModal = true"
      @open-history="showHistoryModal = true"
      @open-settings="showSettingsModal = true"
      @change-stance="contract.stance = $event"
      @complete-verify="api.post(`/contracts/${contractId}/verification`).then(loadContractData)"
    />

    <main class="workbench-columns-container">
      <!-- Left Overview Column -->
      <aside class="workbench-side-col left-col" :class="{ 'is-collapsed': !leftOpen }">
        <button class="toggle-col-handle left-handle" @click="leftOpen = !leftOpen">
          <component :is="leftOpen ? PanelLeftClose : PanelLeftOpen" :size="15" />
        </button>
        <ContractOverviewPanel v-show="leftOpen" :contract="contract" :issues="issues" :head-version="headVersion || undefined" />
      </aside>

      <!-- Center Document Canvas -->
      <section class="workbench-center-col">
        <WebNativeRevisionViewer
          :blocks="blocks"
          :operations="operations"
          :contract-title="contract.title"
          :active-anchor="activeAnchor"
          @accept-op="applyDecision('accept', [$event])"
          @reject-op="applyDecision('reject', [$event])"
        />
      </section>

      <!-- Right Issue Review Column -->
      <aside class="workbench-side-col right-col" :class="{ 'is-collapsed': !rightOpen }">
        <button class="toggle-col-handle right-handle" @click="rightOpen = !rightOpen">
          <component :is="rightOpen ? PanelRightClose : PanelRightOpen" :size="15" />
        </button>
        <IssueListSidebar
          v-show="rightOpen"
          :issues="issues"
          :operations="operations"
          :active-anchor="activeAnchor"
          @locate="locateAnchor"
          @accept-issue="(_, ops) => applyDecision('accept', ops)"
          @reject-issue="(_, ops) => applyDecision('reject', ops)"
          @batch-accept="applyDecision('accept', operations.filter(o => o.status === 'pending').map(o => o.id))"
          @open-comment="(id) => { activeIssue = issues.find(i => i.id === id) || null; followupMode = 'comment'; showFollowupModal = true; }"
          @open-followup="(id) => { activeIssue = issues.find(i => i.id === id) || null; followupMode = 'followup'; showFollowupModal = true; }"
        />
      </aside>
    </main>

    <!-- Modals -->
    <ReviewProgressDialog
      v-model="showReviewDialog"
      :current-stage="reviewStage"
      :is-cancelling="isCancelling"
      :is-complete="reviewComplete"
      :is-failed="reviewFailed"
      :error-message="reviewError"
      :provisional-findings="provisionalFindings"
      :execution-logs="executionLogs"
      @cancel="cancelReview"
      @finish="showReviewDialog = false; loadContractData();"
    />

    <ExportModal v-model="showExportModal" :contract-title="contract.title" @export="handleExport" />
    <VersionHistoryModal v-model="showHistoryModal" :versions="versions" :current-version-id="headVersion?.id" @select-version="loadContractData" />
    <ReviewSettingsDrawer v-model="showSettingsModal" :current-stance="contract.stance" @save-settings="(st, fa) => { contract!.stance = st; startReview(fa); }" />
    <IssueFollowupModal
      v-model="showFollowupModal"
      :issue="activeIssue"
      :mode="followupMode"
      @submit-comment="(txt) => api.post(`/issue-groups/${activeIssue?.id}/comments`, { content: txt }).then(loadContractData)"
      @submit-followup="(q) => api.post(`/issue-groups/${activeIssue?.id}/followups`, { question: q }).then(loadContractData)"
    />
  </div>
</template>

<style scoped>
.workbench-viewport { height: 100vh; display: flex; flex-direction: column; background: #f1f5f9; }
.workbench-columns-container { flex: 1; display: flex; overflow: hidden; position: relative; }
.workbench-side-col { width: 340px; background: #ffffff; border-color: var(--border-subtle); display: flex; flex-direction: column; position: relative; transition: width 0.25s ease; flex-shrink: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.left-col { border-right: 1px solid var(--border-subtle); }
.right-col { width: 380px; border-left: 1px solid var(--border-subtle); }
.workbench-side-col.is-collapsed { width: 38px; }
.workbench-center-col { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-width: 0; }
.toggle-col-handle { position: absolute; top: 12px; z-index: 20; width: 26px; height: 26px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: var(--radius-sm); color: #64748b; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.toggle-col-handle:hover { color: #fff; background: var(--brand-primary); border-color: var(--brand-primary); }
.left-handle { right: 6px; }
.right-handle { left: 6px; }
</style>
