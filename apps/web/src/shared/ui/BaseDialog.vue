<script setup lang="ts">
import { X } from 'lucide-vue-next';

defineProps<{
  modelValue: boolean;
  title: string;
  maxWidth?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'close'): void;
}>();

const close = () => {
  emit('update:modelValue', false);
  emit('close');
};
</script>

<template>
  <div v-if="modelValue" class="dialog-backdrop" @click.self="close">
    <div class="dialog-panel glass-panel animate-fade-in" :style="{ maxWidth: maxWidth || '560px' }">
      <div class="dialog-header">
        <h3 class="dialog-title">{{ title }}</h3>
        <button class="close-btn" @click="close" aria-label="关闭">
          <X :size="18" />
        </button>
      </div>

      <div class="dialog-body">
        <slot />
      </div>

      <div v-if="$slots.footer" class="dialog-footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.dialog-panel {
  width: 100%;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.dialog-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  background: #ffffff;
}

.dialog-title {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  transition: all 0.15s;
}
.close-btn:hover {
  color: #0f172a;
  background: #f1f5f9;
}

.dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  background: #ffffff;
}

.dialog-footer {
  padding: 14px 20px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
