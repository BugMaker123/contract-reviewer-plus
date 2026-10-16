<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '@/shared/http/client';
import BaseButton from '@/shared/ui/BaseButton.vue';
import BasePagination from '@/shared/ui/BasePagination.vue';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import ChecklistEditModal, { type ChecklistItemData, type CategoryOption } from './ChecklistEditModal.vue';
import { Plus, Search, Edit3, Trash2, ListTodo, Filter } from 'lucide-vue-next';

interface ChecklistItem extends ChecklistItemData {
  id: string;
  category_name?: string;
  updated_at: string;
}

const items = ref<ChecklistItem[]>([]);
const categories = ref<CategoryOption[]>([]);
const selectedCatFilter = ref('');
const total = ref(0);
const page = ref(1);
const pageSize = ref(8);
const searchQuery = ref('');
const loading = ref(false);

const showModal = ref(false);
const editingItem = ref<ChecklistItem | null>(null);

const loadCategories = async () => {
  try {
    const res: any = await api.get('/categories/all');
    categories.value = res.items || [];
  } catch (e) {
    // ignore
  }
};

const loadData = async () => {
  loading.value = true;
  try {
    const res: any = await api.get('/checklists', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        category_id: selectedCatFilter.value || undefined,
        keyword: searchQuery.value.trim() || undefined
      }
    });
    items.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const openCreate = async () => {
  await loadCategories();
  editingItem.value = null;
  showModal.value = true;
};

const openEdit = async (chk: ChecklistItem) => {
  await loadCategories();
  editingItem.value = chk;
  showModal.value = true;
};

const deleteChecklist = async (chk: ChecklistItem) => {
  if (!confirm(`确认删除审查清单要点【${chk.title}】吗？`)) return;
  try {
    await api.delete(`/checklists/${chk.id}`);
    await loadData();
  } catch (err: any) {
    alert(err?.response?.data?.detail || '删除失败');
  }
};

onMounted(() => {
  loadCategories();
  loadData();
});
</script>

<template>
  <div class="management-container">
    <div class="top-action-bar">
      <div class="title-col">
        <h2 class="view-title">合同审查清单维护</h2>
        <span class="view-sub">绑定业务分类的条款合规核验标准，驱动审查引擎逐项研判</span>
      </div>

      <div class="right-tools">
        <div class="filter-box">
          <Filter :size="13" class="filter-ic" />
          <select
            v-model="selectedCatFilter"
            class="cat-filter-select"
            @change="page = 1; loadData()"
          >
            <option value="">全部业务分类</option>
            <option v-for="c in categories" :key="c.id" :value="c.id">
              {{ c.name }}
            </option>
          </select>
        </div>

        <div class="search-box">
          <Search :size="14" class="search-ic" />
          <input
            v-model="searchQuery"
            type="text"
            class="search-inp"
            placeholder="搜索要点标题或条款内容..."
            @keyup.enter="page = 1; loadData()"
          />
        </div>
        <BaseButton variant="primary" @click="openCreate">
          <Plus :size="14" /> 新增审查清单
        </BaseButton>
      </div>
    </div>

    <!-- Table Card -->
    <div class="table-card glass-panel">
      <table class="data-table">
        <thead>
          <tr>
            <th width="200">审查要点</th>
            <th width="150">绑定业务分类</th>
            <th width="90">风险等级</th>
            <th>标准合规参考条款与审查指引</th>
            <th width="70">状态</th>
            <th width="120" class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="center-loading">正在读取审查清单数据...</td>
          </tr>
          <tr v-else-if="items.length === 0">
            <td colspan="6" class="center-empty">
              <ListTodo :size="32" class="empty-ic" />
              <span>暂无匹配的审查清单项目，可点击右上角新增</span>
            </td>
          </tr>
          <tr v-for="chk in items" :key="chk.id" class="table-row">
            <td class="chk-title-cell">
              <span class="title-text">{{ chk.title }}</span>
            </td>
            <td>
              <span class="cat-tag">{{ chk.category_name || '未分类' }}</span>
            </td>
            <td>
              <BaseBadge :variant="chk.risk_level" size="sm">
                {{ chk.risk_level === 'high' ? '高风险' : chk.risk_level === 'medium' ? '中风险' : '低风险' }}
              </BaseBadge>
            </td>
            <td class="guideline-cell">
              <div v-if="chk.standard_clause" class="clause-text">
                <span class="lbl">参考条款：</span>{{ chk.standard_clause }}
              </div>
              <div v-if="chk.check_prompt" class="prompt-text">
                <span class="lbl">复核指引：</span>{{ chk.check_prompt }}
              </div>
              <div v-if="chk.prompt_template" class="custom-prompt-row">
                <span class="prompt-badge">AI 审查 Prompt</span>
                <span class="prompt-preview" :title="chk.prompt_template">{{ chk.prompt_template }}</span>
              </div>
            </td>
            <td>
              <span :class="['status-chip', chk.is_enabled ? 'enabled' : 'disabled']">
                {{ chk.is_enabled ? '启用' : '停用' }}
              </span>
            </td>
            <td class="col-actions">
              <button class="tbl-action-btn edit" @click="openEdit(chk)">
                <Edit3 :size="13" /> 编辑
              </button>
              <button class="tbl-action-btn del" @click="deleteChecklist(chk)">
                <Trash2 :size="13" /> 删除
              </button>
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

    <ChecklistEditModal
      v-model="showModal"
      :item="editingItem"
      :categories="categories"
      :default-category-id="selectedCatFilter"
      :next-sort-order="total + 1"
      @saved="loadData"
    />
  </div>
