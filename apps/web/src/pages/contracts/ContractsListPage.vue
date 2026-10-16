<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/shared/http/client';
import PortalSidebar from '@/features/portal/components/PortalSidebar.vue';
import PortalTopNav from '@/features/portal/components/PortalTopNav.vue';
import PortalReviewLauncher from '@/features/portal/components/PortalReviewLauncher.vue';
import ReviewRecordsView from '@/features/portal/components/ReviewRecordsView.vue';
import CategoryManagementView from '@/features/portal/components/CategoryManagementView.vue';
import ChecklistManagementView from '@/features/portal/components/ChecklistManagementView.vue';
import { FileText } from 'lucide-vue-next';

const router = useRouter();
const activeTab = ref<'start' | 'records' | 'categories' | 'checklists' | 'draft'>('start');
const recordsTotal = ref(0);

const fetchRecordsCount = async () => {
  try {
    const res: any = await api.get('/contracts', { params: { page: 1, page_size: 1 } });
    recordsTotal.value = res.total || (res.contracts ? res.contracts.length : 0);
  } catch (e) {
    // ignore
  }
};

const createSampleContract = async (payload?: { categoryId?: string; categoryName?: string; checklistIds?: string[] }) => {
  try {
    const formData = new FormData();
    if (payload?.categoryId) formData.append('category_id', payload.categoryId);
    if (payload?.categoryName) formData.append('category_name', payload.categoryName);
    if (payload?.checklistIds && payload.checklistIds.length > 0) {
      formData.append('checklist_ids', JSON.stringify(payload.checklistIds));
    }
    const res: any = await api.post('/contracts/sample', formData);
    router.push({ path: `/workbench/${res.contract.id}`, query: { autoReview: '1' } });
  } catch (err: any) {
    alert(err?.response?.data?.detail || '载入示例失败');
  }
};

const handleStartReview = async (payload: {
  file: File | null;
  mode: string;
  referenceNotes: string;
  categoryId?: string;
  categoryName?: string;
  checklistIds?: string[];
}) => {
  if (!payload.file) {
    alert('请先上传待审查的 Word (.docx) 合同文档');
    return;
  }
  if (!payload.checklistIds || payload.checklistIds.length === 0) {
    alert('请选择适用的业务分类并至少勾选 1 项审查清单标准');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('title', payload.file.name.replace(/\.[^/.]+$/, ''));
    formData.append('stance', '我方（受托方/通用）');
    if (payload.categoryId) formData.append('category_id', payload.categoryId);
    if (payload.categoryName) formData.append('category_name', payload.categoryName);
    formData.append('checklist_ids', JSON.stringify(payload.checklistIds));

    const res: any = await api.post('/contracts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    router.push({ path: `/workbench/${res.contract.id}`, query: { autoReview: '1' } });
  } catch (err: any) {
    alert(err?.response?.data?.detail || '启动审查失败');
  }
};

onMounted(fetchRecordsCount);
</script>

<template>
  <div class="portal-main-layout">
    <!-- Left Fixed Navigation Sidebar -->
    <PortalSidebar
      :active-tab="activeTab"
      :records-count="recordsTotal"
      @navigate="activeTab = $event"
    />

    <!-- Right Workspace Area -->
    <div class="portal-body-wrapper">
      <PortalTopNav />

      <main class="portal-content-scroll">
        <!-- 1. Start Launcher View -->
        <PortalReviewLauncher
          v-if="activeTab === 'start'"
          @start-review="handleStartReview"
          @load-sample="createSampleContract"
        />

        <!-- 2. Review Records View (with Pagination, Detail & Deletion) -->
        <ReviewRecordsView
          v-else-if="activeTab === 'records'"
          @load-sample="createSampleContract"
        />

        <!-- 3. Business Category Management View (CRUD + Pagination) -->
        <CategoryManagementView
          v-else-if="activeTab === 'categories'"
        />

        <!-- 4. Checklist Standards Management View (CRUD + Category Binding + Pagination) -->
        <ChecklistManagementView
          v-else-if="activeTab === 'checklists'"
        />

        <!-- 5. Drafting Module Placeholder -->
        <div v-else-if="activeTab === 'draft'" class="empty-cards-state draft-placeholder">
          <FileText :size="42" class="empty-icon" />
          <h3 class="empty-title">合同起草与范本库模块</h3>
          <p class="empty-desc">内部合同标准范本起草与条款库组装功能规划中，当前可使用【合同审查】体验审查与修订流水线。</p>
          <button class="primary-blue-btn" @click="activeTab = 'start'">
            返回合同审查
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.portal-main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #f8fafc;
  overflow: hidden;
}

.portal-body-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.portal-content-scroll {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.empty-cards-state {
  text-align: center;
  padding: 80px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  background: #ffffff;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  max-width: 800px;
  margin: 60px auto 0;
}
.empty-icon { color: #94a3b8; }
.empty-title { font-size: 16px; color: #0f172a; font-weight: 600; }
.empty-desc { font-size: 13px; color: #64748b; max-width: 480px; line-height: 1.6; }

.primary-blue-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--brand-primary);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}
.primary-blue-btn:hover {
  background: var(--brand-hover);
}
</style>
