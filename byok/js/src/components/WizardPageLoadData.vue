<template>
  <ul class="wizard-page-list">
    <li>
      <button class="button button-wide" @click="handleLoadFileClick">
        Load from file
      </button>
      <button :disabled="data === ''" class="button" @click="data = ''">
        Clear
      </button>
      <input
        ref="fileInput"
        class="hidden"
        type="file"
        @change="handleFileSelected"
      />
      <button
        class="blue-button button button-wide"
        :disabled="data.length === 0"
        @click="handleContinueClick"
      >
        Continue
      </button>
    </li>
    <li class="paste-input">
      <textarea v-model="data" class="input"> </textarea>
    </li>
  </ul>
</template>

<script>
export default {
  title: "Load data",
  description: "Load the data",
  defaultData: function () {
    return {
      data: {
        value: "",
        wizardSummaryText: "data",
      },
    };
  },
  methods: {
    handleLoadFileClick: function () {
      this.$refs.fileInput.click();
    },
    handleFileSelected: async function (event) {
      let file = event.target.files[0];
      let arrayBuffer = await file.arrayBuffer();
      let bytes = Array.from(new Uint8Array(arrayBuffer));

      // if an unprintable character is found (besides CR and LF),
      // assume DER format
      let isDer = bytes.some((byte) => {
        if (byte < 32 || byte > 127) {
          return byte !== 10 && byte !== 13;
        }
      });

      let binaryString = bytes
        .map((byte) => String.fromCharCode(byte))
        .join("");
      if (isDer) {
        this.data = btoa(binaryString);
      } else {
        this.data = binaryString.trim();
      }
    },
    handleContinueClick: function () {
      this.nextPage();
    },
  },
};
</script>

<style scoped>
ul li.paste-input {
  border-top: 0;
  padding-top: 0;
}

.paste-input > textarea {
  width: 100%;
  height: 200px;
  resize: none;
}
</style>
