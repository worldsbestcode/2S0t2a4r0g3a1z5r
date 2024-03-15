<template>
  <ul class="wizard-page-list">
    <li
      v-for="(optionalBlock, index) in optionalBlocks"
      :key="optionalBlock.key"
    >
      <key-block-header-input
        v-model="optionalBlock.key"
        maxlength="2"
        class="input optional-block-key"
      />
      <key-block-header-input
        v-model="optionalBlock.value"
        maxlength="251"
        class="input optional-block-value"
      />

      <button class="button" @click="removeOptionalBlock(index)">
        <i class="fa fa-trash" />
      </button>
    </li>

    <li>
      <key-block-header-input
        v-model="newKey"
        maxlength="2"
        class="input optional-block-key"
      />
      <key-block-header-input
        v-model="newValue"
        maxlength="251"
        class="input optional-block-value"
      />

      <button class="button" @click="addOptionalBlock">
        <i class="fa fa-plus" />
      </button>
    </li>
  </ul>
</template>

<script>
import KeyBlockHeaderInput from "@/components/KeyBlockHeaderInput.vue";

export default {
  components: {
    KeyBlockHeaderInput,
  },
  props: {
    modelValue: {
      type: Array,
      required: true,
    },
  },
  data: function () {
    return {
      newKey: "",
      newValue: "",
      optionalBlocks: [],
    };
  },
  watch: {
    optionalBlocks: {
      handler: function (newValue) {
        this.$emit("update:modelValue", newValue);
      },
      deep: true,
    },
  },
  methods: {
    addOptionalBlock: function () {
      if (this.newKey.length !== 2) {
        this.$bus.emit("toaster", {
          message: "Optional header tag must be 2 characters",
        });
        return;
      }

      let keyExists = this.optionalBlocks.find((x) => x.key === this.newKey);
      if (keyExists) {
        this.$bus.emit("toaster", {
          message: "Optional header tag already exists",
        });
        return;
      }

      if (this.newKey === "PB") {
        this.$bus.emit("toaster", {
          message: "Optional header tag PB is not allowed",
        });
        return;
      }

      this.optionalBlocks.push({
        key: this.newKey,
        value: this.newValue,
      });
      this.newKey = "";
      this.newValue = "";
    },
    removeOptionalBlock: function (index) {
      this.optionalBlocks.splice(index, 1);
    },
  },
};
</script>

<style scoped>
.optional-blocks {
  margin-top: 1rem;
}

.optional-block-key {
  width: 6ch;
  text-align: center;
}

.optional-block-value {
  flex-grow: 1;
  margin: 0 0.5rem;
}
</style>
