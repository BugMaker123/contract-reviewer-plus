<script setup lang="ts">
import { useRouter } from 'vue-router';
import BaseButton from '@/shared/ui/BaseButton.vue';
import BaseSelect from '@/shared/ui/BaseSelect.vue';
import type { Contract, DocumentVersion } from '@/shared/types';
import { Play, Save, Download, CheckCircle, SlidersHorizontal, History, ArrowLeft, ChevronUp, ChevronDown } from 'lucide-vue-next';

defineProps<{
  contract: Contract;
  headVersion?: DocumentVersion;
  isSaving?: boolean;
  isReviewing?: boolean;
  unreviewedCount?: number;
  currentIssueIndex?: number;
  totalIssues?: number;
}>();

const emit = defineEmits<{
  (e: 'change-stance', stance: string): void;
  (e: 'start-review'): void;
  (e: 'save'): void;
  (e: 'open-export'): void;
  (e: 'open-history'): void;
  (e: 'open-settings'): void;
  (e: 'complete-verify'): void;
  (e: 'prev-issue'): void;
  (e: 'next-issue'): void;
}>();

const router = useRouter();

const stanceOptions = [
  { label: '立场: 我方(受托方)', value: '我方(受托方)' },
  { label: '立场: 我方(委托方)', value: '我方(委托方)' },
  { label: '立场: 我方(采购方)', value: '我方(采购方)' },
  { label: '立场: 我方(供应商)', value: '我方(供应商)' },
  { label: '立场: 中立对等', value: '中立对等' },
];
</script>

<template>
  <header class="workbench-top-bar glass-panel">
    <!-- Left Navigation & Title & Issue Switcher -->
    <div class="bar-left">
      <button class="back-nav-btn" @click="router.push('/')" title="返回合同列表">
        <ArrowLeft :size="16" />
      </button>

      <div class="contract-badge-group">
        <h2 class="top-title">{{ contract.title }}</h2>
        <span class="version-chip" @click="emit('open-history')">
          <History :size="12" />
          <span>{{ headVersion?.id || 'v1' }}</span>
        </span>
      </div>

      <!-- 待复核状态胶囊 -->
      <div v-if="totalIssues && totalIssues > 0" class="status-pill" :class="{ all_done: (unreviewedCount ?? 0) === 0 }">
        <span class="dot"></span>
        <span>{{ (unreviewedCount ?? 0) === 0 ? '已全部复核完毕' : `${unreviewedCount} 处待复核` }}</span>
      </div>

      <!-- 优化点 1：上一处/下一处风险快速导航 -->
      <div v-if="totalIssues && totalIssues > 0" class="issue-navigator" title="在各处风险点之间快速切换 (Alt+↑ / Alt+↓)">
        <button class="btn-nav-step" @click="emit('prev-issue')" title="上一处风险 (Alt+↑)">
          <ChevronUp :size="12" /> 上一处
        </button>
        <span class="nav-step-index">{{ (currentIssueIndex ?? 0) + 1 }} / {{ totalIssues }}</span>
        <button class="btn-nav-step" @click="emit('next-issue')" title="下一处风险 (Alt+↓)">
          下一处 <ChevronDown :size="12" />
        </button>
      </div>
    </div>

    <!-- Center Quick Stance selector -->
    <div class="bar-center">
      <BaseSelect
        :model-value="contract.stance"
        :options="stanceOptions"
        @update:model-value="emit('change-stance', $event)"
      />
      <button class="settings-gear-btn" @click="emit('open-settings')" title="高级审查配置与专项参数">
        <SlidersHorizontal :size="15" />
      </button>
    </div>

    <!-- Right Operations Actions -->
    <div class="bar-right">
      <BaseButton
        variant="primary"
        size="sm"
        :loading="isReviewing"
        @click="emit('start-review')"
      >
        <Play :size="13" /> {{ contract.review_status === 'reviewed' ? '重新审查' : '开始审查' }}
      </BaseButton>

      <BaseButton
        variant="secondary"
        size="sm"
        :loading="isSaving"
        @click="emit('save')"
        title="保存当前文档编辑修改并提交检查点"
      >
        <Save :size="13" /> 保存
      </BaseButton>

      <BaseButton
        variant="secondary"
        size="sm"
        @click="emit('open-export')"
        title="导出清洁稿或带修订稿"
      >
        <Download :size="13" /> 导出
      </BaseButton>

      <BaseButton
        variant="success"
        size="sm"
        @click="emit('complete-verify')"
        title="确认最终复核完成并锁定归档"
      >
        <CheckCircle :size="13" /> 完成复核
      </BaseButton>
    </div>
  </header>
</template>

<style scoped>
.workbench-top-bar {
  height: 52px;
  background: #ffffff;
  border-bottom: 1px solid var(--border-subtle);
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
  z-index: 50;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-nav-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}
.back-nav-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
  border-color: #94a3b8;
}

.contract-badge-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
.top-title {
  font-family: var(--font-heading);
  font-size: 14.5px;
  font-weight: 600;
  color: #0f172a;
  max-width: 320px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.version-chip {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-full);
  padding: 2px 8px;
  font-size: 11px;
  font-family: var(--font-mono);
  color: #2563eb;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.version-chip:hover {
  border-color: #2563eb;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fef3c7;
  color: #b45309;
  border: 1px solid #fde68a;
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 999px;
  margin-left: 4px;
}
.status-pill.all_done {
  background: #dcfce7;
  color: #15803d;
  border-color: #86efac;
}
.status-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f59e0b;
}
.status-pill.all_done .dot {
  background: #22c55e;
}

.issue-navigator {
  display: inline-flex;
  align-items: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 2px 4px;
  gap: 4px;
  margin-left: 6px;
}

.btn-nav-step {
  background: transparent;
  border: none;
  font-size: 11.5px;
  color: #475569;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.15s;
}
.btn-nav-step:hover {
  background: #e2e8f0;
  color: #0f172a;
}
.nav-step-index {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  padding: 0 4px;
}

.bar-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-gear-btn {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  color: #475569;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}
.settings-gear-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.bar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
