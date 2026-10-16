<script setup lang="ts">
defineProps<{
  size?: number;
}>();
</script>

<template>
  <div class="app-logo-badge" :style="{ width: `${size || 32}px`, height: `${size || 32}px` }">
    <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg-elem">
      <!-- Shield Outer Contour -->
      <path
        d="M18 3L5 8.5V17.5C5 25.5 10.6 32.2 18 34C25.4 32.2 31 25.5 31 17.5V8.5L18 3Z"
        fill="url(#shieldGrad)"
      />
      <!-- Inner Legal Document Sheets Geometric Pattern -->
      <path
        d="M13 12H21C22.1 12 23 12.9 23 14V22C23 23.1 22.1 24 21 24H13C11.9 24 11 23.1 11 22V14C11 12.9 11.9 12 13 12Z"
        fill="#ffffff"
        fill-opacity="0.25"
      />
      <!-- Crisp Check & Revision Balance Pen -->
      <path
        d="M14 18.2L16.8 21L22.5 15.3"
        stroke="#ffffff"
        stroke-width="2.6"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <defs>
        <linearGradient id="shieldGrad" x1="5" y1="3" x2="31" y2="34" gradientUnits="userSpaceOnUse">
          <stop stop-color="#3b82f6" />
          <stop offset="1" stop-color="#1d4ed8" />
        </linearGradient>
      </defs>
    </svg>
  </div>
</template>

<style scoped>
.app-logo-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
  user-select: none;
}
.logo-svg-elem {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 4px rgba(37, 99, 235, 0.25));
}
</style>
