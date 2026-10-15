<script setup lang="ts">
defineProps<{
  modelValue: string;
  options: { label: string; value: string }[];
  label?: string;
}>();

defineEmits<{
  (e: 'update:modelValue', val: string): void;
}>();
</script>

<template>
  <div class="select-wrapper">
    <label v-if="label" class="select-label">{{ label }}</label>
    <div class="custom-select-container">
      <select
        :value="modelValue"
        class="custom-select"
        @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option
          v-for="opt in options"
          :key="opt.value"
          :value="opt.value"
          class="select-option"
        >
          {{ opt.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<style scoped>
.select-wrapper {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
}

.select-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.custom-select-container {
  position: relative;
}

.custom-select {
  appearance: none;
  background: #ffffff;
  color: var(--text-main);
  border: 1px solid #cbd5e1;
  border-radius: var(--radius-sm);
  padding: 6px 30px 6px 12px;
  font-family: var(--font-sans);
  font-size: 13px;
  cursor: pointer;
  outline: none;
  transition: all 0.15s;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 14px;
}

.custom-select:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.select-option {
  background: #ffffff;
  color: var(--text-main);
}
</style>
