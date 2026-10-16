<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';
import api from '@/shared/http/client';
import BaseBadge from '@/shared/ui/BaseBadge.vue';
import { CheckSquare, Square, FolderCheck, X, AlertCircle } from 'lucide-vue-next';

interface CategoryOption { id: string; name: string; }
interface ChecklistItem {
  id: string;
  category_id: string;
  title: string;
  risk_level: 'high' | 'medium' | 'low';
  standard_clause?: string;
  check_prompt?: string;
  is_enabled: boolean;
}

const props = defineProps<{
  selectedCategoryId: string;
  selectedChecklistIds: string[];
}>();

const emit = defineEmits<{
  (e: 'update:selectedCategoryId', id: string): void;
  (e: 'update:selectedChecklistIds', ids: string[]): void;
  (e: 'update:categoryName', name: string): void;
  (e: 'close'): void;
}>();

const categories = ref<CategoryOption[]>([]);
const checklistItems = ref<ChecklistItem[]>([]);
const loading = ref(false);

const loadCategories = async () => {
  try {
    const res: any = await api.get('/categories/all');
    categories.value = res.items || [];
    if (!props.selectedCategoryId && categories.value.length > 0) {
      const firstCat = categories.value[0];
      emit('update:selectedCategoryId', firstCat.id);
      emit('update:categoryName', firstCat.name);
      await loadChecklists(firstCat.id);
    }
  } catch (e) { /* ignore */ }
};

const loadChecklists = async (catId: string) => {
  if (!catId) return;
  loading.value = true;
  try {
    const res: any = await api.get('/checklists', { params: { category_id: catId, page_size: 50 } });
    const items: ChecklistItem[] = (res.items || []).filter((i: ChecklistItem) => i.is_enabled);
    checklistItems.value = items;
    if (props.selectedChecklistIds.length === 0 && items.length > 0) {
      emit('update:selectedChecklistIds', items.map(i => i.id));
    }
  } finally {
    loading.value = false;
  }
};

const handleCategoryChange = async (e: Event) => {
  const catId = (e.target as HTMLSelectElement).value;
  emit('update:selectedCategoryId', catId);
  const found = categories.value.find(c => c.id === catId);
  if (found) emit('update:categoryName', found.name);
  await loadChecklists(catId);
  if (checklistItems.value.length > 0) {
    emit('update:selectedChecklistIds', checklistItems.value.map(i => i.id));
  }
};

const isAllSelected = computed(() => {
  if (checklistItems.value.length === 0) return false;
  return checklistItems.value.every(item => props.selectedChecklistIds.includes(item.id));
});

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    emit('update:selectedChecklistIds', []);
  } else {
    emit('update:selectedChecklistIds', checklistItems.value.map(i => i.id));
  }
};

const toggleItem = (id: string) => {
  const next = [...props.selectedChecklistIds];
  const idx = next.indexOf(id);
  if (idx >= 0) next.splice(idx, 1);
  else next.push(id);
  emit('update:selectedChecklistIds', next);
};

watch(() => props.selectedCategoryId, (newId) => {
  if (newId) loadChecklists(newId);
});

onMounted(async () => {
  await loadCategories();
  if (props.selectedCategoryId) await loadChecklists(props.selectedCategoryId);
});
</script>

<template>
  <div class="checklist-selector-card animate-fade-in">
    <div class="card-header-bar">
      <div class="left-head">
        <FolderCheck :size="16" class="header-icon" />
        <span class="header-title">专项清单审查标准配置</span>
        <span class="header-badge">已勾选 {{ selectedChecklistIds.length }} 项要点</span>
      </div>
      <button class="close-card-btn" @click="emit('close')"><X :size="15" /></button>
    </div>

    <!-- Category Selector Controls -->
    <div class="category-select-row">
      <label class="control-label">选择业务分类：</label>
      <select :value="selectedCategoryId" class="category-dropdown" @change="handleCategoryChange">
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <div class="actions-right">
        <button class="batch-action-link" @click="toggleSelectAll">
          <component :is="isAllSelected ? CheckSquare : Square" :size="13" />
          <span>{{ isAllSelected ? '取消全选' : '全部勾选' }}</span>
        </button>
      </div>
    </div>

    <!-- Checklist Items Grid -->
    <div class="checklist-grid-container">
      <div v-if="loading" class="empty-hint">正在加载清单要点...</div>
      <div v-else-if="checklistItems.length === 0" class="empty-hint">
        <AlertCircle :size="14" /> 该分类下暂无可用的审查清单，可在左侧「审查清单维护」添加
      </div>
      <div
        v-for="item in checklistItems"
        v-else
        :key="item.id"
        class="checklist-item-tile"
        :class="{ checked: selectedChecklistIds.includes(item.id) }"
        @click="toggleItem(item.id)"
      >
        <div class="tile-checkbox">
          <component :is="selectedChecklistIds.includes(item.id) ? CheckSquare : Square" :size="15" />
        </div>
        <div class="tile-info">
          <div class="tile-title-row">
            <span class="tile-title">{{ item.title }}</span>
            <BaseBadge :variant="item.risk_level" size="sm">
              {{ item.risk_level === 'high' ? '高风险' : item.risk_level === 'medium' ? '中风险' : '低风险' }}
            </BaseBadge>
          </div>
          <p v-if="item.standard_clause || item.check_prompt" class="tile-guideline">
            {{ item.standard_clause || item.check_prompt }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checklist-selector-card {
  width: 100%;
  background: #ffffff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 14px;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.06);
}
.card-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
}
.left-head { display: flex; align-items: center; gap: 8px; }
.header-icon { color: var(--brand-primary); }
.header-title { font-size: 13.5px; font-weight: 700; color: #0f172a; }
.header-badge { background: #eff6ff; color: var(--brand-primary); font-size: 11.5px; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
.close-card-btn { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 2px; }
.close-card-btn:hover { color: #475569; }

.category-select-row { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
.control-label { font-size: 12.5px; font-weight: 600; color: #334155; white-space: nowrap; }
.category-dropdown {
  flex: 1;
  max-width: 320px;
  padding: 5px 10px;
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 12px;
  color: #0f172a;
  outline: none;
}
.category-dropdown:focus { border-color: var(--brand-primary); background: #fff; }
.actions-right { margin-left: auto; }
.batch-action-link {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 12px;
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 500;
}

.checklist-grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
}
.checklist-item-tile {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.checklist-item-tile:hover { border-color: #93c5fd; background: #eff6ff; }
.checklist-item-tile.checked { background: #f0f7ff; border-color: #3b82f6; }
.tile-checkbox { color: #94a3b8; margin-top: 2px; }
.checklist-item-tile.checked .tile-checkbox { color: var(--brand-primary); }
.tile-info { flex: 1; min-width: 0; }
.tile-title-row { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.tile-title { font-size: 12px; font-weight: 600; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tile-guideline {
  font-size: 11px;
  color: #64748b;
  margin-top: 3px;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-hint {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
</style>
