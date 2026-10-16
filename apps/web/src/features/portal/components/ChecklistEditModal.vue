<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '@/shared/http/client';
import BaseDialog from '@/shared/ui/BaseDialog.vue';
import BaseButton from '@/shared/ui/BaseButton.vue';
import { AlertCircle, Sparkles, Terminal } from 'lucide-vue-next';

export interface ChecklistItemData {
  id?: string;
  category_id: string;
  title: string;
  risk_level: 'high' | 'medium' | 'low';
  standard_clause?: string;
  check_prompt?: string;
  prompt_template?: string;
  is_enabled: boolean;
  sort_order: number;
}

export interface CategoryOption {
  id: string;
  name: string;
}

const props = defineProps<{
  modelValue: boolean;
  item: ChecklistItemData | null;
  categories: CategoryOption[];
  defaultCategoryId?: string;
  nextSortOrder?: number;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'saved'): void;
}>();

const formCatId = ref('');
const formTitle = ref('');
const formRisk = ref<'high' | 'medium' | 'low'>('high');
const formClause = ref('');
const formPrompt = ref('');
const formPromptTemplate = ref('');
const formSort = ref(1);
const formEnabled = ref(true);
const formError = ref('');
const isSaving = ref(false);

watch(
  () => props.modelValue,
  (visible) => {
    if (!visible) return;
    formError.value = '';
    if (props.item) {
      formCatId.value = props.item.category_id;
      formTitle.value = props.item.title;
      formRisk.value = props.item.risk_level;
      formClause.value = props.item.standard_clause || '';
      formPrompt.value = props.item.check_prompt || '';
      formPromptTemplate.value = props.item.prompt_template || '';
      formSort.value = props.item.sort_order;
      formEnabled.value = props.item.is_enabled;
    } else {
      formCatId.value = props.defaultCategoryId || (props.categories[0]?.id || '');
      formTitle.value = '';
      formRisk.value = 'high';
      formClause.value = '';
      formPrompt.value = '';
      formPromptTemplate.value = '';
      formSort.value = props.nextSortOrder || 1;
      formEnabled.value = true;
    }
  }
);

const generateStandardPrompt = () => {
  const title = formTitle.value.trim() || '本项法律合规标准';
  const clause = formClause.value.trim() || '需符合对等商业惯例与法律强制性规范';
  formPromptTemplate.value = `请作为资深企业法务专家，从【{stance}】立场深度审查合同条款【{clause_text}】。\n` +
    `审查目标：核查条款是否符合【${title}】的法务风控标准。\n` +
    `合规标准参考：【{standard_clause}】（${clause}）。\n` +
    `若原条款偏离上述原则，请精准指出法律风险依据，并给出供我方采纳的替换性修订表述。`;
};

