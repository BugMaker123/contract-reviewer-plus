<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  FileText,
  FileEdit,
  Play,
  AlertCircle
} from 'lucide-vue-next';
import UploadDropzoneCard from './UploadDropzoneCard.vue';
import ChecklistSelectorCard from './ChecklistSelectorCard.vue';
import AppLogo from '@/shared/ui/AppLogo.vue';

export interface StartReviewPayload {
  file: File | null;
  mode: string;
  referenceNotes: string;
  categoryId?: string;
  categoryName?: string;
  checklistIds?: string[];
}

const emit = defineEmits<{
  (e: 'start-review', payload: StartReviewPayload): void;
  (e: 'load-sample', payload?: Partial<StartReviewPayload>): void;
}>();

const mainTab = ref<'review' | 'draft'>('review');
const selectedMode = ref<'fast' | 'deep' | 'checklist' | 'compare'>('deep');
const showRefInput = ref(false);
const referenceNotes = ref('');
const selectedFile = ref<File | null>(null);

// Category & Checklist Selection - default open for mandatory checklist configuration
const selectedCategoryId = ref('');
const selectedCategoryName = ref('');
const selectedChecklistIds = ref<string[]>([]);
const showChecklistSelector = ref(true);

// Validation Computed
const hasFile = computed(() => !!selectedFile.value);
const hasChecklists = computed(() => selectedChecklistIds.value.length > 0);
const canStartReview = computed(() => hasFile.value && hasChecklists.value);

const startReview = () => {
  if (!selectedFile.value) {
    alert('请先上传待审查的合同 Word (.docx) 文档');
    return;
  }
  if (selectedChecklistIds.value.length === 0) {
    alert('请选择适用的业务分类并至少勾选 1 项审查清单标准');
    return;
  }

  emit('start-review', {
    file: selectedFile.value,
    mode: selectedMode.value,
    referenceNotes: referenceNotes.value,
    categoryId: selectedCategoryId.value || undefined,
    categoryName: selectedCategoryName.value || undefined,
    checklistIds: selectedChecklistIds.value
  });
};
</script>

