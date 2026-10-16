<script setup lang="ts">
import { ref } from 'vue';
import { UploadCloud, CheckCircle2, Paperclip } from 'lucide-vue-next';
import ReviewModeDropdown from './ReviewModeDropdown.vue';

defineProps<{
  selectedFile: File | null;
  mode: 'fast' | 'deep' | 'checklist' | 'compare';
  hasReference: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:selectedFile', file: File | null): void;
  (e: 'update:mode', mode: 'fast' | 'deep' | 'checklist' | 'compare'): void;
  (e: 'toggle-reference'): void;
}>();

const fileInputRef = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    emit('update:selectedFile', target.files[0]);
  }
};

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    emit('update:selectedFile', e.dataTransfer.files[0]);
  }
};

const triggerFileInput = () => {
  fileInputRef.value?.click();
};
</script>

<template>
  <div
    class="upload-dropzone-card"
    :class="{ dragging: isDragging }"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <input
      ref="fileInputRef"
      type="file"
      accept=".docx,.doc"
      class="hidden-file-input"
      @change="handleFileSelect"
    />

    <div class="dropzone-center-content" @click="triggerFileInput">
      <div class="upload-icon-circle">
        <UploadCloud :size="24" />
      </div>
      <p class="dropzone-text">
        拖拽或复制合同文件，或 <span class="action-highlight">选择文件</span>
      </p>
      <div class="format-badges-row">
        <span class="format-chip docx">
          <span class="file-icon-w">W</span> 文字版 Word 合同文档 (.docx, .doc)
        </span>
      </div>

      <div v-if="selectedFile" class="selected-file-banner" @click.stop>
        <CheckCircle2 :size="16" class="check-ic" />
        <span class="file-name">{{ selectedFile.name }} ({{ (selectedFile.size / 1024).toFixed(1) }} KB)</span>
        <button class="clear-file-btn" @click="emit('update:selectedFile', null)">清除</button>
      </div>
    </div>

    <div class="card-bottom-bar" @click.stop>
      <div class="bottom-left-controls">
        <ReviewModeDropdown
          :model-value="mode"
          @update:model-value="emit('update:mode', $event)"
        />
        <button
          class="ref-materials-btn"
          :class="{ active: hasReference }"
          @click="emit('toggle-reference')"
        >
          <Paperclip :size="13" />
          <span>参考资料</span>
        </button>
      </div>
      <div class="bottom-right-stats">
        <span>{{ selectedFile ? '1' : '0' }} 项</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-dropzone-card {
  width: 100%;
  background: #ffffff;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  position: relative;
  transition: all 0.2s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}
.upload-dropzone-card:hover, .upload-dropzone-card.dragging {
  border-color: var(--brand-primary);
  background: #f8fafc;
}
.hidden-file-input { display: none; }
.dropzone-center-content {
  padding: 44px 20px 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}
.upload-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #f1f5f9;
  color: var(--brand-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}
.dropzone-text { font-size: 14px; color: #334155; margin-bottom: 12px; }
.action-highlight { color: var(--brand-primary); font-weight: 600; }
.format-badges-row { display: flex; gap: 12px; }
.format-chip { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #64748b; }
.file-icon-w { background: var(--brand-primary); color: #fff; font-weight: 800; font-size: 9px; padding: 1px 4px; border-radius: 2px; }

.selected-file-banner {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12.5px;
  color: #1e40af;
}
.check-ic { color: var(--brand-primary); }
.clear-file-btn { background: none; border: none; color: #ef4444; cursor: pointer; font-size: 11px; }

.card-bottom-bar {
  border-top: 1px solid #f1f5f9;
  padding: 10px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bottom-left-controls { display: flex; align-items: center; gap: 12px; }
.ref-materials-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
}
.ref-materials-btn.active {
  background: #eff6ff;
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}
.bottom-right-stats { font-size: 12px; color: #9ca3af; }
</style>