const handleSave = async () => {
  if (!formTitle.value.trim() || !formCatId.value) {
    formError.value = '请填写审查要点名称并选择所属业务分类';
    return;
  }
  isSaving.value = true;
  formError.value = '';
  try {
    const payload = {
      category_id: formCatId.value,
      title: formTitle.value.trim(),
      risk_level: formRisk.value,
      standard_clause: formClause.value.trim(),
      check_prompt: formPrompt.value.trim(),
      prompt_template: formPromptTemplate.value.trim(),
      sort_order: Number(formSort.value),
      is_enabled: formEnabled.value
    };
    if (props.item?.id) {
      await api.put(`/checklists/${props.item.id}`, payload);
    } else {
      await api.post('/checklists', payload);
    }
    emit('update:modelValue', false);
    emit('saved');
  } catch (err: any) {
    formError.value = err?.response?.data?.detail || '保存失败';
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <BaseDialog
    :model-value="modelValue"
    :title="item ? '编辑审查清单标准与 Prompt' : '新建审查清单标准与 Prompt'"
    max-width="620px"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="form-stack">
      <div v-if="formError" class="form-error-banner">
        <AlertCircle :size="14" />
        <span>{{ formError }}</span>
      </div>

      <div class="form-field">
        <label class="field-label">绑定业务分类 <span class="req">*</span></label>
        <select v-model="formCatId" class="field-select">
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
      </div>

      <div class="form-field">
        <label class="field-label">审查要点名称 <span class="req">*</span></label>
        <input v-model="formTitle" type="text" class="field-input" placeholder="例如：知识产权归属与衍生授权保留" />
      </div>

      <div class="form-row-2">
        <div class="form-field">
          <label class="field-label">预设风险级别</label>
          <select v-model="formRisk" class="field-select">
            <option value="high">高风险（法律底线/核心利益）</option>
            <option value="medium">中风险（常规商务争议）</option>
            <option value="low">低风险（规范性建议/文字微调）</option>
          </select>
        </div>
        <div class="form-field">
          <label class="field-label">排序权重</label>
          <input v-model="formSort" type="number" min="1" class="field-input" />
        </div>
      </div>

      <div class="form-field">
        <label class="field-label">标准示范条款（期望合同应包含的标准范式）</label>
        <textarea
          v-model="formClause"
          rows="3"
          class="field-textarea"
          placeholder="例如：签约前各方拥有的背景知识产权仍归各自所有；交付物知识产权转让不包含通用底层工具与第三方开源代码。"
        ></textarea>
      </div>

      <div class="form-field">
        <label class="field-label">核查要点与人工复核指引</label>
        <input
          v-model="formPrompt"
          type="text"
          class="field-input"
          placeholder="例如：防范任意解除权及突击解约损害我方在途已投入研发成本"
        />
      </div>

      <!-- Business Prompt Customization Section -->
      <div class="prompt-custom-box">
        <div class="prompt-head-row">
          <div class="prompt-head-left">
            <Terminal :size="14" class="prompt-ic" />
            <label class="field-label bold-label">业务定制 AI 审查提示词 (Prompt Template)</label>
          </div>
          <button type="button" class="generate-prompt-btn" @click="generateStandardPrompt">
            <Sparkles :size="12" /> 生成标准 Prompt 模板
          </button>
        </div>
        <textarea
          v-model="formPromptTemplate"
          rows="4"
          class="field-textarea code-font"
          placeholder="配置与该清单绑定的专属提示词。审查时大模型与分析引擎将以此提示词为核心指令进行条款级研判..."
        ></textarea>
        <div class="prompt-var-tags">
          <span class="var-hint">可用变量占位符：</span>
          <code class="var-tag" @click="formPromptTemplate += '{clause_text}'">{clause_text}</code>
          <code class="var-tag" @click="formPromptTemplate += '{standard_clause}'">{standard_clause}</code>
          <code class="var-tag" @click="formPromptTemplate += '{stance}'">{stance}</code>
        </div>
      </div>

      <div class="form-field-switch">
        <label class="switch-label">
          <input v-model="formEnabled" type="checkbox" class="switch-inp" />
          <span>启用该项审查标准（勾选后将在审查清单选择器中默认展示并执行）</span>
        </label>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer-actions">
        <BaseButton variant="secondary" @click="emit('update:modelValue', false)">取消</BaseButton>
        <BaseButton variant="primary" :loading="isSaving" @click="handleSave">
          保存清单与提示词
        </BaseButton>
      </div>
    </template>
  </BaseDialog>
</template>

<style scoped>
.form-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-error-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}
.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.field-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
}
.req { color: #dc2626; }
.field-input, .field-select {
  height: 34px;
  padding: 0 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #111827;
  outline: none;
  background: #ffffff;
}
.field-input:focus, .field-select:focus, .field-textarea:focus {
  border-color: var(--brand-primary);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}
.field-textarea {
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #111827;
  outline: none;
  resize: vertical;
  line-height: 1.5;
  background: #ffffff;
}

/* Prompt Box Styling */
.prompt-custom-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.prompt-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.prompt-head-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.prompt-ic {
  color: #6366f1;
}
.bold-label {
  color: #1e293b;
  font-weight: 700;
}
.generate-prompt-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  color: #4f46e5;
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.generate-prompt-btn:hover {
  background: #e0e7ff;
}
.code-font {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12.5px;
  background: #ffffff;
}
.prompt-var-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.var-hint {
  font-size: 11px;
  color: #64748b;
}
.var-tag {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #0f172a;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  cursor: pointer;
}
.var-tag:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.form-field-switch {
  margin-top: 4px;
}
.switch-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: #4b5563;
  cursor: pointer;
}
.switch-inp {
  width: 15px;
  height: 15px;
  accent-color: var(--brand-primary);
  cursor: pointer;
}
.dialog-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