</template>

<style scoped>
.management-container { padding: 24px 36px; max-width: 1320px; margin: 0 auto; width: 100%; }
.top-action-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.view-title { font-size: 16px; font-weight: 700; color: #0f172a; }
.view-sub { font-size: 12px; color: #64748b; margin-top: 2px; }

.right-tools { display: flex; align-items: center; gap: 10px; }
.filter-box { position: relative; display: flex; align-items: center; }
.filter-ic { position: absolute; left: 8px; color: #64748b; }
.cat-filter-select {
  padding: 6px 10px 6px 26px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 12.5px;
  color: #334155;
  outline: none;
}
.cat-filter-select:focus { border-color: var(--brand-primary); }

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
  width: 200px;
}
.search-inp:focus { border-color: var(--brand-primary); }

.table-card { background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
.data-table th { background: #f8fafc; padding: 10px 14px; color: #475569; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: top; }
.table-row:hover { background: #f8fafc; }

.chk-title-cell .title-text { font-weight: 600; color: #0f172a; }
.cat-tag { background: #eff6ff; color: #1d4ed8; font-size: 11.5px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.guideline-cell { font-size: 12px; display: flex; flex-direction: column; gap: 4px; }
.clause-text { color: #334155; line-height: 1.4; }
.prompt-text { color: #64748b; line-height: 1.4; }
.lbl { font-weight: 600; color: #475569; }

.custom-prompt-row { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.prompt-badge { background: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; font-size: 10.5px; padding: 1px 5px; border-radius: 3px; font-weight: 600; flex-shrink: 0; }
.prompt-preview { font-size: 11.5px; color: #6d28d9; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 380px; }

.status-chip { font-size: 11px; padding: 1px 6px; border-radius: 4px; }
.status-chip.enabled { background: #dcfce7; color: #15803d; }
.status-chip.disabled { background: #f1f5f9; color: #94a3b8; }

.col-actions { text-align: right; white-space: nowrap; }
.tbl-action-btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: none; border: none; font-size: 12px; cursor: pointer; border-radius: 4px; }
.tbl-action-btn.edit { color: var(--brand-primary); }
.tbl-action-btn.edit:hover { background: #eff6ff; }
.tbl-action-btn.del { color: #dc2626; margin-left: 6px; }
.tbl-action-btn.del:hover { background: #fef2f2; }

.center-loading, .center-empty { text-align: center; padding: 40px; color: #94a3b8; }
.center-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; }
</style>
