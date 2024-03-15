<template>
  <button
    class="fx-button fx-button__plain"
    :disabled="disabled"
    :style="buttonStyle"
    @click="emit('click')"
  >
    <v-icon v-if="icon" :style="iconStyle"> {{ icon }}</v-icon>
    <fx-label v-if="text" class="ml-2" :text="text" :color="labelColor" />
  </button>
</template>

<script setup>
import { defineEmits, defineProps, ref, onBeforeMount } from "vue";

const emit = defineEmits(["click"]);

const props = defineProps({
  text: {
    type: String,
    required: false,
    default: "",
  },
  icon: {
    type: String,
    requred: false,
    default: "",
  },
  height: {
    type: String,
    required: false,
    default: "40px",
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
  theme: {
    type: String,
    required: false,
    default: "primary-text",
  },
  variant: {
    type: String,
    required: false,
    default: "outline", // tonal, plain are the other options.
  },
});

const labelColor = ref("");
const iconStyle = ref({});
const buttonStyle = ref({});

const getColor = () => {
  let color = "";
  switch (props.theme) {
    case "primary-text":
      color = "var(--primary-text-color)";
      break;
    case "primary":
    default:
      color = "var(--primary-color)";
      break;
  }

  return color;
};

onBeforeMount(() => {
  iconStyle.value.color = getColor();
  labelColor.value = getColor();

  buttonStyle.value.height = props.height;
  switch (props.variant) {
    case "plain":
      buttonStyle.value.border = "none";
      break;

    case "tonal":
      buttonStyle.value.backgroundColor = getColor();
      labelColor.value = "#FFFFFF";
      iconStyle.value.color = "#FFFFFF";
      break;
    case "outline":
    default:
      buttonStyle.value.border = "1px solid " + getColor();
      buttonStyle.value.backgroundColor = "inherit";
      break;
  }
});
</script>

<style scoped>
.fx-button {
  display: flex;
  border-radius: 5px;
  justify-content: center;
  align-items: center;
  width: fit-content;
  padding: 0 1rem;
}

.fx-button:disabled {
  opacity: 0.5;
}

.fx-button + .fx-button {
  margin-left: 0.25rem;
}
</style>
