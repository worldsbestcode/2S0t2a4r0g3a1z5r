<!-- Place this where you want an icon that spawns an editor modal -->
<!-- It will spawn a modal to edit an object of given storeType+uuid -->
<template>
  <Modal :title="props.title" ref="modalRef">
    <template #button="{ on, toggleModal }">
      <div class="tooltip-container" :data-tooltip="props.tooltip">
        <span
          class="material-symbols-outlined table__link"
          v-on="on"
          @click="init(on)"
          >{{ props.icon }}</span
        >
      </div>
    </template>
    <template #content="{ toggleModal }">
      <form @submit.prevent="save(toggleModal)">
        <slot />
        <ModalFooter :text="props.buttonText" @cancel="toggleModal" />
      </form>
    </template>
  </Modal>
</template>

<script setup>
import { defineProps, onMounted, ref, watch } from "vue";
import { useStore } from "vuex";

import Modal from "$shared/components/Modal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

const store = useStore();

const modalRef = ref(null);
const props = defineProps({
  title: {
    type: String,
    default: "",
    required: true,
  },
  tooltip: {
    type: String,
    default: "",
    required: true,
  },
  icon: {
    type: String,
    default: "",
    required: true,
  },
  uuid: {
    type: String,
    default: "",
    required: true,
  },
  buttonText: {
    type: String,
    default: "UPDATE",
    required: false,
  },
  submitDispatch: {
    type: String,
    default: "update",
    required: false,
  },
  storeType: {
    type: String,
    required: true,
  },
});

async function init(toggleModal) {
  try {
    await store.dispatch(props.storeType + "/load", props.uuid);
  } catch (error) {
    toggleModal.click();
  }
}

async function save(toggleModal) {
  try {
    await store.dispatch(props.storeType + "/" + props.submitDispatch);
    toggleModal();
  } catch (error) {
    // Toast should already be sent
  }
}
</script>

<style scoped>
.button-container {
  text-align: right; /* Align the button to the right */
  padding-top: 10px; /* Add padding above the button */
}

.button-container button {
  padding: 8px 16px; /* Add padding to the button for better appearance */
}
</style>
