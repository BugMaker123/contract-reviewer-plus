<script setup lang="ts">
import { ref } from 'vue';
import {
  ChevronDown,
  Zap,
  Search,
  ListTodo,
  GitCompare
} from 'lucide-vue-next';

interface ReviewMode {
  id: 'fast' | 'deep' | 'checklist' | 'compare';
  label: string;
  desc: string;
  icon: any;
}

const props = defineProps<{
  modelValue: 'fast' | 'deep' | 'checklist' | 'compare';
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: 'fast' | 'deep' | 'checklist' | 'compare'): void;
}>();

const showDropdown = ref(false);

const reviewModes: ReviewMode[] = [
  { id: 'fast', label: '快速审查', desc: '基础合规与常见通用风险排查', icon: Zap },
  { id: 'deep', label: '深度审查', desc: '违约赔偿、付款账期、管辖排他全景研判', icon: Search },
  { id: 'checklist', label: '清单审查', desc: '对照法务合规标准清单逐条核验', icon: ListTodo },
  { id: 'compare', label: '对比审查', desc: '基准模板与修订稿双向交叉比对', icon: GitCompare }
];

const getCurrentModeObj = () => reviewModes.find((m) => m.id === props.modelValue) || reviewModes[1];

const selectMode = (mode: 'fast' | 'deep' | 'checklist' | 'compare') => {
  emit('update:modelValue', mode);
  showDropdown.value = false;
};
</script>

<template>
  <div class="mode-dropdown-wrapper">
    <button class="mode-selector-pill" @click="showDropdown = !showDropdown">
      <component :is="getCurrentModeObj().icon" :size="14" class="mode-ic" />
      <span class="mode-name">{{ getCurrentModeObj().label }}</span>
      <ChevronDown :size="14" class="chevron" />
    </button>

    <div v-if="showDropdown" class="mode-dropdown-panel animate-fade-in">
      <div
        v-for="m in reviewModes"
        :key="m.id"
        class="dropdown-row-item"
        :class="{ active: modelValue === m.id }"
        @click="selectMode(m.id)"
      >
        <div class="row-left">
          <component :is="m.icon" :size="14" class="menu-ic" />
          <div class="menu-info-col">
            <span class="menu-label">{{ m.label }}</span>
            <span class="menu-desc">{{ m.desc }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mode-dropdown-wrapper { position: relative; }
.mode-selector-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #ffffff;
  border: 1px solid var(--brand-primary);
  border-radius: 6px;
  color: var(--brand-primary);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}
.chevron { color: var(--brand-primary); }

.mode-dropdown-panel {
  position: absolute;
  top: 36px;
  left: 0;
  width: 270px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  padding: 6px;
  z-index: 50;
}
.dropdown-row-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: #374151;
  transition: all 0.15s ease;
}
.dropdown-row-item:hover, .dropdown-row-item.active {
  background: #eff6ff;
  color: var(--brand-primary);
}
.row-left { display: flex; align-items: flex-start; gap: 10px; }
.menu-ic { margin-top: 2px; }
.menu-info-col { display: flex; flex-direction: column; gap: 2px; }
.menu-label { font-size: 13px; font-weight: 600; color: #1e293b; }
.dropdown-row-item.active .menu-label, .dropdown-row-item:hover .menu-label { color: var(--brand-primary); }
.menu-desc { font-size: 11px; color: #94a3b8; line-height: 1.3; }
</style>
