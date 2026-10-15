<script setup lang="ts">
import { computed } from 'vue';
import type { Contract, IssueGroup, DocumentVersion } from '@/shared/types';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { CheckCircle2, Clock, GitBranch } from 'lucide-vue-next';

const props = defineProps<{
  contract: Contract;
  issues: IssueGroup[];
  headVersion?: DocumentVersion;
}>();

const highCount = computed(() => props.issues.filter((i) => i.severity === 'high').length);
const mediumCount = computed(() => props.issues.filter((i) => i.severity === 'medium').length);
const lowCount = computed(() => props.issues.filter((i) => i.severity === 'low').length);

const acceptedCount = computed(() => props.issues.filter((i) => i.status === 'accepted').length);
const rejectedCount = computed(() => props.issues.filter((i) => i.status === 'rejected').length);
const pendingCount = computed(() => props.issues.filter((i) => i.status === 'unreviewed' || i.status === 'partially_accepted').length);

const progressPercent = computed(() => {
  if (props.issues.length === 0) return 0;
  const resolved = acceptedCount.value + rejectedCount.value;
  return Math.round((resolved / props.issues.length) * 100);
});
</script>

<template>
  <div class="overview-panel-content">
    <!-- Contract Title & Stance -->
    <div class="panel-section contract-info-card">
      <div class="contract-title-text">{{ contract.title }}</div>
      <div class="contract-tags">
        <BaseBadge variant="info" size="sm">立场: {{ contract.stance }}</BaseBadge>
        <BaseBadge :variant="contract.review_status === 'verified' ? 'success' : 'neutral'" size="sm">
          {{ contract.review_status === 'verified' ? '已完成复核' : contract.review_status === 'reviewed' ? '待复核确认' : '未审查' }}
        </BaseBadge>
      </div>
    </div>

    <!-- Review Progress Metric -->
    <div class="panel-section progress-box">
      <div class="box-header">
        <span class="box-title">人工复核处理进度</span>
        <span class="box-percent">{{ progressPercent }}%</span>
      </div>
      <div class="progress-bar-bg">
        <div class="progress-bar-fill" :style="{ width: `${progressPercent}%` }"></div>
      </div>
      <div class="progress-stats">
        <span class="stat-tag success"><CheckCircle2 :size="12" /> 已采纳: {{ acceptedCount }}</span>
        <span class="stat-tag danger">已拒绝: {{ rejectedCount }}</span>
        <span class="stat-tag warning"><Clock :size="12" /> 待复核: {{ pendingCount }}</span>
      </div>
    </div>

    <!-- Risk Breakdown -->
    <div class="panel-section risk-breakdown-box">
      <div class="box-header">
        <span class="box-title">审查风险分布 (共 {{ issues.length }} 处问题组)</span>
      </div>
      <div class="risk-cards-grid">
        <div class="risk-stat-card high">
          <span class="stat-num">{{ highCount }}</span>
          <span class="stat-label">高风险</span>
        </div>
        <div class="risk-stat-card medium">
          <span class="stat-num">{{ mediumCount }}</span>
          <span class="stat-label">中风险</span>
        </div>
        <div class="risk-stat-card low">
          <span class="stat-num">{{ lowCount }}</span>
          <span class="stat-label">低风险</span>
        </div>
      </div>
    </div>

    <!-- Active Version & Immutability Info -->
    <div class="panel-section version-info-box">
      <div class="box-header">
        <span class="box-title"><GitBranch :size="13" /> 当前工作版本快照</span>
      </div>
      <div v-if="headVersion" class="version-details">
        <div class="detail-row">
          <span class="row-label">版本 ID:</span>
          <span class="row-val font-mono">{{ headVersion.id }}</span>
        </div>
        <div class="detail-row">
          <span class="row-label">类型:</span>
          <span class="row-val">{{ headVersion.kind }}</span>
        </div>
        <div class="detail-row">
          <span class="row-label">内容哈希:</span>
          <span class="row-val font-mono">{{ headVersion.content_hash.substring(0, 10) }}</span>
        </div>
        <div class="detail-row">
          <span class="row-label">状态:</span>
          <span class="row-val text-emerald">不可变安全存储</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overview-panel-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  background: #ffffff;
}

.panel-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: 14px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.contract-title-text {
  font-family: var(--font-heading);
  font-size: 14.5px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.4;
  margin-bottom: 8px;
}
.contract-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.box-title {
  font-size: 12.5px;
  font-weight: 600;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 5px;
}
.box-percent {
  font-weight: 700;
  color: #2563eb;
  font-size: 14px;
}

.progress-bar-bg {
  height: 6px;
  background: #e2e8f0;
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 10px;
}
.progress-bar-fill {
  height: 100%;
  background: #2563eb;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
}
.stat-tag {
  display: flex;
  align-items: center;
  gap: 3px;
}
.stat-tag.success { color: #16a34a; font-weight: 500; }
.stat-tag.danger { color: #dc2626; font-weight: 500; }
.stat-tag.warning { color: #d97706; font-weight: 500; }

.risk-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.risk-stat-card {
  padding: 8px;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid transparent;
}
.risk-stat-card.high {
  background: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}
.risk-stat-card.medium {
  background: #fffbeb;
  border-color: #fde68a;
  color: #d97706;
}
.risk-stat-card.low {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #2563eb;
}
.stat-num {
  font-size: 18px;
  font-weight: 700;
}
.stat-label {
  font-size: 11px;
}

.version-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
}
.detail-row {
  display: flex;
  justify-content: space-between;
}
.row-label { color: #64748b; }
.row-val { color: #0f172a; }
.font-mono { font-family: var(--font-mono); }
.text-emerald { color: #16a34a; font-weight: 500; }
</style>
