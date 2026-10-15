<script setup lang="ts">
import { ref, computed } from 'vue';
import type { IssueGroup, RevisionOperation } from '@/shared/types';
import IssueCard from './IssueCard.vue';
import BaseSelect from '@/shared/ui/BaseSelect.vue';
import { Search, CheckCheck, ListFilter } from 'lucide-vue-next';

const props = defineProps<{
  issues: IssueGroup[];
  operations: RevisionOperation[];
  activeAnchor?: string;
}>();

const emit = defineEmits<{
  (e: 'locate', anchor: string): void;
  (e: 'accept-issue', issueId: string, opIds: string[]): void;
  (e: 'reject-issue', issueId: string, opIds: string[]): void;
  (e: 'batch-accept'): void;
  (e: 'open-comment', issueId: string): void;
  (e: 'open-followup', issueId: string): void;
}>();

const searchQuery = ref('');
const selectedSeverity = ref('all');
const selectedStatus = ref('all');

const severityOptions = [
  { label: '全部风险等级', value: 'all' },
  { label: '高风险', value: 'high' },
  { label: '中风险', value: 'medium' },
  { label: '低风险', value: 'low' },
];

const statusOptions = [
  { label: '全部复核状态', value: 'all' },
  { label: '待复核', value: 'unreviewed' },
  { label: '已采纳', value: 'accepted' },
  { label: '已拒绝', value: 'rejected' },
];

const filteredIssues = computed(() => {
  return props.issues.filter((i) => {
    if (selectedSeverity.value !== 'all' && i.severity !== selectedSeverity.value) return false;
    if (selectedStatus.value !== 'all') {
      if (selectedStatus.value === 'unreviewed' && i.status !== 'unreviewed' && i.status !== 'partially_accepted') return false;
      if (selectedStatus.value !== 'unreviewed' && i.status !== selectedStatus.value) return false;
    }
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const match =
        i.clause_title.toLowerCase().includes(q) ||
        i.evidence.toLowerCase().includes(q) ||
        i.public_analysis.toLowerCase().includes(q) ||
        i.proposal.toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });
});
</script>

<template>
  <div class="issue-sidebar-wrapper">
    <!-- Filter controls -->
    <div class="filter-controls-box">
      <div class="search-input-wrap">
        <Search :size="14" class="search-icon" />
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="检索条款编号、原文或风险评述..."
        />
      </div>

      <div class="filter-dropdowns">
        <BaseSelect v-model="selectedSeverity" :options="severityOptions" />
        <BaseSelect v-model="selectedStatus" :options="statusOptions" />
      </div>

      <div class="batch-bar">
        <span class="count-text">显示 {{ filteredIssues.length }} / {{ issues.length }} 条问题</span>
        <button class="batch-accept-btn" @click="emit('batch-accept')" title="一键采纳所有待决修改">
          <CheckCheck :size="13" /> 批量采纳
        </button>
      </div>
    </div>

    <!-- Cards Scroll list -->
    <div class="issues-cards-list">
      <div v-if="filteredIssues.length === 0" class="empty-state">
        <ListFilter :size="32" class="empty-icon" />
        <span>未检索到匹配的审查意见</span>
      </div>

      <IssueCard
        v-for="issue in filteredIssues"
        :key="issue.id"
        :issue="issue"
        :operations="operations"
        :is-active="activeAnchor === issue.clause_title"
        @locate="emit('locate', $event)"
        @accept-issue="(id, ops) => emit('accept-issue', id, ops)"
        @reject-issue="(id, ops) => emit('reject-issue', id, ops)"
        @open-comment="emit('open-comment', $event)"
        @open-followup="emit('open-followup', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.issue-sidebar-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #ffffff;
}

.filter-controls-box {
  padding: 12px 14px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
}
.search-input {
  width: 100%;
  padding: 6px 12px 6px 30px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-sm);
  color: #0f172a;
  font-size: 12.5px;
  outline: none;
}
.search-input:focus {
  border-color: #2563eb;
}

.filter-dropdowns {
  display: flex;
  gap: 8px;
}

.batch-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11.5px;
  padding-top: 4px;
}
.count-text { color: #64748b; }

.batch-accept-btn {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
  border-radius: var(--radius-sm);
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
.batch-accept-btn:hover {
  background: #15803d;
  color: #fff;
  border-color: #15803d;
}

.issues-cards-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f8fafc;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.empty-icon { color: var(--text-dim); }
</style>
