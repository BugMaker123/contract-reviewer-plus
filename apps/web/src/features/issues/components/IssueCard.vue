<script setup lang="ts">
import { ref } from 'vue';
import type { IssueGroup, RevisionOperation } from '@/shared/types';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { Check, X, MessageSquare, HelpCircle, Navigation, RotateCw } from 'lucide-vue-next';

const props = defineProps<{
  issue: IssueGroup;
  operations: RevisionOperation[];
  isActive?: boolean;
}>();

const emit = defineEmits<{
  (e: 'locate', anchor: string): void;
  (e: 'accept-issue', issueId: string, opIds: string[]): void;
  (e: 'reject-issue', issueId: string, opIds: string[]): void;
  (e: 'regenerate', issueId: string): void;
  (e: 'open-comment', issueId: string): void;
  (e: 'open-followup', issueId: string): void;
}>();

const isRegenerating = ref(false);

const getRelatedOpIds = (): string[] => {
  return props.operations
    .filter((op) => op.issue_group_id === props.issue.id)
    .map((op) => op.id);
};

const handleRegenerateClick = () => {
  if (isRegenerating.value) return;
  isRegenerating.value = true;
  emit('regenerate', props.issue.id);
  setTimeout(() => {
    isRegenerating.value = false;
  }, 750);
};
</script>

<template>
  <div
    :id="`card-${issue.clause_title}`"
    class="issue-card-panel"
    :class="[
      `severity-${issue.severity}`,
      `status-${issue.status}`,
      { 'is-active': isActive }
    ]"
    @click="emit('locate', issue.clause_title)"
  >
    <!-- Top Bar -->
    <div class="card-header">
      <div class="header-left">
        <BaseBadge :variant="issue.severity" size="sm">
          {{ issue.severity === 'high' ? '高风险' : issue.severity === 'medium' ? '中风险' : '低风险' }}
        </BaseBadge>
        <span class="clause-pill">{{ issue.clause_title }}</span>
      </div>

      <div class="header-right">
        <!-- 优化点 1：明确的定位正文按钮 -->
        <button class="btn-locate" @click.stop="emit('locate', issue.clause_title)" title="在正文中定位此条款">
          <Navigation :size="12" /> 定位正文
        </button>
      </div>
    </div>

    <!-- Risk Summary Title -->
    <div class="card-title-row">
      <span class="main-risk-point">{{ issue.risk_points[0] || '条款合规性风险' }}</span>
    </div>

    <!-- Public Analysis -->
    <div class="analysis-box">
      <span class="analysis-tag">法务分析: </span>
      <span>{{ issue.public_analysis }}</span>
    </div>

    <!-- 建议修订差异框 -->
    <div v-if="issue.proposal" class="card-diff-box">
      <div class="diff-label">建议修订/补充条款：</div>
      <div class="diff-content">+ {{ issue.proposal }}</div>
    </div>

    <!-- Action Bar: 采纳修改左侧增加重新生成按钮，采纳在前拒绝在后 -->
    <div class="card-footer-actions">
      <div class="decision-group">
        <!-- 重新生成按钮 -->
        <button
          class="btn-card regenerate"
          :class="{ loading: isRegenerating }"
          :disabled="isRegenerating"
          @click.stop="handleRegenerateClick"
          title="让 AI 重新撰写修订建议"
        >
          <RotateCw :size="13" :class="{ 'spin-icon': isRegenerating }" />
          <span>{{ isRegenerating ? '重新生成中...' : '重新生成' }}</span>
        </button>

        <!-- 采纳修改按钮（绿色主按钮） -->
        <button
          class="btn-card accept"
          :class="{ active: issue.status === 'accepted' }"
          @click.stop="emit('accept-issue', issue.id, getRelatedOpIds())"
        >
          <Check :size="13" /> 采纳修改
        </button>

        <!-- 拒绝按钮（灰色次按钮） -->
        <button
          class="btn-card reject"
          :class="{ active: issue.status === 'rejected' }"
          @click.stop="emit('reject-issue', issue.id, getRelatedOpIds())"
        >
          <X :size="13" /> 拒绝
        </button>
      </div>

      <div class="aux-btns">
        <button class="icon-aux-btn" @click.stop="emit('open-comment', issue.id)" title="添加备注">
          <MessageSquare :size="14" />
          <span v-if="issue.comments.length > 0" class="count-badge">{{ issue.comments.length }}</span>
        </button>
        <button class="icon-aux-btn" @click.stop="emit('open-followup', issue.id)" title="条款合规咨询">
          <HelpCircle :size="14" />
          <span v-if="issue.followups.length > 0" class="count-badge">{{ issue.followups.length }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.issue-card-panel {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.issue-card-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
}
.issue-card-panel.severity-high::before { background: #ef4444; }
.issue-card-panel.severity-medium::before { background: #f59e0b; }
.issue-card-panel.severity-low::before { background: #2563eb; }

.issue-card-panel:hover, .issue-card-panel.is-active {
  background: #f8fafc;
  border-color: #94a3b8;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.clause-pill {
  font-weight: 700;
  color: #0284c7;
  font-size: 13px;
}

.card-title-row {
  font-size: 13.5px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
}

.evidence-quote-box {
  background: #f8fafc;
  border-left: 3px solid #cbd5e1;
  padding: 6px 10px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 12px;
  color: #475569;
}
.quote-tag { color: #64748b; font-weight: 600; }

.analysis-box {
  font-size: 12.5px;
  color: #334155;
  line-height: 1.45;
}
.analysis-tag { color: #b45309; font-weight: 600; }

.proposal-box {
  font-size: 12.5px;
  color: #15803d;
  line-height: 1.45;
}
.proposal-tag { font-weight: 600; }

.card-footer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
}

.btn-locate {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 500;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-locate:hover {
  background: #dbeafe;
  border-color: #bfdbfe;
}

.card-diff-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12.5px;
  line-height: 1.5;
}
.diff-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 4px;
}
.diff-content {
  color: #1d4ed8;
  font-weight: 500;
}

.decision-group {
  display: flex;
  gap: 6px;
  align-items: center;
}

.btn-card {
  font-size: 12px;
  font-weight: 500;
  padding: 5px 12px;
  border-radius: 5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}
.btn-card.regenerate {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
}
.btn-card.regenerate:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #93c5fd;
  color: #1d4ed8;
}
.btn-card.regenerate:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.btn-card.accept {
  background: #16a34a;
  color: #ffffff;
}
.btn-card.accept:hover, .btn-card.accept.active {
  background: #15803d;
}
.btn-card.reject {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #64748b;
}
.btn-card.reject:hover, .btn-card.reject.active {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}
.spin-icon {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.aux-btns {
  display: flex;
  gap: 4px;
}
.icon-aux-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 5px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  position: relative;
}
.icon-aux-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}
.count-badge {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 9px;
  background: #2563eb;
  color: #fff;
  border-radius: 50%;
  width: 13px;
  height: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
