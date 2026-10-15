<script setup lang="ts">
import { ref } from 'vue';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import type { IssueGroup } from '@/shared/types';
import { Send } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: boolean;
  issue: IssueGroup | null;
  mode: 'comment' | 'followup';
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'submit-comment', content: string): void;
  (e: 'submit-followup', question: string): void;
}>();

const inputContent = ref('');

const submit = () => {
  if (!inputContent.value.trim()) return;
  if (props.mode === 'comment') {
    emit('submit-comment', inputContent.value);
  } else {
    emit('submit-followup', inputContent.value);
  }
  inputContent.value = '';
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    :title="mode === 'comment' ? `复核备注 - ${issue?.clause_title}` : `条款合规咨询 - ${issue?.clause_title}`"
    max-width="540px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div v-if="issue" class="modal-body-stack">
      <!-- Existing items -->
      <div v-if="mode === 'comment'" class="history-list">
        <div v-if="issue.comments.length === 0" class="empty-hint">
          暂无复核备注，您可在此记录内部讨论或妥协底线。
        </div>
        <div v-for="c in issue.comments" :key="c.id" class="history-item">
          <div class="item-meta">
            <span class="item-author">{{ c.author }}</span>
            <span class="item-time">{{ c.created_at }}</span>
          </div>
          <div class="item-content">{{ c.content }}</div>
        </div>
      </div>

      <div v-else class="history-list">
        <div v-if="issue.followups.length === 0" class="empty-hint">
          您可以针对本条款的修改方案、谈判尺度或替代条款发起合规咨询探讨。
        </div>
        <div v-for="f in issue.followups" :key="f.id" class="history-item followup-item">
          <div class="qa-q">
            <span class="q-tag">咨询：</span>
            <span>{{ f.question }}</span>
          </div>
          <div class="qa-a">
            <span class="a-tag">合规参考：</span>
            <span>{{ f.answer }}</span>
          </div>
        </div>
      </div>

      <!-- Input box -->
      <div class="input-section">
        <textarea
          v-model="inputContent"
          class="custom-textarea"
          :placeholder="mode === 'comment' ? '请输入复核说明或处理备注...' : '请输入咨询问题，例如：若对方不同意删除违约责任上限，可采取何种替代合规方案？'"
          rows="3"
        ></textarea>

        <div class="input-actions">
          <BaseButton
            variant="primary"
            size="sm"
            :loading="loading"
            :disabled="!inputContent.trim()"
            @click="submit"
          >
            <Send :size="13" /> {{ mode === 'comment' ? '添加备注' : '提交咨询' }}
          </BaseButton>
        </div>
      </div>
    </div>
  </BaseDialog>
</template>

<style scoped>
.modal-body-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-list {
  max-height: 240px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 20px 10px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.history-item {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 12.5px;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 11px;
}
.item-author { font-weight: 600; color: var(--brand-primary); }
.item-time { color: var(--text-dim); }
.item-content { color: var(--text-main); }

.followup-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.qa-q { color: var(--text-main); font-weight: 500; }
.q-tag { color: var(--risk-medium-text); }
.qa-a { color: var(--text-main); line-height: 1.5; }
.a-tag { font-weight: 600; color: var(--risk-low-text); }

.input-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-textarea {
  width: 100%;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  padding: 10px 12px;
  font-family: var(--font-sans);
  font-size: 13px;
  resize: vertical;
  outline: none;
}
.custom-textarea:focus {
  border-color: var(--border-focus);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}
</style>
