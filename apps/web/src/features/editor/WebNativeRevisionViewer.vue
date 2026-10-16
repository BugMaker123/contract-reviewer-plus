<script setup lang="ts">
import { ref } from 'vue';
import type { DocumentBlock, RevisionOperation } from '@/shared/types';
import ViewerToolbar from './components/ViewerToolbar.vue';
import { AlertTriangle } from 'lucide-vue-next';

const props = defineProps<{
  blocks: DocumentBlock[];
  operations: RevisionOperation[];
  contractTitle: string;
  activeAnchor?: string;
}>();

const emit = defineEmits<{
  (e: 'accept-op', opId: string): void;
  (e: 'reject-op', opId: string): void;
  (e: 'locate', anchor: string): void;
  (e: 'scroll-focus', anchor: string): void;
}>();

const viewMode = ref<'markup' | 'original' | 'clean'>('markup');
const canvasRef = ref<HTMLElement | null>(null);

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

// 左右智能联动：滚动左侧正文时，检测最接近视口焦点的风险条款，通知父级联动右侧卡片
const handleScroll = () => {
  if (!canvasRef.value) return;
  const container = canvasRef.value;
  const containerRect = container.getBoundingClientRect();
  const triggerLine = containerRect.top + containerRect.height * 0.35;

  let closestAnchor = '';
  let minDistance = Infinity;

  props.blocks.forEach((b) => {
    if (!b.clause_id) return;
    const hasOp = getOpForBlock(b);
    if (!hasOp) return;

    const el = document.getElementById(`block-${b.clause_id}`);
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const dist = Math.abs(rect.top - triggerLine);
    if (dist < minDistance && rect.bottom > containerRect.top && rect.top < containerRect.bottom) {
      minDistance = dist;
      closestAnchor = b.clause_id;
    }
  });

  if (closestAnchor && closestAnchor !== props.activeAnchor) {
    emit('scroll-focus', closestAnchor);
  }
};
</script>

<template>
  <div class="revision-viewer-wrapper">
    <ViewerToolbar
      v-model="viewMode"
      :contract-title="contractTitle"
    />

    <div ref="canvasRef" class="document-canvas-container" @scroll="handleScroll">
      <!-- Authentic Word A4 Paper Canvas -->
      <div class="document-paper a4-page">
        <div class="paper-body">
          <template v-for="b in blocks" :key="b.block_id">
            <!-- Word Blank Line Spacer -->
            <div v-if="b.is_blank" class="word-blank-row"></div>

            <!-- Natural Word Paragraph - Clean Typography without intrusive inline badges -->
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
              @click="getOpForBlock(b) && emit('locate', b.clause_id || '')"
            >
              <!-- With Revision Operation (Track Changes) -->
              <template v-if="getOpForBlock(b)">
                <div v-if="viewMode === 'markup'" class="markup-paragraph-row">
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

                  <!-- 红框位置：正文右侧大字加粗引线批注标签 -->
                  <span
                    class="risk-callout-right"
                    @click.stop="emit('locate', b.clause_id || '')"
                    title="点击查看 AI 审查建议详情"
                  >
                    <span class="callout-line"></span>
                    <span class="callout-content">
                      <AlertTriangle :size="15" />
                      建议修订
                    </span>
                  </span>
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
  position: relative;
  display: inline;
}

/* 红框位置：正文右侧大字加粗引线批注标签 (高度还原 Word 批注) */
.risk-callout-right {
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  z-index: 15;
  cursor: pointer;
  text-indent: 0;
  user-select: none;
  white-space: nowrap;
}

.callout-line {
  width: 24px;
  height: 1.5px;
  background: #dc2626;
  display: inline-block;
  margin-right: -1px;
}

.callout-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #ffffff;
  border: 1.5px solid #dc2626;
  color: #dc2626;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 15px; /* 加大字体 */
  font-weight: 700; /* 加粗展示 */
  padding: 5px 12px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.12);
  white-space: nowrap;
  letter-spacing: 0.5px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.risk-callout-right:hover .callout-content {
  background: #fef2f2;
  border-color: #b91c1c;
  color: #b91c1c;
  transform: scale(1.04);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.22);
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
