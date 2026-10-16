<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/shared/http/client';
import BaseButton from '@/shared/ui/BaseButton.vue';
import BasePagination from '@/shared/ui/BasePagination.vue';
import CategoryEditModal from './CategoryEditModal.vue';
import { Plus, Search, Edit3, Trash2, FolderTree } from 'lucide-vue-next';

interface CategoryItem {
  id: string;
  name: string;
  code: string;
  description?: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

const items = ref<CategoryItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(8);
const searchQuery = ref('');
const loading = ref(false);

const showEditDialog = ref(false);
const isEditing = ref(false);
const editingCategory = ref<CategoryItem | null>(null);
const formError = ref('');
const isSaving = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    const res: any = await api.get('/categories', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: searchQuery.value.trim() || undefined
      }
    });
    items.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const openCreate = () => {
  isEditing.value = false;
  editingCategory.value = null;
  formError.value = '';
  showEditDialog.value = true;
};

const openEdit = (cat: CategoryItem) => {
  isEditing.value = true;
  editingCategory.value = cat;
  formError.value = '';
  showEditDialog.value = true;
};

const handleSaveCategory = async (payload: { name: string; code: string; description: string; sort_order: number }) => {
  if (!payload.name || !payload.code) {
    formError.value = '请填写分类名称和编码';
    return;
  }
  isSaving.value = true;
  formError.value = '';
  try {
    if (isEditing.value && editingCategory.value) {
      await api.put(`/categories/${editingCategory.value.id}`, payload);
    } else {
      await api.post('/categories', payload);
    }
    showEditDialog.value = false;
    await loadData();
  } catch (err: any) {
    formError.value = err?.response?.data?.detail || '保存失败，请检查输入';
  } finally {
    isSaving.value = false;
  }
};

const deleteCategory = async (cat: CategoryItem) => {
  if (!confirm(`确认删除业务分类【${cat.name}】吗？`)) return;
  try {
    await api.delete(`/categories/${cat.id}`);
    await loadData();
  } catch (err: any) {
    alert(err?.response?.data?.detail || '删除失败');
  }
};

onMounted(loadData);
</script>

<template>
  <div class="management-container">
    <div class="top-action-bar">
      <div class="title-col">
        <h2 class="view-title">合同业务分类维护</h2>
        <span class="view-sub">为审查清单提供层级分类与专项归集标准</span>
      </div>

      <div class="right-tools">
        <div class="search-box">
          <Search :size="14" class="search-ic" />
          <input
            v-model="searchQuery"
            type="text"
            class="search-inp"
            placeholder="搜索分类名称或编码..."
            @keyup.enter="page = 1; loadData()"
          />
        </div>
        <BaseButton variant="primary" @click="openCreate">
          <Plus :size="14" /> 新增业务分类
        </BaseButton>
      </div>
    </div>

    <!-- Table Container -->
    <div class="table-card glass-panel">
      <table class="data-table">
        <thead>
          <tr>
            <th width="180">业务分类名称</th>
            <th width="120">分类编码</th>
            <th>分类说明与适用范围</th>
            <th width="80">排序号</th>
            <th width="160">更新时间</th>
            <th width="120" class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="center-loading">正在读取分类数据...</td>
          </tr>
          <tr v-else-if="items.length === 0">
            <td colspan="6" class="center-empty">
              <FolderTree :size="32" class="empty-ic" />
              <span>暂无业务分类记录，可点击右上角新增</span>
            </td>
          </tr>
          <tr v-for="cat in items" :key="cat.id" class="table-row">
            <td class="cat-name-cell"><span class="name-text">{{ cat.name }}</span></td>
            <td><span class="code-badge">{{ cat.code }}</span></td>
            <td class="desc-cell">{{ cat.description || '-' }}</td>
            <td>{{ cat.sort_order }}</td>
            <td class="time-cell">{{ cat.updated_at.split('T')[0] }}</td>
            <td class="col-actions">
              <button class="tbl-action-btn edit" @click="openEdit(cat)"><Edit3 :size="13" /> 编辑</button>
              <button class="tbl-action-btn del" @click="deleteCategory(cat)"><Trash2 :size="13" /> 删除</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <BasePagination
        :total="total"
        :page="page"
        :page-size="pageSize"
        @update:page="page = $event; loadData()"
      />
    </div>

    <!-- Edit/Create Modal Component -->
    <CategoryEditModal
      v-model="showEditDialog"
      :is-editing="isEditing"
      :initial-data="editingCategory"
      :loading="isSaving"
      :error="formError"
      @save="handleSaveCategory"
    />
  </div>
</template>

<style scoped>
.management-container { padding: 24px 36px; max-width: 1320px; margin: 0 auto; width: 100%; }
.top-action-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.view-title { font-size: 16px; font-weight: 700; color: #0f172a; }
.view-sub { font-size: 12px; color: #64748b; margin-top: 2px; }

.right-tools { display: flex; align-items: center; gap: 12px; }
.search-box { position: relative; display: flex; align-items: center; }
.search-ic { position: absolute; left: 10px; color: #94a3b8; }
.search-inp {
  padding: 6px 14px 6px 32px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 12.5px;
  color: #0f172a;
  outline: none;
  width: 220px;
}
.search-inp:focus { border-color: var(--brand-primary); }

.table-card { background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
.data-table th { background: #f8fafc; padding: 10px 14px; color: #475569; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.table-row:hover { background: #f8fafc; }

.name-text { font-weight: 600; color: #0f172a; }
.code-badge { font-family: var(--font-mono); font-size: 11px; background: #eff6ff; color: var(--brand-primary); padding: 2px 6px; border-radius: 4px; }
.desc-cell { color: #64748b; font-size: 12px; }
.time-cell { color: #94a3b8; font-size: 12px; }

.col-actions { text-align: right; }
.tbl-action-btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: none; border: none; font-size: 12px; cursor: pointer; border-radius: 4px; }
.tbl-action-btn.edit { color: var(--brand-primary); }
.tbl-action-btn.edit:hover { background: #eff6ff; }
.tbl-action-btn.del { color: #dc2626; margin-left: 6px; }
.tbl-action-btn.del:hover { background: #fef2f2; }

.center-loading, .center-empty { text-align: center; padding: 40px; color: #94a3b8; }
.center-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; }
</style>
