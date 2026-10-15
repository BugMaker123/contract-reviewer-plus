<script setup lang="ts">
defineProps<{
  variant?: 'high' | 'medium' | 'low' | 'success' | 'warning' | 'neutral' | 'info';
  size?: 'sm' | 'md';
}>();
</script>

<template>
  <span class="base-badge" :class="[`variant-${variant || 'neutral'}`, `size-${size || 'md'}`]">
    <span class="badge-dot" v-if="variant === 'high' || variant === 'medium' || variant === 'low'"></span>
    <slot />
  </span>
</template>

<style scoped>
.base-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-sans);
  font-weight: 600;
  border-radius: var(--radius-full);
  line-height: 1;
  letter-spacing: 0.02em;
}

.size-sm {
  padding: 2px 7px;
  font-size: 11px;
}
.size-md {
  padding: 4px 10px;
  font-size: 12px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.variant-high {
  background: var(--risk-high-bg);
  color: var(--risk-high-text);
  border: 1px solid var(--risk-high-border);
}

.variant-medium {
  background: var(--risk-medium-bg);
  color: var(--risk-medium-text);
  border: 1px solid var(--risk-medium-border);
}

.variant-low {
  background: var(--risk-low-bg);
  color: var(--risk-low-text);
  border: 1px solid var(--risk-low-border);
}

.variant-success {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.variant-warning {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.variant-neutral {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
}

.variant-info {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.35);
}
</style>
