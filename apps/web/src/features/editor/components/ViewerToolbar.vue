<script setup lang="ts">
import { Eye, Layers, FileText } from 'lucide-vue-next';

defineProps<{
  contractTitle: string;
  modelValue: 'markup' | 'original' | 'clean';
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: 'markup' | 'original' | 'clean'): void;
}>();
</script>

<template>
  <div class="viewer-toolbar">
    <div class="doc-meta">
      <FileText :size="15" class="doc-icon" />
      <span class="doc-title">{{ contractTitle }}</span>
    </div>

    <div class="view-mode-tabs">
      <button
        class="tab-btn"
        :class="{ active: modelValue === 'markup' }"
        @click="emit('update:modelValue', 'markup')"
      >
        <Layers :size="13" /> 全部修订标记
      </button>
      <button
        class="tab-btn"
        :class="{ active: modelValue === 'original' }"
        @click="emit('update:modelValue', 'original')"
      >
        原始合同文本
      </button>
      <button
        class="tab-btn"
        :class="{ active: modelValue === 'clean' }"
        @click="emit('update:modelValue', 'clean')"
      >
        <Eye :size="13" /> 最终清洁效果
      </button>
    </div>
  </div>
</template>

<style scoped>
.viewer-toolbar {
  height: 44px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
}
.doc-meta { display: flex; align-items: center; gap: 8px; }
.doc-icon { color: #60a5fa; }
.doc-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-main);
  max-width: 340px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.view-mode-tabs {
  display: flex;
  background: var(--bg-tertiary);
  padding: 2px;
  border-radius: var(--radius-sm);
  gap: 2px;
}
.tab-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s;
}
.tab-btn.active {
  background: var(--brand-primary);
  color: #fff;
}
</style>
