<template>
  <div>
    <p>Certificate signing request</p>
    <textarea ref="textArea" v-model="csr" class="input" readonly />
    <nav>
      <button class="button" @click="saveToFile">Save to file</button>
      <button class="button" @click="copyToClipboard">Copy to clipboard</button>
    </nav>
  </div>
</template>

<script>
import { download, copyToClipboard } from "@/utils/misc.js";

export default {
  data: function () {
    return {
      csr: null,
      fileName: null,
    };
  },
  methods: {
    saveToFile: function () {
      download(this.csr, this.fileName);
    },
    copyToClipboard: function () {
      copyToClipboard(this.csr);
      this.$bus.emit("toaster", {
        message: "Copied to clipboard",
        type: "success",
      });
    },
  },
};
</script>

<style scoped>
p {
  text-align: center;
  font-size: 15px;
  margin-bottom: 0.5rem;
  color: var(--text-color-blue-lighter);
}

div {
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  margin-bottom: 1rem;
  padding: 1rem;
}

textarea {
  width: 100%;
  height: 300px;
  resize: none;
  pointer-events: none;
  margin-bottom: 1rem;
}

nav {
  display: flex;
  justify-content: flex-end;
}

button + button {
  margin-left: 0.5rem;
}
</style>
