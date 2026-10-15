<script setup lang="ts">
import BaseButton from '@/shared/ui/BaseButton.vue';

defineProps<{
  currentStage: string;
  isCancelling: boolean;
  isComplete: boolean;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
}>();

const stages = [
  { key: 'prepare_snapshot', label: '准备快照' },
  { key: 'build_context', label: '条款提取' },
  { key: 'analyze_clauses', label: '法务研判' },
  { key: 'validate_findings', label: '边界校验' },
  { key: 'consolidate_issues', label: '归并问题' },
  { key: 'compose_revisions', label: '生成修订' },
  { key: 'publish_result', label: '发布结果' },
];

const getStageIndex = (key: string) => stages.findIndex((s) => s.key === key);
</script>

<template>
  <div class="progress-header-container">
    <div class="stage-stepper">
      <div
        v-for="(st, idx) in stages"
        :key="st.key"
        class="step-item"
        :class="{
          active: currentStage === st.key,
          passed: getStageIndex(currentStage) > idx || isComplete
        }"
      >
        <div class="step-dot">
          <span v-if="getStageIndex(currentStage) > idx || isComplete">✓</span>
          <span v-else>{{ idx + 1 }}</span>
        </div>
        <span class="step-label">{{ st.label }}</span>
      </div>
    </div>

    <div class="header-action-zone">
      <BaseButton
        v-if="!isComplete"
        variant="danger"
        size="sm"
        :loading="isCancelling"
        @click="emit('cancel')"
      >
        取消审查
      </BaseButton>
    </div>
  </div>
</template>

<style scoped>
.progress-header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.stage-stepper {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-dim);
}

.step-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 11px;
}

.step-item.active {
  color: var(--brand-primary);
  font-weight: 600;
}
.step-item.active .step-dot {
  background: var(--brand-subtle);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.step-item.passed {
  color: var(--risk-low-text);
}
.step-item.passed .step-dot {
  background: var(--risk-low-bg);
  border-color: var(--risk-low-border);
  color: var(--risk-low-text);
}
</style>
