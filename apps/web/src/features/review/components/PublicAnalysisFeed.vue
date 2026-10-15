<script setup lang="ts">
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { AlertTriangle } from 'lucide-vue-next';

interface ProvisionalItem {
  item_id: string;
  clause_id: string;
  title: string;
  severity: 'high' | 'medium' | 'low';
  evidence: string;
  public_analysis: string;
  proposal: string;
}

defineProps<{
  items: ProvisionalItem[];
}>();
</script>

<template>
  <div class="analysis-feed-container">
    <div class="feed-header">
      <span class="feed-title">条款审查意见清单 (已识别 {{ items.length }} 项)</span>
      <span class="feed-badge">合规审查要点</span>
    </div>

    <div v-if="items.length === 0" class="empty-feed">
      <div class="pulse-indicator"></div>
      <span>正在逐项核验条款合规性与法律责任风险，意见将在此实时同步...</span>
    </div>

    <div v-else class="feed-list">
      <div v-for="item in items" :key="item.item_id" class="feed-card animate-fade-in">
        <div class="card-top">
          <div class="card-clause-title">
            <AlertTriangle :size="14" class="risk-icon" />
            <span class="clause-num">{{ item.clause_id }}</span>
            <span class="finding-title">{{ item.title }}</span>
          </div>
          <BaseBadge :variant="item.severity" size="sm">
            {{ item.severity === 'high' ? '高风险' : item.severity === 'medium' ? '中风险' : '低风险' }}
          </BaseBadge>
        </div>

        <div class="card-quote">
          <span class="quote-label">原文依据：</span>
          <span class="quote-text">{{ item.evidence }}</span>
        </div>

        <div class="card-analysis">
          <span class="analysis-label">法务评述：</span>
          <span>{{ item.public_analysis }}</span>
        </div>

        <div class="card-proposal">
          <span class="proposal-label">对策方向：</span>
          <span>{{ item.proposal }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.analysis-feed-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--text-muted);
}
.feed-title {
  font-weight: 600;
  color: var(--text-main);
}
.feed-badge {
  font-size: 11px;
  color: var(--text-dim);
}

.empty-feed {
  padding: 30px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px dashed var(--border-subtle);
}

.pulse-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--brand-primary);
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

.feed-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-clause-title {
  display: flex;
  align-items: center;
  gap: 6px;
}
.risk-icon { color: var(--risk-high-text); }
.clause-num { font-weight: 700; color: var(--brand-primary); }
.finding-title { font-weight: 600; color: var(--text-main); }

.card-quote {
  color: var(--text-muted);
  font-size: 12px;
}
.quote-label { color: var(--text-dim); }

.card-analysis {
  color: var(--text-main);
  line-height: 1.45;
}
.analysis-label { color: var(--risk-medium-text); font-weight: 500; }

.card-proposal {
  color: var(--risk-low-text);
}
.proposal-label { font-weight: 500; }
</style>
