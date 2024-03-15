<template>
  <div class="select-input-tr31">
    <select class="button" :value="selectValue" @input="selectInput">
      <option v-for="(v, k) in mappings" :key="k" :value="k">
        {{ v }}
      </option>
      <option v-if="customText" value="custom">
        {{ customText }}
      </option>
    </select>

    <key-block-header-input
      class="input"
      :maxlength="maxlength"
      :model-value="modelValue"
      @update:modelValue="$emit('update:modelValue', $event)"
    />
  </div>
</template>

<script>
import KeyBlockHeaderInput from "@/components/KeyBlockHeaderInput.vue";

export default {
  components: {
    KeyBlockHeaderInput,
  },
  props: {
    mappings: {
      type: Object,
      required: true,
    },
    modelValue: {
      type: String,
      required: true,
    },
    customText: {
      type: String,
    },
    maxlength: {
      type: String,
      required: true,
    },
  },
  computed: {
    selectValue: function () {
      if (this.valueInMappings(this.modelValue)) {
        return this.modelValue;
      } else {
        return "custom";
      }
    },
  },
  methods: {
    valueInMappings: function (value) {
      return Object.keys(this.mappings).includes(value);
    },

    selectInput: function (event) {
      if (event.target.value === "custom") {
        this.$emit("update:modelValue", "");
      } else if (this.valueInMappings(event.target.value)) {
        this.$emit("update:modelValue", event.target.value);
      }
    },
  },
};
</script>

<style scoped>
.select-input-tr31 {
  display: flex;
  gap: 0.5rem;
}

.select-input-tr31 select {
  text-overflow: ellipsis;
  width: 300px;
}

.select-input-tr31 input {
  font-family: monospace;
  width: 4ch;
  padding-left: 0;
  padding-right: 0;
  text-align: center;
}
</style>
