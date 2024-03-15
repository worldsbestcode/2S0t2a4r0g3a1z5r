<template>
  <slot name="button" :on="{ click: toggleModal }" />

  <Teleport to="body">
    <div
      v-if="showModal"
      ref="modalDivRef"
      tabindex="-1"
      class="shared-modal"
      @click="toggleModal"
    >
      <div class="shared-modal__container" @click.stop>
        <header class="shared-modal__header">
          <h2 class="shared-modal__header-text">{{ props.title }}</h2>
          <button class="shared-modal__close-button" @click="toggleModal">
            <img src="/shared/static/close.svg" />
          </button>
        </header>
        <div class="shared-modal__body">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {
  computed,
  defineEmits,
  defineExpose,
  defineProps,
  reactive,
  ref,
} from "vue";

const emit = defineEmits(["update:modelValue"]);

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: null,
  },
});

const modalDivRef = ref(null);

const state = reactive({
  showModal: false,
});

const showModal = computed({
  get() {
    if (props.modelValue === null) {
      return state.showModal;
    } else {
      return props.modelValue;
    }
  },
  set(value) {
    if (props.modelValue === null) {
      state.showModal = value;
    } else {
      emit("update:modelValue", value);
    }
  },
});

function toggleModal() {
  showModal.value = !showModal.value;

  setTimeout(() => {
    if (showModal.value) {
      modalDivRef.value.focus();
    }
  });
}

defineExpose({
  toggleModal,
});
</script>

<style scoped>
.shared-modal {
  z-index: 1;

  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;

  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 6rem;

  overflow: auto;
  padding-bottom: 3rem;

  background: rgba(24, 24, 24, 0.8);
  backdrop-filter: blur(5px);
}

.shared-modal__container {
  background: var(--primary-background-color);
  border-radius: 5px;
  min-width: 400px;
  position: fixed;
}

.shared-modal__header {
  border-top-left-radius: inherit;
  border-top-right-radius: inherit;

  display: flex;
  justify-content: space-between;
  padding-right: 1.5rem;

  border-bottom: 1px solid var(--border-color);
}

.shared-modal__header-text {
  font-weight: 500;
  font-size: 24px;
  margin-left: 32px;
  margin-top: 12px;
  margin-bottom: 12px;
  color: var(--primary-color);
}

.shared-modal__close-button {
  background: 0;
  padding: 0;
  border: 0;
  margin-left: 32px;
}

.shared-modal__body {
  padding: 2rem;
}
</style>
