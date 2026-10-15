<script setup lang="ts">
import { ref } from 'vue';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';

defineProps<{
  modelValue: boolean;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'submit', data: { file: File | null; title: string; stance: string }): void;
}>();

const title = ref('');
const stance = ref('我方(受托方)');
const selectedFile = ref<File | null>(null);

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0];
    if (!title.value) {
      title.value = selectedFile.value.name.replace(/\.[^/.]+$/, '');
    }
  }
};

const submit = () => {
  emit('submit', {
    file: selectedFile.value,
    title: title.value || '新上传合同',
    stance: stance.value
  });
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    title="新建合同审查任务"
    max-width="500px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="upload-form-stack">
      <div class="form-item">
        <label class="form-lbl">合同标题</label>
        <input v-model="title" type="text" class="form-input" placeholder="请输入合同名称（留空使用文件名）" />
      </div>

      <div class="form-item">
        <label class="form-lbl">选择本地 DOCX 合同文件</label>
        <input type="file" accept=".docx" class="form-file-input" @change="handleFileChange" />
      </div>

      <div class="form-item">
        <label class="form-lbl">我方立场预设</label>
        <select v-model="stance" class="form-input">
          <option value="我方(受托方)">我方 (受托方 / 乙方)</option>
          <option value="我方(委托方)">我方 (委托方 / 甲方)</option>
          <option value="我方(采购方)">我方 (采购方 / 买方)</option>
          <option value="我方(供应商)">我方 (供应商 / 卖方)</option>
          <option value="中立对等">中立对等</option>
        </select>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:modelValue', false)">取消</BaseButton>
      <BaseButton variant="primary" :loading="loading" @click="submit">
        开始创建并进入工作台
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.upload-form-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-lbl {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-main);
}
.form-input {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  font-size: 13px;
  outline: none;
}
.form-file-input {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
