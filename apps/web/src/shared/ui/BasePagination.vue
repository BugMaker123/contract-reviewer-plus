<script setup lang="ts">
import { computed } from 'vue';
import { ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = defineProps<{
  total: number;
  page: number;
  pageSize: number;
}>();

const emit = defineEmits<{
  (e: 'update:page', page: number): void;
}>();

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1);

const canPrev = computed(() => props.page > 1);
const canNext = computed(() => props.page < totalPages.value);

const prev = () => {
  if (canPrev.value) emit('update:page', props.page - 1);
};

const next = () => {
  if (canNext.value) emit('update:page', props.page + 1);
};
</script>

<template>
  <div class="pagination-container">
    <span class="total-info">共 {{ total }} 条记录，第 {{ page }} / {{ totalPages }} 页</span>

    <div class="pager-buttons">
      <button
        class="page-btn"
        :disabled="!canPrev"
        @click="prev"
      >
        <ChevronLeft :size="14" />
        <span>上一页</span>
      </button>

      <span class="current-page-pill">{{ page }}</span>

      <button
        class="page-btn"
        :disabled="!canNext"
        @click="next"
      >
        <span>下一页</span>
        <ChevronRight :size="14" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-top: 1px solid #eef2f6;
  font-size: 12.5px;
  color: #64748b;
  user-select: none;
}

.total-info {
  color: #64748b;
}

.pager-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 12px;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
}
.page-btn:hover:not(:disabled) {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  background: #eff6ff;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.current-page-pill {
  min-width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: var(--brand-primary);
  color: #ffffff;
  font-weight: 600;
  font-size: 12px;
}
</style>
