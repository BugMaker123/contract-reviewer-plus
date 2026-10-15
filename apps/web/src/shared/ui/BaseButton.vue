<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline' | 'success';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
}>();
</script>

<template>
  <button
    class="base-btn"
    :class="[
      `variant-${variant || 'primary'}`,
      `size-${size || 'md'}`,
      { 'is-loading': loading, 'is-disabled': disabled || loading }
    ]"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="spinner"></span>
    <span class="btn-content">
      <slot />
    </span>
  </button>
</template>

<style scoped>
.base-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: var(--font-sans);
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  user-select: none;
}

.size-sm {
  padding: 4px 10px;
  font-size: 12px;
}
.size-md {
  padding: 7px 16px;
  font-size: 13.5px;
}
.size-lg {
  padding: 10px 22px;
  font-size: 15px;
}

.variant-primary {
  background: var(--brand-primary);
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}
.variant-primary:hover:not(:disabled) {
  background: var(--brand-hover);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
}

.variant-secondary {
  background: #ffffff;
  color: #334155;
  border-color: #cbd5e1;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.variant-secondary:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #94a3b8;
  color: #0f172a;
}

.variant-danger {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}
.variant-danger:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #ef4444;
}

.variant-success {
  background: #f0fdf4;
  color: #16a34a;
  border-color: #bbf7d0;
}
.variant-success:hover:not(:disabled) {
  background: #dcfce7;
  border-color: #15803d;
}

.variant-ghost {
  background: transparent;
  color: #64748b;
}
.variant-ghost:hover:not(:disabled) {
  color: #0f172a;
  background: #f1f5f9;
}

.variant-outline {
  background: #ffffff;
  border-color: #cbd5e1;
  color: #334155;
}
.variant-outline:hover:not(:disabled) {
  border-color: var(--border-focus);
  color: var(--border-focus);
}

.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
