<template>
  <tr style="cursor: pointer" @click="copyUri">
    <th class="icon-with-hover">
      {{ props.name }} URI
      <ButtonIcon icon="clipboard-export" />
    </th>
    <td class="uri">
      <a class="chc-link" :href="uri" @click.prevent>{{ uri }}</a>
    </td>
  </tr>
</template>

<script setup>
import { computed, defineProps } from "vue";
import { useToast } from "vue-toastification";

import ButtonIcon from "@/components/ButtonIcon.vue";

const toast = useToast();

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  path: {
    type: String,
    required: true,
  },
});

const uri = computed(() => {
  const location = window.location;

  let returnUri = "";
  if (location.hostname !== "localhost") {
    returnUri += window.location.origin;
  }
  returnUri += `/gekms/gapi/v0${props.path}`;

  return returnUri;
});

function copyToClipboard(text) {
  let textArea = document.createElement("textArea");
  document.body.append(textArea);
  textArea.value = text;
  textArea.select();
  document.execCommand("copy");
  textArea.remove();
}

function copyUri() {
  copyToClipboard(uri.value);
  toast(`Copied ${props.name} URI to clipboard`);
}
</script>

<style scoped>
.uri {
  word-break: break-all;
  padding-left: 1rem;
  font-size: 13px;
}
</style>
