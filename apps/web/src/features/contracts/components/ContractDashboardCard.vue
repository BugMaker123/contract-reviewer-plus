<script setup lang="ts">
import type { Contract } from '@/shared/types';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { ArrowRight } from 'lucide-vue-next';

defineProps<{
  contract: Contract;
}>();

const emit = defineEmits<{
  (e: 'click'): void;
}>();
</script>

<template>
  <div class="contract-dashboard-card animate-fade-in" @click="emit('click')">
    <div class="card-top-meta">
      <BaseBadge variant="info" size="sm">立场: {{ contract.stance }}</BaseBadge>
      <BaseBadge
        :variant="contract.review_status === 'verified' ? 'success' : contract.review_status === 'reviewed' ? 'warning' : 'neutral'"
        size="sm"
      >
        {{ contract.review_status === 'verified' ? '已完成复核' : contract.review_status === 'reviewed' ? '待复核' : '未审查' }}
      </BaseBadge>
    </div>

    <h3 class="contract-card-title">{{ contract.title }}</h3>

    <div class="card-info-pills">
      <span class="info-pill font-mono">Head: {{ contract.head_version_id }}</span>
      <span class="info-pill">修订轮次: r{{ contract.revision }}</span>
    </div>

    <div class="card-footer-bar">
      <span class="card-time">更新时间: {{ contract.updated_at.split('T')[0] }}</span>
      <span class="enter-btn">
        进入工作台 <ArrowRight :size="14" />
      </span>
    </div>
  </div>
</template>

<style scoped>
.contract-dashboard-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-md);
  padding: 18px 20px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.contract-dashboard-card:hover {
  background: #ffffff;
  border-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.card-top-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.contract-card-title {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.45;
  height: 44px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-info-pills {
  display: flex;
  gap: 8px;
}
.info-pill {
  font-size: 11px;
  color: #475569;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}
.font-mono { font-family: var(--font-mono); }

.card-footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #f1f5f9;
  font-size: 12px;
  color: #64748b;
}
.enter-btn {
  color: #2563eb;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
