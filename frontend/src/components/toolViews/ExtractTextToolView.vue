<template>
  <div
    class="h-[36px] flex items-center px-3 w-full bg-[var(--background-gray-main)] border-b border-[var(--border-main)] rounded-t-[12px] shadow-[inset_0px_1px_0px_0px_#FFFFFF] dark:shadow-[inset_0px_1px_0px_0px_#FFFFFF30]">
    <div class="flex-1 flex items-center justify-center">
      <div class="max-w-[300px] truncate text-[var(--text-tertiary)] text-sm font-medium text-center">
        {{ toolContent?.args?.url || 'Extract Text' }}
      </div>
    </div>
  </div>
  <div class="flex-1 min-h-0 w-full overflow-y-auto">
    <div class="px-4 py-3 h-full">
      <div
        v-if="renderedHtml"
        class="prose prose-sm dark:prose-invert max-w-none text-[var(--text-primary)] text-sm leading-relaxed break-words"
        v-html="renderedHtml"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-[var(--text-tertiary)] text-sm"
      >
        <span>{{ $t('Extracting text…') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { marked, Renderer } from 'marked';
import type { ToolContent } from '@/types/message';

const props = defineProps<{
  sessionId: string;
  toolContent: ToolContent;
  live: boolean;
  isShare?: boolean;
}>();

const renderer = new Renderer();
renderer.link = ({ href, title, text }) => {
  const t = title ? ` title="${title}"` : '';
  return `<a href="${href}"${t} target="_blank" rel="noopener noreferrer">${text}</a>`;
};

const renderedHtml = computed(() => {
  const content = props.toolContent?.content;
  if (!content) return '';
  const raw = content.markdown || content.text || '';
  if (!raw) return '';
  try {
    return marked(raw, { renderer, gfm: true, breaks: true }) as string;
  } catch {
    return `<pre class="whitespace-pre-wrap break-words">${raw}</pre>`;
  }
});
</script>
