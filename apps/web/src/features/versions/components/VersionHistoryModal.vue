<script setup lang="ts">
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import type { DocumentVersion } from '@/shared/types';
import { GitCommit } from 'lucide-vue-next';

defineProps<{
  modelValue: boolean;
  versions: DocumentVersion[];
  currentVersionId?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'select-version', versionId: string): void;
}>();

const getKindLabel = (kind: string) => {
  switch (kind) {
    case 'original': return '初始上传版本';
    case 'ai_proposal': return '系统审查建议稿';
    case 'verified': return '复核采纳版本';
    case 'user_saved': return '人工保存版本';
    default: return kind;
  }
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    title="不可变文档版本历史"
    max-width="580px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="version-timeline-container">
      <div
        v-for="ver in versions"
        :key="ver.id"
        class="version-item"
        :class="{ 'is-current': ver.id === currentVersionId }"
        @click="emit('select-version', ver.id)"
      >
        <div class="item-left-marker">
          <GitCommit :size="16" class="commit-icon" />
          <div class="timeline-line"></div>
        </div>

        <div class="item-body">
          <div class="item-top">
            <span class="version-id-tag">{{ ver.id }}</span>
            <BaseBadge :variant="ver.id === currentVersionId ? 'success' : 'neutral'" size="sm">
              {{ ver.id === currentVersionId ? '当前工作 HEAD' : getKindLabel(ver.kind) }}
            </BaseBadge>
          </div>

          <div class="item-summary">{{ ver.summary || getKindLabel(ver.kind) }}</div>

          <div class="item-footer">
            <span class="footer-meta">操作人: {{ ver.created_by }}</span>
            <span class="footer-meta">时间: {{ ver.created_at.split('T')[0] }} {{ ver.created_at.split('T')[1]?.substring(0, 5) }}</span>
            <span class="hash-text">Hash: {{ ver.content_hash.substring(0, 8) }}</span>
          </div>
        </div>
      </div>
    </div>
  </BaseDialog>
</template>

<style scoped>
.version-timeline-container {
  display: flex;
  flex-direction: column;
  max-height: 400px;
  overflow-y: auto;
  padding: 4px;
}

.version-item {
  display: flex;
  gap: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}
.version-item:hover {
  background: var(--bg-card-hover);
}
.version-item.is-current {
  background: var(--brand-subtle);
  border: 1px solid var(--brand-primary);
}

.item-left-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding-top: 4px;
}
.commit-icon { color: var(--brand-primary); }
.timeline-line {
  flex: 1;
  width: 2px;
  background: var(--border-subtle);
  margin-top: 4px;
}

.item-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-bottom: 14px;
}

.item-top {
  display: flex;
  align-items: center;
  gap: 8px;
}
.version-id-tag {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--brand-primary);
  font-weight: 600;
}

.item-summary {
  font-size: 13px;
  color: var(--text-main);
  font-weight: 500;
}

.item-footer {
  display: flex;
  gap: 12px;
  font-size: 11.5px;
  color: var(--text-dim);
}
.hash-text {
  font-family: var(--font-mono);
}
</style>
