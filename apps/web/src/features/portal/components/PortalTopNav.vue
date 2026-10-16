<script setup lang="ts">
import { User } from 'lucide-vue-next';
</script>

<template>
  <header class="portal-top-nav">
    <div class="nav-left">
      <span class="status-indicator-dot"></span>
      <span class="system-tag">合规审查引擎已就绪 (DOCX 原生修订)</span>
    </div>

    <div class="nav-right">
      <div class="user-account-badge">
        <div class="user-avatar-circle">
          <User :size="14" />
        </div>
        <span class="user-phone">法务复核员 (81342)</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.portal-top-nav {
  height: 48px;
  background: #ffffff;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  user-select: none;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-indicator-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--brand-primary);
}
.system-tag {
  font-size: 12px;
  color: #64748b;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.nav-link-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: none;
  font-size: 12px;
  color: #64748b;
  cursor: pointer;
}
.nav-link-btn:hover {
  color: var(--brand-primary);
}

.user-account-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.user-avatar-circle {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}
.user-phone {
  font-size: 12px;
  color: #334155;
  font-weight: 500;
}
</style>
