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
    (op) => (b.clause_id && op.anchor === b.clause_id) || (op.expected_text && b.text.includes(op.expected_text.trim()))
  );
};

// Word-Grade Intelligent Inline Diff Algorithm
// Avoids duplicate full-paragraph deletions when only modifying or appending clauses
const getMarkupParts = (text: string, op: RevisionOperation) => {
  const exp = op.expected_text?.trim() || '';
  const rep = op.replacement_text?.trim() || '';

  if (!exp) {
    return { before: text, del: '', ins: rep, after: '' };
  }

  // 1. If replacement is purely appending to expected text (e.g. adding cap or grace period)
  if (rep.startsWith(exp)) {
    const appended = rep.slice(exp.length);
    const pos = text.indexOf(exp);
    if (pos >= 0) {
      return {
        before: text.slice(0, pos + exp.length),
        del: '',
        ins: appended,
        after: text.slice(pos + exp.length)
      };
    }
  }

  // 2. Find common prefix and suffix to isolate minimal diff
  const pos = text.indexOf(exp);
  if (pos >= 0) {
    const prefixOffset = pos;
    let pLen = 0;
    while (pLen < exp.length && pLen < rep.length && exp[pLen] === rep[pLen]) {
      pLen++;
    }

    let sLen = 0;
    while (
      sLen < (exp.length - pLen) &&
      sLen < (rep.length - pLen) &&
      exp[exp.length - 1 - sLen] === rep[rep.length - 1 - sLen]
    ) {
      sLen++;
    }

    const before = text.slice(0, prefixOffset + pLen);
    const del = exp.slice(pLen, exp.length - sLen);
    const ins = rep.slice(pLen, rep.length - sLen);
    const after = text.slice(prefixOffset + exp.length - sLen);

    return { before, del, ins, after };
  }

  // Fallback: whole text diff
  return { before: '', del: exp, ins: rep, after: '' };
};

const isSectionHeading = (b: DocumentBlock): boolean => {
  if (b.is_title) return false;
  const t = b.text.trim();
  return /^(?:[一二三四五六七八九十百]+[、.．]|第[一二三四五六七八九十百]+[条章节款])/.test(t) && t.length <= 40;
};
</script>

<template>
  <div class="revision-viewer-wrapper">
    <ViewerToolbar
      v-model="viewMode"
      :contract-title="contractTitle"
    />

    <div class="document-canvas-container">
      <!-- Authentic Word A4 Paper Canvas -->
      <div class="document-paper a4-page">
        <div class="paper-body">
          <template v-for="b in blocks" :key="b.block_id">
            <!-- Word Blank Line Spacer -->
            <div v-if="b.is_blank" class="word-blank-row"></div>

            <!-- Natural Word Paragraph - Clean Typography without intrusive badges -->
            <div
              v-else
              :id="`block-${b.clause_id}`"
              class="contract-para"
              :class="[
                `align-${b.align || 'left'}`,
                {
                  'is-active-anchor': activeAnchor && (activeAnchor === b.clause_id || (b.clause_id && activeAnchor.includes(b.clause_id))),
                  'is-title-para': b.is_title,
                  'is-section-heading': isSectionHeading(b),
                  'has-indent': b.indent && b.align !== 'center' && b.align !== 'right',
                  'is-bold': b.bold || isSectionHeading(b)
                }
              ]"
            >
              <!-- With Revision Operation (Track Changes) -->
              <template v-if="getOpForBlock(b)">
                <div v-if="viewMode === 'markup'" class="markup-paragraph-row">
                  <div class="paragraph-text">
                    <span class="inline-text-flow">
                      {{ getMarkupParts(b.text, getOpForBlock(b)!).before }}
                      <del v-if="getMarkupParts(b.text, getOpForBlock(b)!).del" class="word-tracked-del">
                        {{ getMarkupParts(b.text, getOpForBlock(b)!).del }}
                      </del>
                      <ins v-if="getMarkupParts(b.text, getOpForBlock(b)!).ins" class="word-tracked-ins">
                        {{ getMarkupParts(b.text, getOpForBlock(b)!).ins }}
                      </ins>
                      {{ getMarkupParts(b.text, getOpForBlock(b)!).after }}
                    </span>
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

              <!-- Regular Paragraph without revisions -->
              <p v-else class="regular-para">
                {{ b.text }}
              </p>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.revision-viewer-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f1f5f9;
  overflow: hidden;
}

.document-canvas-container {
  flex: 1;
  overflow-y: auto;
  padding: 36px 20px 100px;
  background: #cbd5e1;
}

/* Authentic Word A4 Paper Dimensions and Shadow */
.document-paper.a4-page {
  position: relative;
  width: 100%;
  max-width: 840px;
  margin: 0 auto;
  background: #ffffff;
  color: #111827;
  border-radius: 2px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #cbd5e1;
  padding: 68px 76px 100px;
  /* Authentic Chinese Legal Contract Word Font Stack (SimSun 12pt / 16px) */
  font-family: "SimSun", "宋体", "STSong", "Microsoft YaHei", -apple-system, serif;
  font-size: 16px;
  line-height: 1.72;
  min-height: 1160px;
  height: auto;
  box-sizing: border-box;
}

.paper-body {
  display: flex;
  flex-direction: column;
}

.word-blank-row {
  height: 16px;
}

.contract-para {
  margin: 0 0 4px 0;
  padding: 1px 4px;
  transition: all 0.2s ease;
  word-break: break-word;
  position: relative;
  border-radius: 2px;
  line-height: 1.72;
}
.contract-para.is-active-anchor {
  background: rgba(99, 102, 241, 0.08);
  outline: 1.5px solid #6366f1;
}

/* Word Standard Paragraph Alignments */
.contract-para.align-center {
  text-align: center;
}
.contract-para.align-right {
  text-align: right;
  padding-right: 4px;
}
.contract-para.align-left {
  text-align: left;
}
.contract-para.align-justify {
  text-align: justify;
}

/* Contract Main Heading Style (e.g. 年度采购协议) */
.contract-para.is-title-para {
  font-family: "SimSun", "宋体", "STSong", "Microsoft YaHei", serif;
  font-size: 22px;
  font-weight: 700;
  color: #000000;
  margin-top: 6px;
  margin-bottom: 16px;
  letter-spacing: 2px;
}

/* Contract Major Section Heading (e.g. 一、前提条件, 二、合作期限) */
.contract-para.is-section-heading {
  font-family: "SimSun", "宋体", "STSong", "Microsoft YaHei", serif !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  margin-top: 18px !important;
  margin-bottom: 6px !important;
}

/* Standard Chinese 2-Character First Line Indent */
.contract-para.has-indent {
  text-indent: 2em;
}

.contract-para.is-bold {
  font-weight: 700;
  color: #000000;
}

.regular-para, .clean-text {
  margin: 0;
}

/* Word Track Changes Style */
.markup-paragraph-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  position: relative;
}
.paragraph-text {
  flex: 1;
}

.word-tracked-del {
  background-color: transparent;
  color: #dc2626;
  text-decoration: line-through;
  text-decoration-thickness: 1.5px;
  text-decoration-color: #dc2626;
  padding: 0 1px;
  font-weight: normal;
}

.word-tracked-ins {
  background-color: transparent;
  color: #1d4ed8;
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-thickness: 1.5px;
  text-decoration-color: #1d4ed8;
  padding: 0 1px;
  font-weight: 600;
}
</style>
