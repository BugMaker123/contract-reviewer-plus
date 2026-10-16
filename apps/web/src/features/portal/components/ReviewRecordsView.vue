<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/shared/http/client';
import type { Contract } from '@/shared/types';
import BaseButton from '@/shared/ui/BaseButton.vue';
import BasePagination from '@/shared/ui/BasePagination.vue';
import { Search, ExternalLink, Trash2, FileText, Play, RotateCw } from 'lucide-vue-next';

const router = useRouter();

const emit = defineEmits<{
  (e: 'load-sample'): void;
}>();

const contracts = ref<Contract[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(8);
const searchQuery = ref('');
const loading = ref(false);

const loadData = async () => {
  loading.value = true;
  try {
    const res: any = await api.get('/contracts', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: searchQuery.value.trim() || undefined
      }
    });
    contracts.value = res.contracts || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
};

const deleteRecord = async (c: Contract) => {
  if (!confirm(`确定删除合同审查任务【${c.title}】及其相关版本快照吗？`)) return;
  try {
    await api.delete(`/contracts/${c.id}`);
    await loadData();
  } catch (err: any) {
    alert(err?.response?.data?.detail || '删除失败');
  }
};

const viewDetail = (c: Contract) => {
  router.push(`/workbench/${c.id}`);
};

onMounted(loadData);
</script>

<template>
  <div class="records-container">
    <div class="top-action-bar">
      <div class="title-col">
        <h2 class="view-title">合同审查记录台账</h2>
        <span class="view-sub">全生命周期法务审查任务、DOCX 原生修订痕迹与履约版本交付档案</span>
      </div>

      <div class="right-tools">
        <div class="search-box">
          <Search :size="14" class="search-ic" />
          <input
            v-model="searchQuery"
            type="text"
            class="search-inp"
            placeholder="搜索合同名称或商务立场..."
            @keyup.enter="page = 1; loadData()"
          />
        </div>
        <button class="icon-refresh-btn" title="刷新列表" @click="loadData">
          <RotateCw :size="14" />
        </button>
        <BaseButton variant="secondary" size="md" @click="emit('load-sample')">
          <Play :size="13" /> 载入示例合同
        </BaseButton>
      </div>
    </div>

    <!-- Table Card -->
    <div class="table-card glass-panel">
      <table class="data-table">
        <thead>
          <tr>
            <th>合同名称与编号</th>
            <th width="160">绑定业务分类/清单</th>
            <th width="130">我方商务立场</th>
            <th width="100">复核状态</th>
            <th width="110">当前工作版本</th>
            <th width="140">更新时间</th>
            <th width="150" class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="center-loading">正在读取合同审查记录...</td>
          </tr>
          <tr v-else-if="contracts.length === 0">
            <td colspan="7" class="center-empty">
              <FileText :size="36" class="empty-ic" />
              <span>暂无合同审查记录，您可以从上方载入示例合同或去首页上传文档</span>
            </td>
          </tr>
          <tr v-for="c in contracts" :key="c.id" class="table-row">
            <td class="contract-title-cell">
              <div class="title-wrap">
                <span class="title-text" @click="viewDetail(c)">{{ c.title }}</span>
                <span class="id-sub">ID: {{ c.id }}</span>
              </div>
            </td>
            <td>
              <div class="cat-pill-wrap">
                <span class="cat-name-tag">{{ (c as any).category_name || '通用审查' }}</span>
                <span v-if="(c as any).checklist_ids?.length" class="checklist-count-tag">
                  {{ (c as any).checklist_ids.length }} 项清单
                </span>
              </div>
            </td>
            <td>
              <span class="stance-badge">{{ c.stance }}</span>
            </td>
            <td>
              <span :class="['status-chip', c.review_status]">
                {{ c.review_status === 'verified' ? '已确认归档' : '待法务复核' }}
              </span>
            </td>
            <td>
              <span class="version-tag">{{ c.head_version_id || '-' }}</span>
            </td>
            <td class="time-cell">{{ c.updated_at.split('T')[0] }}</td>
            <td class="col-actions">
              <button class="tbl-action-btn view" @click="viewDetail(c)">
                <ExternalLink :size="13" /> 查看详情
              </button>
              <button class="tbl-action-btn del" @click="deleteRecord(c)">
                <Trash2 :size="13" /> 删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination Component -->
      <BasePagination
        :total="total"
        :page="page"
        :page-size="pageSize"
        @update:page="page = $event; loadData()"
      />
    </div>
  </div>
</template>

<style scoped>
.records-container { padding: 24px 36px; max-width: 1320px; margin: 0 auto; width: 100%; }
.top-action-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.view-title { font-size: 16px; font-weight: 700; color: #0f172a; }
.view-sub { font-size: 12px; color: #64748b; margin-top: 2px; }

.right-tools { display: flex; align-items: center; gap: 10px; }
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

.icon-refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}
.icon-refresh-btn:hover { border-color: var(--brand-primary); color: var(--brand-primary); }

.table-card { background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
.data-table th { background: #f8fafc; padding: 10px 14px; color: #475569; font-weight: 600; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.table-row:hover { background: #f8fafc; }

.contract-title-cell .title-wrap { display: flex; flex-direction: column; gap: 2px; }
.title-text { font-weight: 600; color: #0f172a; cursor: pointer; transition: color 0.15s; }
.title-text:hover { color: var(--brand-primary); }
.id-sub { font-size: 10.5px; color: #94a3b8; font-family: var(--font-mono); }

.cat-pill-wrap { display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.cat-name-tag { font-size: 11.5px; background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 4px; font-weight: 500; }
.checklist-count-tag { font-size: 10.5px; background: #f1f5f9; color: #475569; padding: 1px 6px; border-radius: 3px; }

.stance-badge { font-size: 11.5px; background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 4px; }
.status-chip { font-size: 11px; padding: 2px 7px; border-radius: 4px; font-weight: 500; }
.status-chip.verified { background: #dcfce7; color: #15803d; }
.status-chip.draft { background: #eff6ff; color: var(--brand-primary); }

.version-tag { font-family: var(--font-mono); font-size: 11px; color: #64748b; }
.time-cell { font-size: 12px; color: #94a3b8; }

.col-actions { text-align: right; white-space: nowrap; }
.tbl-action-btn { display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; background: none; border: none; font-size: 12px; cursor: pointer; border-radius: 4px; }
.tbl-action-btn.view { color: var(--brand-primary); font-weight: 500; }
.tbl-action-btn.view:hover { background: #eff6ff; }
.tbl-action-btn.del { color: #dc2626; margin-left: 6px; }
.tbl-action-btn.del:hover { background: #fef2f2; }

.center-loading, .center-empty { text-align: center; padding: 40px; color: #94a3b8; }
.center-empty { display: flex; flex-direction: column; align-items: center; gap: 8px; }
</style>
