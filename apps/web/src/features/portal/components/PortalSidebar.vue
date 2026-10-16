<script setup lang="ts">
import {
  Home,
  FileCheck2,
  ListTodo,
  FolderTree,
  FilePenLine
} from 'lucide-vue-next';
import AppLogo from '@/shared/ui/AppLogo.vue';

defineProps<{
  activeTab: 'start' | 'records' | 'categories' | 'checklists' | 'draft';
  recordsCount: number;
}>();

const emit = defineEmits<{
  (e: 'navigate', tab: 'start' | 'records' | 'categories' | 'checklists' | 'draft'): void;
}>();
</script>

<template>
  <aside class="portal-sidebar">
    <!-- Brand Header -->
    <div class="sidebar-brand-zone" @click="emit('navigate', 'start')">
      <AppLogo :size="28" />
      <div class="brand-text-col">
        <div class="brand-title-row">
          <span class="brand-name">合同审查系统</span>
        </div>
        <span class="brand-desc">企业合规管理平台</span>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <!-- Home Action -->
      <button
        class="nav-item-btn main-start"
        :class="{ active: activeTab === 'start' }"
        @click="emit('navigate', 'start')"
      >
        <Home :size="16" />
        <span>开始审查</span>
      </button>

      <!-- Review Section -->
      <div class="nav-section-group">
        <span class="section-label">
          分割线
        </span>
        <button
          class="nav-item-btn"
          :class="{ active: activeTab === 'records' }"
          @click="emit('navigate', 'records')"
        >
          <FileCheck2 :size="15" />
          <span>审查记录</span>
          <span v-if="recordsCount > 0" class="badge-count">{{ recordsCount }}</span>
        </button>
        <button
          class="nav-item-btn"
          :class="{ active: activeTab === 'categories' }"
          @click="emit('navigate', 'categories')"
        >
          <FolderTree :size="15" />
          <span>业务分类维护</span>
        </button>
        <button
          class="nav-item-btn"
          :class="{ active: activeTab === 'checklists' }"
          @click="emit('navigate', 'checklists')"
        >
          <ListTodo :size="15" />
          <span>审查清单维护</span>
        </button>
      </div>

      <!-- Drafting Section -->
      <div class="nav-section-group">
        <span class="section-label">合同起草</span>
        <button
          class="nav-item-btn"
          :class="{ active: activeTab === 'draft' }"
          @click="emit('navigate', 'draft')"
        >
          <FilePenLine :size="15" />
          <span>起草记录</span>
        </button>
      </div>
    </nav>

    <!-- Bottom Internal Department Footer -->
    <div class="sidebar-footer">
      <div class="internal-dept-card">
        <div class="dept-dot"></div>
        <div class="dept-info">
          <span class="dept-name">法律合规部</span>
          <span class="dept-env">企业内网专用版</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.portal-sidebar {
  width: 200px;
  min-width: 200px;
  background: #ffffff;
  border-right: 1px solid #eef2f6;
  display: flex;
  flex-direction: column;
  height: 100vh;
  user-select: none;
}

.sidebar-brand-zone {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 14px;
  cursor: pointer;
}
.brand-logo-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--markup-green);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}
.logo-svg {
  width: 16px;
  height: 16px;
}
.brand-text-col {
  display: flex;
  flex-direction: column;
}
.brand-title-row {
  display: flex;
  align-items: center;
}
.brand-name {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #111827;
}
.brand-desc {
  font-size: 10px;
  color: #94a3b8;
}

.sidebar-nav {
  flex: 1;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.nav-item-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: left;
}
.nav-item-btn:hover {
  background: #f3f4f6;
  color: #111827;
}
.nav-item-btn.active {
  background: #eff6ff;
  color: var(--brand-primary);
  font-weight: 600;
}

.nav-item-btn.main-start {
  background: #f8fafc;
  color: #1e293b;
  font-weight: 600;
}
.nav-item-btn.main-start.active {
  background: #eff6ff;
  color: var(--brand-primary);
}

.badge-count {
  margin-left: auto;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #475569;
}
.nav-item-btn.active .badge-count {
  background: #dbeafe;
  color: var(--brand-primary);
}

.nav-section-group {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.section-label {
  font-size: 11px;
  color: #9ca3af;
  padding: 4px 12px;
  font-weight: 500;
}

.sidebar-footer {
  padding: 12px 14px 16px;
  border-top: 1px solid #f1f5f9;
}
.internal-dept-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}
.dept-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--brand-primary);
}
.dept-info {
  display: flex;
  flex-direction: column;
}
.dept-name {
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
}
.dept-env {
  font-size: 10px;
  color: #94a3b8;
}
</style>
