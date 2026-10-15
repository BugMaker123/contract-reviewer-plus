<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/shared/http/client';
import type { Contract } from '@/shared/types';
import BaseButton from '@/shared/ui/BaseButton.vue';
import ContractDashboardCard from '@/features/contracts/components/ContractDashboardCard.vue';
import ContractUploadModal from '@/features/contracts/components/ContractUploadModal.vue';
import { FileText, Upload, Play, Shield, Search } from 'lucide-vue-next';

const router = useRouter();
const contracts = ref<Contract[]>([]);
const isLoading = ref(true);
const searchQuery = ref('');
const showUploadModal = ref(false);
const isUploading = ref(false);

const loadContracts = async () => {
  isLoading.value = true;
  try {
    const res: any = await api.get('/contracts');
    contracts.value = res.contracts;
  } finally {
    isLoading.value = false;
  }
};

const createSampleContract = async () => {
  isLoading.value = true;
  try {
    const res: any = await api.post('/contracts', {});
    router.push(`/workbench/${res.contract.id}`);
  } finally {
    isLoading.value = false;
  }
};

const submitUpload = async (data: { file: File | null; title: string; stance: string }) => {
  isUploading.value = true;
  try {
    const formData = new FormData();
    if (data.file) {
      formData.append('file', data.file);
    }
    formData.append('title', data.title);
    formData.append('stance', data.stance);

    const res: any = await api.post('/contracts', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    showUploadModal.value = false;
    router.push(`/workbench/${res.contract.id}`);
  } finally {
    isUploading.value = false;
  }
};

onMounted(loadContracts);
</script>

<template>
  <div class="contracts-page-layout">
    <header class="contracts-hero glass-panel">
      <div class="hero-brand">
        <div class="brand-logo-glow">
          <Shield :size="22" class="logo-icon" />
        </div>
        <div>
          <h1 class="hero-title">企业合同审查与修订复核系统</h1>
          <p class="hero-subtitle">基于 DOCX 原生修订痕迹的合同合规审查、法务复核与交付管理平台</p>
        </div>
      </div>

      <div class="hero-actions">
        <BaseButton variant="secondary" @click="createSampleContract">
          <Play :size="14" /> 载入示例合同样本
        </BaseButton>
        <BaseButton variant="primary" @click="showUploadModal = true">
          <Upload :size="14" /> 上传合同文档 (.docx)
        </BaseButton>
      </div>
    </header>

    <main class="contracts-content-container">
      <div class="content-toolbar">
        <h2 class="section-title">合同任务列表 ({{ contracts.length }})</h2>
        <div class="search-box">
          <Search :size="14" class="search-ic" />
          <input v-model="searchQuery" type="text" class="search-inp" placeholder="搜索合同名称..." />
        </div>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <span>正在读取合同任务与版本历史...</span>
      </div>

      <div v-else-if="contracts.length === 0" class="empty-cards-state">
        <FileText :size="48" class="empty-icon" />
        <h3 class="empty-title">当前尚无合同审查任务</h3>
        <p class="empty-desc">您可以点击上方按钮直接载入标准合同样本，或上传本地 Word (.docx) 文件进行条款审查与修订复核。</p>
        <BaseButton variant="primary" size="md" @click="createSampleContract">
          载入示例合同文档
        </BaseButton>
      </div>

      <div v-else class="contracts-cards-grid">
        <ContractDashboardCard
          v-for="c in contracts"
          :key="c.id"
          :contract="c"
          @click="router.push(`/workbench/${c.id}`)"
        />
      </div>
    </main>

    <ContractUploadModal
      v-model="showUploadModal"
      :loading="isUploading"
      @submit="submitUpload"
    />
  </div>
</template>

<style scoped>
.contracts-page-layout { min-height: 100vh; display: flex; flex-direction: column; background: #f8fafc; }
.contracts-hero { padding: 20px 36px; background: #ffffff; border-bottom: 1px solid #e2e8f0; border-radius: 0; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03); }
.hero-brand { display: flex; align-items: center; gap: 14px; }
.brand-logo-glow { width: 40px; height: 40px; border-radius: var(--radius-sm); background: #2563eb; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(37, 99, 235, 0.25); }
.logo-icon { color: #fff; }
.hero-title { font-family: var(--font-heading); font-size: 18px; font-weight: 700; color: #0f172a; }
.hero-subtitle { font-size: 13px; color: #64748b; }
.hero-actions { display: flex; gap: 12px; }
.contracts-content-container { flex: 1; padding: 28px 36px; max-width: 1320px; margin: 0 auto; width: 100%; }
.content-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.section-title { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: #0f172a; }
.search-box { position: relative; display: flex; align-items: center; }
.search-ic { position: absolute; left: 10px; color: #94a3b8; }
.search-inp { padding: 6px 14px 6px 32px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: var(--radius-sm); color: #0f172a; font-size: 13px; outline: none; width: 220px; }
.search-inp:focus { border-color: #2563eb; }
.contracts-cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 18px; }
.empty-cards-state { text-align: center; padding: 80px 20px; display: flex; flex-direction: column; align-items: center; gap: 14px; background: #ffffff; border: 1px dashed #cbd5e1; border-radius: var(--radius-lg); }
.empty-icon { color: #94a3b8; }
.empty-title { font-size: 16px; color: #0f172a; font-weight: 600; }
.empty-desc { font-size: 13px; color: #64748b; max-width: 480px; line-height: 1.6; }
</style>
