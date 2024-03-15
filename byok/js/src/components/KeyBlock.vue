<template>
  <div>
    <p class="key-block-heading">
      {{ heading }}
      <button @click="showEntireKeyBlock = !showEntireKeyBlock">
        <i class="fa fa-eye" />
      </button>
    </p>
    <p
      :title="keyBlock"
      :class="[
        'checksum',
        'key-block',
        showEntireKeyBlock ? 'key-block-full' : '',
      ]"
    >
      {{ keyBlock }}
    </p>
    <div class="key-block-buttons">
      <button class="button" @click="_copyToClipboard(keyBlock)">Copy</button>
      <button class="button" @click="download(keyBlock, fileName)">Save</button>
    </div>
  </div>
</template>

<script>
import { download, copyToClipboard } from "@/utils/misc.js";

export default {
  props: {
    heading: {
      type: String,
      required: true,
    },
    keyBlock: {
      type: String,
      required: true,
    },
    fileName: {
      type: String,
      required: true,
    },
  },
  data: function () {
    return {
      showEntireKeyBlock: false,
    };
  },
  methods: {
    download: download,
    _copyToClipboard: function (text) {
      copyToClipboard(text);
      this.$bus.emit("toaster", {
        message: "Copied to clipboard",
        type: "success",
      });
    },
  },
};
</script>

<style scoped>
.key-block-heading {
  font-size: 15px;
  margin-bottom: 0;
}

.key-block-heading button {
  border: 0;
  padding: 0;
  background: transparent;
  color: inherit;
}

.key-block {
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.5rem;
  white-space: nowrap;
}

.key-block-full {
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.key-block-buttons {
  display: flex;
}

.key-block-buttons button + button {
  margin-left: 0.5rem;
}
</style>
