<script setup lang="ts">
import { ref } from 'vue';
import type { DocumentBlock, RevisionOperation } from '@/shared/types';
import ViewerToolbar from './components/ViewerToolbar.vue';
import RevisionBalloon from './components/RevisionBalloon.vue';

const props = defineProps<{
  blocks: DocumentBlock[];
  operations: RevisionOperation[];
  contractTitle: string;
  activeAnchor?: string;
}>();

const emit = defineEmits<{
  (e: 'accept-op', opId: string): void;
  (e: 'reject-op', opId: string): void;
}>();

const viewMode = ref<'markup' | 'original' | 'clean'>('markup');

const getOpForBlock = (b: DocumentBlock): RevisionOperation | undefined => {
  return props.operations.find(
    (op) => op.anchor === b.clause_id || (op.expected_text && b.text.includes(op.expected_text))
  );
};
</script>

<template>
  <div class="revision-viewer-wrapper">
    <ViewerToolbar
      v-model="viewMode"
      :contract-title="contractTitle"
    />

    <div class="document-canvas-container">
      <div class="document-paper">
        <div class="paper-header">
          <div class="confidential-tag">内部绝密 · 法务受控</div>
        </div>

        <h1 class="paper-title">{{ contractTitle }}</h1>

        <div class="paper-body">
          <div
            v-for="b in blocks"
            :key="b.block_id"
            :id="`block-${b.clause_id}`"
            class="contract-para"
            :class="{ 'is-active-anchor': activeAnchor === b.clause_id }"
          >
            <template v-if="getOpForBlock(b)">
              <div v-if="viewMode === 'markup'" class="markup-paragraph-row">
                <div class="paragraph-text">
                  <span class="clause-num-tag">{{ b.clause_id }}</span>
                  <del class="tracked-del">{{ getOpForBlock(b)!.expected_text }}</del>
                  <ins class="tracked-ins">{{ getOpForBlock(b)!.replacement_text }}</ins>
                </div>

                <RevisionBalloon
                  :op="getOpForBlock(b)!"
                  @accept="emit('accept-op', $event)"
                  @reject="emit('reject-op', $event)"
                />
              </div>

              <p v-else-if="viewMode === 'original'" class="clean-text">
                {{ b.text }}
              </p>

              <p v-else class="clean-text">
                {{ getOpForBlock(b)!.status === 'accepted' ? getOpForBlock(b)!.replacement_text : b.text }}
              </p>
            </template>

            <p v-else class="regular-para">
              {{ b.text }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.revision-viewer-wrapper { display: flex; flex-direction: column; height: 100%; background: #ffffff; overflow: hidden; }
.document-canvas-container { flex: 1; overflow-y: auto; padding: 30px 20px; display: flex; justify-content: center; background: #e2e8f0; }
.document-paper { width: 100%; max-width: 920px; background: #ffffff; color: #1e293b; border-radius: 4px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border: 1px solid #cbd5e1; padding: 50px 60px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "SimSun", "Songti SC", serif; min-height: 800px; }
.paper-header { display: flex; justify-content: flex-end; margin-bottom: 24px; }
.confidential-tag { font-size: 11px; color: #94a3b8; border: 1px dashed #cbd5e1; padding: 2px 8px; border-radius: 3px; }
.paper-title { font-size: 22px; font-weight: 700; text-align: center; margin-bottom: 36px; color: #0f172a; }
.paper-body { display: flex; flex-direction: column; gap: 20px; line-height: 1.85; font-size: 15px; }
.contract-para { padding: 6px 10px; border-radius: 4px; transition: all 0.3s ease; }
.contract-para.is-active-anchor { background: rgba(99, 102, 241, 0.12); outline: 2px solid #6366f1; }
.clause-num-tag { font-weight: 700; color: #0284c7; margin-right: 6px; }
.tracked-del { background-color: #fee2e2; color: #dc2626; text-decoration: line-through; padding: 1px 4px; border-radius: 2px; margin-right: 4px; }
.tracked-ins { background-color: #d1fae5; color: #059669; text-decoration: underline; text-underline-offset: 3px; padding: 1px 4px; border-radius: 2px; font-weight: 500; }
.markup-paragraph-row { display: flex; gap: 20px; align-items: flex-start; }
.paragraph-text { flex: 1; }
</style>
