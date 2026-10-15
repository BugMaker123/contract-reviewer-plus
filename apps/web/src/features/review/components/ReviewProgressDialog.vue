<script setup lang="ts">
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import ReviewProgressHeader from './ReviewProgressHeader.vue';
import PublicAnalysisFeed from './PublicAnalysisFeed.vue';
import ReviewExecutionLog from './ReviewExecutionLog.vue';

defineProps<{
  modelValue: boolean;
  currentStage: string;
  isCancelling: boolean;
  isComplete: boolean;
  isFailed: boolean;
  errorMessage?: string;
  provisionalFindings: any[];
  executionLogs: any[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'cancel'): void;
  (e: 'finish'): void;
}>();
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    title="合同合规性审查分析"
    max-width="720px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="dialog-content-stack">
      <ReviewProgressHeader
        :current-stage="currentStage"
        :is-cancelling="isCancelling"
        :is-complete="isComplete"
        @cancel="emit('cancel')"
      />

      <div v-if="isFailed" class="error-banner animate-fade-in">
        <span class="error-title">审查未能全部完成：</span>
        <span class="error-msg">{{ errorMessage || '发生内部异常或已达最大重试限制' }}</span>
      </div>

      <PublicAnalysisFeed :items="provisionalFindings" />

      <ReviewExecutionLog :logs="executionLogs" />
    </div>

    <template #footer>
      <BaseButton
        v-if="isComplete || isFailed"
        variant="primary"
        @click="emit('finish')"
      >
        {{ isComplete ? '查看审查修订稿' : '关闭' }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.dialog-content-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.error-banner {
  padding: 10px 14px;
  background: var(--risk-high-bg);
  border: 1px solid var(--risk-high-border);
  border-radius: var(--radius-sm);
  color: var(--risk-high-text);
  font-size: 13px;
  display: flex;
  gap: 6px;
}
.error-title {
  font-weight: 600;
}
</style>