<template>
  <div class="launcher-container">
    <!-- Center Brand Zone -->
    <div class="brand-hero">
      <AppLogo :size="46" class="hero-logo-box" />
      <h1 class="hero-heading">企业合同智能审查系统</h1>
      <p class="hero-subtext">法务合规研判 · Word (DOCX) 原生修订与条款复核</p>
    </div>

    <!-- Mode Selector Tabs -->
    <div class="tab-pill-group">
      <button
        class="tab-pill-btn"
        :class="{ active: mainTab === 'review' }"
        @click="mainTab = 'review'"
      >
        <FileText :size="14" />
        <span>合同审查</span>
      </button>
      <button
        class="tab-pill-btn"
        :class="{ active: mainTab === 'draft' }"
        @click="mainTab = 'draft'"
      >
        <FileEdit :size="14" />
        <span>合同起草</span>
      </button>
    </div>

    <!-- Step 1: Dropzone Upload Card Component -->
    <div class="step-section">
      <div class="step-header">
        <span class="step-number">1</span>
        <span class="step-title">上传待审查合同文档</span>
        <span v-if="selectedFile" class="step-badge success">已选: {{ selectedFile.name }}</span>
        <span v-else class="step-badge required">必传 (.docx)</span>
      </div>
      <UploadDropzoneCard
        v-model:selected-file="selectedFile"
        v-model:mode="selectedMode"
        :has-reference="referenceNotes.trim().length > 0"
        @toggle-reference="showRefInput = !showRefInput"
      />
    </div>

    <!-- Reference Notes Collapse Drawer -->
    <div v-if="showRefInput" class="ref-input-box animate-fade-in">
      <label class="ref-label">商务立场或对照要求（可选）：</label>
      <input
        v-model="referenceNotes"
        type="text"
        class="ref-text-input"
        placeholder="例如：我方为受托方，重点控制逾期违约责任上限与知识产权归属..."
      />
    </div>

    <!-- Step 2: Business Category & Checklist Selection Card (Mandatory) -->
    <div class="step-section">
      <div class="step-header">
        <span class="step-number">2</span>
        <span class="step-title">配置业务分类与审查清单标准</span>
        <span v-if="selectedChecklistIds.length > 0" class="step-badge success">
          已勾选 {{ selectedChecklistIds.length }} 项审查要点
        </span>
        <span v-else class="step-badge required">至少勾选 1 项</span>
      </div>
      <ChecklistSelectorCard
        v-model:selected-category-id="selectedCategoryId"
        v-model:selected-checklist-ids="selectedChecklistIds"
        @update:category-name="selectedCategoryName = $event"
        @close="showChecklistSelector = true"
      />
    </div>

    <!-- Main CTA Button & Condition Hints -->
    <div class="action-cta-area">
      <!-- Validation Guide Hints -->
      <div v-if="!canStartReview" class="start-hint-banner">
        <AlertCircle :size="14" class="hint-icon" />
        <span v-if="!hasFile && !hasChecklists">
          请上传合同文档 (.docx) 并勾选审查清单标准后进入工作台
        </span>
        <span v-else-if="!hasFile">
          请拖拽或选择上传待审查的 Word (.docx) 合同文档
        </span>
        <span v-else-if="!hasChecklists">
          合同文档已就绪，请勾选至少一项审查清单标准
        </span>
      </div>

      <!-- Action Button -->
      <button
        class="primary-start-btn"
        :class="{ 'btn-disabled': !canStartReview }"
        :disabled="!canStartReview"
        @click="startReview"
      >
        <Play :size="16" />
        <span v-if="!hasFile">请先上传合同文档</span>
        <span v-else-if="!hasChecklists">请选择审查清单</span>
        <span v-else>进入工作台并开启审查 (已选 {{ selectedChecklistIds.length }} 项清单)</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.launcher-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px 48px;
  width: 100%;
  max-width: 820px;
  margin: 0 auto;
}

.brand-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}
.hero-heading { font-size: 20px; font-weight: 800; color: #111827; letter-spacing: 0.5px; }
.hero-subtext { font-size: 13.5px; color: #4b5563; margin-top: 4px; }

.tab-pill-group {
  display: flex;
  background: #f1f5f9;
  padding: 3px;
  border-radius: 8px;
  gap: 4px;
  margin-bottom: 20px;
}
.tab-pill-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 18px;
  border: none;
  border-radius: 6px;
  background: transparent;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s ease;
}
.tab-pill-btn.active {
  background: #ffffff;
  color: #111827;
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.step-section {
  width: 100%;
  margin-bottom: 18px;
}
.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.step-number {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--brand-primary, #2563eb);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.step-title {
  font-size: 13.5px;
  font-weight: 600;
  color: #1e293b;
}
.step-badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 12px;
  margin-left: auto;
}
.step-badge.required {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
}
.step-badge.success {
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  font-weight: 600;
}

.ref-input-box {
  width: 100%;
  margin-top: -6px;
  margin-bottom: 14px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 10px 14px;
}
.ref-label { font-size: 11.5px; color: #6b7280; display: block; margin-bottom: 4px; }
.ref-text-input { width: 100%; border: none; outline: none; font-size: 12.5px; color: #1f2937; }

.action-cta-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  width: 100%;
}

.start-hint-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12.5px;
}
.hint-icon {
  flex-shrink: 0;
  color: #d97706;
}

.primary-start-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 42px;
  background: var(--brand-primary, #2563eb);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.28);
  min-width: 260px;
}
.primary-start-btn:hover:not(.btn-disabled) {
  background: var(--brand-hover, #1d4ed8);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}
.primary-start-btn.btn-disabled {
  background: #94a3b8;
  color: #f1f5f9;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.7;
}
</style>
