<script setup lang="ts">
import { ref } from 'vue';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import BaseSelect from '@/shared/ui/BaseSelect.vue';

const props = defineProps<{
  modelValue: boolean;
  currentStance: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'save-settings', stance: string, focusAreas: string[]): void;
}>();

const stanceOptions = [
  { label: '我方 (受托方 / 乙方)', value: '我方(受托方)' },
  { label: '我方 (委托方 / 甲方)', value: '我方(委托方)' },
  { label: '我方 (采购方 / 买方)', value: '我方(采购方)' },
  { label: '我方 (供应商 / 卖方)', value: '我方(供应商)' },
  { label: '中立第三方 / 双向对等', value: '中立对等' },
];

const selectedStance = ref(props.currentStance || '我方(受托方)');

const allFocusAreas = [
  { id: 'liability', label: '违约赔偿上限与间接损失排除' },
  { id: 'ip', label: '既有知识产权保护与成果权属' },
  { id: 'termination', label: '单方解除权平衡与整改宽限期' },
  { id: 'payment', label: '付款节点、发票前置与逾期利息' },
  { id: 'dispute', label: '争议管辖与仲裁地最优化' },
];

const selectedFocus = ref<string[]>([
  '违约赔偿上限与间接损失排除',
  '既有知识产权保护与成果权属',
  '单方解除权平衡与整改宽限期',
  '付款节点、发票前置与逾期利息'
]);

const toggleFocus = (label: string) => {
  if (selectedFocus.value.includes(label)) {
    selectedFocus.value = selectedFocus.value.filter((x) => x !== label);
  } else {
    selectedFocus.value.push(label);
  }
};

const save = () => {
  emit('save-settings', selectedStance.value, selectedFocus.value);
  emit('update:modelValue', false);
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    title="审查规则与商务立场配置"
    max-width="500px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="settings-form-stack">
      <div class="form-group">
        <label class="group-label">我方核心商务立场</label>
        <BaseSelect
          v-model="selectedStance"
          :options="stanceOptions"
        />
        <span class="field-hint">审查引擎将根据此立场与重点清单分析法律风险并拟定修订方案。</span>
      </div>

      <div class="form-group">
        <label class="group-label">重点审查专项与风险关注</label>
        <div class="focus-checkbox-grid">
          <label
            v-for="fa in allFocusAreas"
            :key="fa.id"
            class="checkbox-card"
            :class="{ active: selectedFocus.includes(fa.label) }"
          >
            <input
              type="checkbox"
              :checked="selectedFocus.includes(fa.label)"
              @change="toggleFocus(fa.label)"
            />
            <span class="cb-label">{{ fa.label }}</span>
          </label>
        </div>
      </div>
    </div>

    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:modelValue', false)">
        取消
      </BaseButton>
      <BaseButton variant="primary" @click="save">
        保存审查配置
      </BaseButton>
    </template>
  </BaseDialog>
</template>

<style scoped>
.settings-form-stack {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.group-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.field-hint {
  font-size: 12px;
  color: var(--text-dim);
}

.focus-checkbox-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.checkbox-card:hover {
  background: var(--bg-card-hover);
}
.checkbox-card.active {
  background: var(--brand-subtle);
  border-color: var(--brand-primary);
  color: var(--text-main);
}
.cb-label {
  user-select: none;
}
</style>
