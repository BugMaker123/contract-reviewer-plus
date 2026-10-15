<script setup lang="ts">
import { ref } from 'vue';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import { Download, FileCheck, FileCode, FileText } from 'lucide-vue-next';

defineProps<{
  modelValue: boolean;
  contractTitle: string;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'export', kind: 'clean_draft' | 'track_changes' | 'review_report'): void;
}>();

const selectedKind = ref<'clean_draft' | 'track_changes' | 'review_report'>('clean_draft');

const exportOptions = [
  {
    kind: 'clean_draft',
    title: '清洁稿 (Clean Draft)',
    desc: '已采纳的修改将直接合并入正文，已拒绝的修改予以剔除，适合用于归档或终版签约。',
    icon: FileCheck
  },
  {
    kind: 'track_changes',
    title: '带修订标记稿 (Track Changes)',
    desc: '完整保留 Word 原生插入、删除及批注标记，支持使用 Office / WPS 进一步离线复审。',
    icon: FileCode
  },
  {
    kind: 'review_report',
    title: '合同法务审查意见书',
    desc: '生成结构化法务审查报告，包含风险评述、原文证据与各条款处理决定记录。',
    icon: FileText
  }
];
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    title="导出合同文档与审查成果"
    max-width="580px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="export-modal-stack">
      <div class="export-hint">
        当前导出将严格基于已持久化的工作版本生成不可变副本，保证与当前复核状态 100% 一致。
      </div>

      <div class="options-grid">
        <div
          v-for="opt in exportOptions"
          :key="opt.kind"
          class="export-option-card"
          :class="{ selected: selectedKind === opt.kind }"
          @click="selectedKind = opt.kind as any"
        >
          <div class="card-icon-col">
            <component :is="opt.icon" :size="24" class="opt-icon" />
          </div>
          <div class="card-info-col">
            <div class="card-title">{{ opt.title }}</div>
            <div class="card-desc">{{ opt.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:modelValue', false)">
        取消
      </BaseButton>
      <BaseButton
        variant="primary"
        :loading="loading"
        @click="emit('export', selectedKind)"
      >
        <Download :size="14" /> 确认生成并下载
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.export-modal-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-hint {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
  background: var(--brand-subtle);
  border: 1px solid var(--border-subtle);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
}

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.export-option-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s ease;
}
.export-option-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-focus);
}
.export-option-card.selected {
  border-color: var(--brand-primary);
  background: var(--brand-subtle);
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.12);
}

.card-icon-col {
  color: var(--brand-primary);
  display: flex;
  align-items: center;
}

.card-info-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}
.card-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
}
</style>
