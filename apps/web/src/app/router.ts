import { createRouter, createWebHistory } from 'vue-router';
import ContractsListPage from '@/pages/contracts/ContractsListPage.vue';
import WorkbenchPage from '@/pages/workbench/WorkbenchPage.vue';

const routes = [
  {
    path: '/',
    name: 'contracts-list',
    component: ContractsListPage
  },
  {
    path: '/workbench/:id',
    name: 'workbench',
    component: WorkbenchPage
  }
];

export const router = createRouter({
  history: createWebHistory(),
  routes
});
