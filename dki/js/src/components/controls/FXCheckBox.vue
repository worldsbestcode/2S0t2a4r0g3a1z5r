<template>
  <div class="fx-checkbox-container">
    <input
      v-model="checked"
      type="checkbox"
      class="fx-checkbox"
      :style="checkBoxStyle"
      @click.stop="stopClick"
    />
    <slot name="label">
      <fx-label :theme="theme" :text="text"> </fx-label>
    </slot>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits, ref, onBeforeMount } from "vue";

const emit = defineEmits(["update:checked"]);
const props = defineProps({
  theme: {
    type: String,
    required: false,
    default: "muted",
  },
  text: {
    type: String,
    required: false,
    default: "",
  },
  density: {
    type: String,
    required: false,
    default: "default",
  },
  checked: {
    type: Boolean,
    required: false,
    default: false,
  },
});

const checked = computed({
  get() {
    return props.checked;
  },

  set(value) {
    emit("update:checked", value);
  },
});

const checkBoxStyle = ref({});
onBeforeMount(() => {
  let rightMargin;

  switch (props.density) {
    case "comfortable":
      rightMargin = "1rem";
      break;
    case "compact":
      rightMargin = "0.2rem";
      break;
    case "default":
    default:
      rightMargin = "0.5rem";
      break;
  }

  checkBoxStyle.value = {
    marginRight: rightMargin,
  };
});

// just used to stop mouse event propagation to parent
const stopClick = (event) => {
  event.stopPropagation();
};
</script>

<style scoped>
.fx-checkbox-container {
  display: flex;
  align-items: center;
  height: auto;
  width: auto;
}
.fx-checkbox {
  appearance: none;
  background-color: var(--primary-background-color);
  border: 2px solid #a6a6a6;
  border-radius: 3px;
  width: 18px;
  height: 18px;
  position: relative;
  cursor: pointer;
  display: grid;
  place-content: center;
}

.fx-checkbox::before {
  width: 0.65em;
  height: 0.65em;
  transform: scale(0);
  transition: 120ms transorm ease-in-out;
}
.fx-checkbox:checked {
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.fx-checkbox:checked:after {
  font-family: "Material Design Icons";
  content: "\F012C";
  color: var(--primary-background-color);
  transform: scale(1.3);
}
</style>
