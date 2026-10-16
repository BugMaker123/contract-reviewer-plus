<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
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
// 页面做减法：默认收起左侧杂糅技术概览，正文与右侧审查建议占满视野
const leftOpen = ref(false);
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

// 待复核数量计算
const unreviewedCount = computed(() => {
  return issues.value.filter(i => i.status === 'unreviewed' || i.status === 'partially_accepted').length;
});

// 当前风险点索引
const currentIssueIndex = computed(() => {
  if (!activeAnchor.value || issues.value.length === 0) return 0;
  const idx = issues.value.findIndex(i => i.clause_title === activeAnchor.value || activeAnchor.value.includes(i.clause_title));
  return idx >= 0 ? idx : 0;
});

// 上一处 / 下一处风险定位
const prevIssue = () => {
  if (issues.value.length === 0) return;
  let nextIdx = currentIssueIndex.value - 1;
  if (nextIdx < 0) nextIdx = issues.value.length - 1;
  locateAnchor(issues.value[nextIdx].clause_title);
};

const nextIssue = () => {
  if (issues.value.length === 0) return;
  let nextIdx = currentIssueIndex.value + 1;
  if (nextIdx >= issues.value.length) nextIdx = 0;
  locateAnchor(issues.value[nextIdx].clause_title);
};

// 键盘快捷键支持：Alt+↑ / Alt+↓ 切换风险点
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.altKey && e.key === 'ArrowUp') {
    e.preventDefault();
    prevIssue();
  } else if (e.altKey && e.key === 'ArrowDown') {
    e.preventDefault();
    nextIssue();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

// 重新生成修改建议
const handleRegenerate = async (issueId: string) => {
  try {
    await api.post(`/issue-groups/${issueId}/regenerate`);
    await loadContractData();
  } catch (err: any) {
    console.error('Failed to regenerate proposal', err);
  }
};

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
      :unreviewed-count="unreviewedCount"
      :current-issue-index="currentIssueIndex"
      :total-issues="issues.length"
      @prev-issue="prevIssue"
      @next-issue="nextIssue"
      @start-review="startReview()"
      @save="handleSaveDoc"
      @open-export="showExportModal = true"
      @open-history="showHistoryModal = true"
      @open-settings="showSettingsModal = true"
      @change-stance="contract.stance = $event"
      @complete-verify="api.post(`/contracts/${contractId}/verification`).then(loadContractData)"
    />

    <main class="workbench-columns-container">
      <!-- Left Overview Column (做减法，可按需展开) -->
      <aside class="workbench-side-col left-col" :class="{ 'is-collapsed': !leftOpen }">
        <button class="toggle-col-handle left-handle" @click="leftOpen = !leftOpen" :title="leftOpen ? '折叠左侧面板' : '展开合同基础概览'">
          <component :is="leftOpen ? PanelLeftClose : PanelLeftOpen" :size="15" />
        </button>
        <ContractOverviewPanel v-show="leftOpen" :contract="contract" :issues="issues" :head-version="headVersion || undefined" />
      </aside>

      <!-- Center Document Canvas (70% 宽，白底纯净 Word A4 纸张排版) -->
      <section class="workbench-center-col">
        <WebNativeRevisionViewer
          :blocks="blocks"
          :operations="operations"
          :contract-title="contract.title"
          :active-anchor="activeAnchor"
          @locate="locateAnchor"
          @scroll-focus="activeAnchor = $event"
          @accept-op="applyDecision('accept', [$event])"
          @reject-op="applyDecision('reject', [$event])"
        />
      </section>

      <!-- Right Issue Review Column (统一智能审查面板，采纳修改左侧增加重新生成) -->
      <aside class="workbench-side-col right-col" :class="{ 'is-collapsed': !rightOpen }">
        <button class="toggle-col-handle right-handle" @click="rightOpen = !rightOpen" :title="rightOpen ? '折叠审查面板' : '展开审查面板'">
          <component :is="rightOpen ? PanelRightClose : PanelRightOpen" :size="15" />
        </button>
        <IssueListSidebar
          v-show="rightOpen"
          :issues="issues"
          :operations="operations"
          :active-anchor="activeAnchor"
          @locate="locateAnchor"
          @regenerate="handleRegenerate"
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
