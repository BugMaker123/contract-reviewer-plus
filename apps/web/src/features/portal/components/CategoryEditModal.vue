<script setup lang="ts">
import { ref, watch } from 'vue';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import { AlertCircle } from 'lucide-vue-next';

const props = defineProps<{
  modelValue: boolean;
  isEditing: boolean;
  initialData?: {
    id: string;
    name: string;
    code: string;
    description?: string;
    sort_order: number;
  } | null;
  loading: boolean;
  error?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'save', payload: { name: string; code: string; description: string; sort_order: number }): void;
}>();

const formName = ref('');
const formCode = ref('');
const formDesc = ref('');
const formSort = ref(1);

watch(
  () => props.initialData,
  (val) => {
    if (val) {
      formName.value = val.name;
      formCode.value = val.code;
      formDesc.value = val.description || '';
      formSort.value = val.sort_order;
    } else {
      formName.value = '';
      formCode.value = '';
      formDesc.value = '';
      formSort.value = 1;
    }
  },
  { immediate: true }
);

const handleSave = () => {
  emit('save', {
    name: formName.value.trim(),
    code: formCode.value.trim(),
    description: formDesc.value.trim(),
    sort_order: Number(formSort.value)
  });
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    :title="isEditing ? '编辑合同业务分类' : '新建合同业务分类'"
    max-width="480px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="form-stack">
      <div v-if="error" class="form-error-banner">
        <AlertCircle :size="14" />
        <span>{{ error }}</span>
      </div>

      <div class="form-field">
        <label class="field-label">分类名称 <span class="req">*</span></label>
        <input v-model="formName" type="text" class="field-input" placeholder="例如：技术开发与实施类" />
      </div>

      <div class="form-field">
        <label class="field-label">分类编码 <span class="req">*</span></label>
        <input v-model="formCode" type="text" class="field-input" placeholder="例如：TECH_DEV" />
      </div>

      <div class="form-field">
        <label class="field-label">排序号</label>
        <input v-model.number="formSort" type="number" class="field-input" min="1" />
      </div>

      <div class="form-field">
        <label class="field-label">说明描述</label>
        <textarea v-model="formDesc" rows="3" class="field-textarea" placeholder="填写该分类适用的业务场景与合同类型..."></textarea>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:modelValue', false)">取消</BaseButton>
      <BaseButton variant="primary" :loading="loading" @click="handleSave">
        {{ isEditing ? '保存修改' : '确认新建' }}
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.form-stack { display: flex; flex-direction: column; gap: 14px; }
.form-error-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
}
.form-field { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 12px; font-weight: 600; color: #334155; }
.req { color: #dc2626; }
.field-input, .field-textarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 12.5px;
  outline: none;
}
.field-input:focus, .field-textarea:focus { border-color: var(--brand-primary); }
</style>
