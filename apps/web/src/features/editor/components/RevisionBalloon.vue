<script setup lang="ts">
import type { RevisionOperation } from '@/shared/types';
import { Check, X } from 'lucide-vue-next';

defineProps<{
  op: RevisionOperation;
}>();

const emit = defineEmits<{
  (e: 'accept', opId: string): void;
  (e: 'reject', opId: string): void;
}>();
</script>

<template>
  <div class="revision-balloon" :class="`status-${op.status}`">
    <div class="balloon-header">
      <span class="author-badge">{{ op.author }}</span>
      <span class="op-status-text">
        {{ op.status === 'accepted' ? '已采纳' : op.status === 'rejected' ? '已拒绝' : '待复核' }}
      </span>
    </div>
    <div class="balloon-reason">{{ op.public_reason }}</div>
    <div v-if="op.status === 'pending'" class="balloon-actions">
      <button class="action-btn accept" @click="emit('accept', op.id)" title="采纳此修订">
        <Check :size="13" /> 采纳
      </button>
      <button class="action-btn reject" @click="emit('reject', op.id)" title="拒绝此修订">
        <X :size="13" /> 拒绝
      </button>
    </div>
  </div>
</template>

<style scoped>
.revision-balloon {
  width: 250px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 8px 10px;
  font-size: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.revision-balloon.status-accepted { border-color: #16a34a; background: #f0fdf4; }
.revision-balloon.status-rejected { border-color: #dc2626; background: #fef2f2; }
.balloon-header { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 11px; }
.author-badge { font-weight: 600; color: #1e3a8a; }
.op-status-text { color: #475569; font-weight: 500; }
.balloon-reason { color: #334155; margin-bottom: 8px; line-height: 1.4; font-size: 12px; }
.balloon-actions { display: flex; gap: 6px; }
.action-btn { border: none; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 3px; cursor: pointer; display: flex; align-items: center; gap: 3px; }
.action-btn.accept { background: #15803d; color: #fff; }
.action-btn.reject { background: #b91c1c; color: #fff; }
</style>
