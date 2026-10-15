<script setup lang="ts">
import type { IssueGroup, RevisionOperation } from '@/shared/types';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { Check, X, MessageSquare, HelpCircle, Navigation } from 'lucide-vue-next';

const props = defineProps<{
  issue: IssueGroup;
  operations: RevisionOperation[];
  isActive?: boolean;
}>();

const emit = defineEmits<{
  (e: 'locate', anchor: string): void;
  (e: 'accept-issue', issueId: string, opIds: string[]): void;
  (e: 'reject-issue', issueId: string, opIds: string[]): void;
  (e: 'open-comment', issueId: string): void;
  (e: 'open-followup', issueId: string): void;
}>();

const getRelatedOpIds = (): string[] => {
  return props.operations
    .filter((op) => op.issue_group_id === props.issue.id)
    .map((op) => op.id);
};
</script>

<template>
  <div
    class="issue-card-panel"
    :class="[
      `severity-${issue.severity}`,
      `status-${issue.status}`,
      { 'is-active': isActive }
    ]"
  >
    <!-- Top Bar -->
    <div class="card-header" @click="emit('locate', issue.clause_title)">
      <div class="header-left">
        <span class="clause-pill">{{ issue.clause_title }}</span>
        <BaseBadge :variant="issue.severity" size="sm">
          {{ issue.severity === 'high' ? '高风险' : issue.severity === 'medium' ? '中风险' : '低风险' }}
        </BaseBadge>
      </div>

      <div class="header-right">
        <BaseBadge :variant="issue.status === 'accepted' ? 'success' : issue.status === 'rejected' ? 'neutral' : 'warning'" size="sm">
          {{ issue.status === 'accepted' ? '已采纳' : issue.status === 'rejected' ? '已拒绝' : issue.status === 'partially_accepted' ? '部分采纳' : '待复核' }}
        </BaseBadge>
      </div>
    </div>

    <!-- Risk Summary -->
    <div class="card-title-row">
      <span class="main-risk-point">{{ issue.risk_points[0] || '条款合规性风险' }}</span>
    </div>

    <!-- Evidence Quote -->
    <div class="evidence-quote-box">
      <span class="quote-tag">原文: </span>
      <span class="quote-text">{{ issue.evidence }}</span>
    </div>

    <!-- Public Analysis -->
    <div class="analysis-box">
      <span class="analysis-tag">法务分析: </span>
      <span>{{ issue.public_analysis }}</span>
    </div>

    <!-- Proposal -->
    <div class="proposal-box">
      <span class="proposal-tag">修改方向: </span>
      <span>{{ issue.proposal }}</span>
    </div>

    <!-- Action Bar -->
    <div class="card-footer-actions">
      <button class="footer-btn locate-btn" @click="emit('locate', issue.clause_title)" title="在正文中定位">
        <Navigation :size="13" /> 定位
      </button>

      <div class="decision-group">
        <button
          class="decision-btn accept-btn"
          :class="{ active: issue.status === 'accepted' }"
          @click="emit('accept-issue', issue.id, getRelatedOpIds())"
        >
          <Check :size="13" /> 采纳
        </button>
        <button
          class="decision-btn reject-btn"
          :class="{ active: issue.status === 'rejected' }"
          @click="emit('reject-issue', issue.id, getRelatedOpIds())"
        >
          <X :size="13" /> 拒绝
        </button>
      </div>

      <div class="aux-btns">
        <button class="icon-aux-btn" @click="emit('open-comment', issue.id)" title="添加备注">
          <MessageSquare :size="14" />
          <span v-if="issue.comments.length > 0" class="count-badge">{{ issue.comments.length }}</span>
        </button>
        <button class="icon-aux-btn" @click="emit('open-followup', issue.id)" title="条款合规咨询">
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
  padding-top: 8px;
  border-top: 1px solid #f1f5f9;
}

.locate-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
  font-size: 11.5px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.locate-btn:hover {
  color: #2563eb;
  border-color: #2563eb;
}

.decision-group {
  display: flex;
  gap: 6px;
}
.decision-btn {
  border: none;
  font-size: 11.5px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 3px;
  transition: all 0.15s;
}
.accept-btn {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}
.accept-btn:hover, .accept-btn.active {
  background: #15803d;
  color: #fff;
  border-color: #15803d;
}

.reject-btn {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.reject-btn:hover, .reject-btn.active {
  background: #b91c1c;
  color: #fff;
  border-color: #b91c1c;
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
