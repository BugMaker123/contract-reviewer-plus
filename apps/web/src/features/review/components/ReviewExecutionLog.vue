<script setup lang="ts">
import { ref } from 'vue';
import { ChevronDown, ChevronRight, Terminal } from 'lucide-vue-next';

interface LogItem {
  seq: number;
  time: string;
  type: string;
  message: string;
}

defineProps<{
  logs: LogItem[];
}>();

const isOpen = ref(false);
</script>

<template>
  <div class="execution-log-container">
    <button class="log-toggle-header" @click="isOpen = !isOpen">
      <div class="toggle-left">
        <Terminal :size="14" />
        <span>审查执行日志 (共 {{ logs.length }} 条事件)</span>
      </div>
      <component :is="isOpen ? ChevronDown : ChevronRight" :size="16" />
    </button>

    <div v-if="isOpen" class="log-content-body animate-fade-in">
      <div v-for="log in logs" :key="log.seq" class="log-row">
        <span class="log-seq">#{{ log.seq }}</span>
        <span class="log-time">{{ log.time.split('T')[1]?.substring(0, 8) || log.time }}</span>
        <span class="log-type">[{{ log.type }}]</span>
        <span class="log-msg">{{ log.message }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.execution-log-container {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: var(--bg-tertiary);
  font-family: var(--font-mono);
  font-size: 11.5px;
  overflow: hidden;
}

.log-toggle-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-card);
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}
.log-toggle-header:hover {
  color: var(--text-main);
  background: var(--bg-card-hover);
}

.toggle-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.log-content-body {
  max-height: 160px;
  overflow-y: auto;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.log-row {
  display: flex;
  gap: 8px;
  color: var(--text-muted);
  line-height: 1.4;
}

.log-seq { color: var(--brand-primary); }
.log-time { color: var(--text-dim); }
.log-type { color: var(--brand-primary); font-weight: 500; }
.log-msg { color: var(--text-main); flex: 1; word-break: break-all; }
</style>
