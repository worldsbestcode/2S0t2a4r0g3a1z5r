<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div class="chc-markdown" v-html="markdownHtml" />
</template>

<script setup>
import DOMPurify from "dompurify";
import showdown from "showdown";
import { computed, defineProps } from "vue";

// todo: Consider moving to shared if needed elsewhere, must install DOMPurify and showdown into other projects

const props = defineProps({
  markdown: {
    type: String,
    default: undefined,
  },
});

const converter = new showdown.Converter();

const markdownHtml = computed(() =>
  DOMPurify.sanitize(converter.makeHtml(props.markdown)),
);
</script>

<style>
.chc-markdown img {
  max-width: 100%;
}

/* duplication of .chc-link */
.chc-markdown a {
  color: var(--primary-color);
  text-decoration: none;
}

.chc-markdown a:hover {
  color: var(--primary-color);
  text-decoration: underline;
}
</style>
