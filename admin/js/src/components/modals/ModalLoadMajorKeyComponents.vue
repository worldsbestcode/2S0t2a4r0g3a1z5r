<template>
  <ChcModal v-model="showModal" title="Load Major Key from Components">
    <template #button="{ on }">
      <ChcButton style="font-size: 12px" secondary v-on="on">
        Load from components
      </ChcButton>
    </template>

    <template v-if="state.gatheringNumberOfComponents">
      <ChcInput
        v-model="state.numberOfComponents"
        label="Number of Components"
      />
    </template>
    <template v-else-if="state.gatheringComponents">
      <!-- todo: Create ChcComponent, 4 lines, split every 4 characters -->
      <ChcInput
        v-model="state.component"
        :label="`Component #${currentComponentNumber}/${state.numberOfComponents}`"
      />
    </template>
    <template v-else-if="state.finished">
      <p>You have finished loading the {{ props.majorKey }} major key.</p>
      <p>
        The {{ props.majorKey }} major key checksum is:
        <span class="checksum">{{ state.keyChecksum }}</span>
      </p>
    </template>

    <ModalFooter
      :loading="loading"
      :text="modalFooterText"
      @action="modalFooterAction"
      @cancel="toggleModal"
    />
  </ChcModal>
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref, watch } from "vue";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcModal from "$shared/components/ChcModal.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

const toast = useToast();

const emit = defineEmits(["newChecksum"]);

const props = defineProps({
  majorKey: {
    type: String,
    required: true,
  },
});

const showModal = ref(false);
const loading = ref(false);

const defaultState = {
  gatheringNumberOfComponents: true,
  numberOfComponents: 1,

  gatheringComponents: false,
  componentsRemaining: 0,
  component: "",

  finished: false,
  keyChecksum: null,
};

const state = reactive({ ...defaultState });

const modalFooterText = computed(() => {
  if (state.finished) {
    return "Finish";
  } else {
    return "Continue";
  }
});

const modalFooterAction = computed(() => {
  if (state.gatheringNumberOfComponents) {
    return handleGatheringNumberOfComponents;
  } else if (state.gatheringComponents) {
    return handleGatheringComponents;
  } else if (state.finished) {
    return toggleModal;
  }

  return undefined;
});

const currentComponentNumber = computed(
  () => state.numberOfComponents - state.componentsRemaining + 1,
);

function setDefault() {
  Object.assign(state, defaultState);
}

function toggleModal() {
  showModal.value = !showModal.value;
}

function handleGatheringNumberOfComponents() {
  axios
    .post(
      "/admin/v1/majorkeys/components",
      {
        majorKey: props.majorKey,
        numComponents: state.numberOfComponents,
      },
      {
        errorContext: "Failed to start major key loading session",
        loading: loading,
      },
    )
    .then(() => {
      state.gatheringNumberOfComponents = false;

      state.componentsRemaining = state.numberOfComponents;
      state.gatheringComponents = true;
    });
}

function handleGatheringComponents() {
  axios
    .post(
      "/admin/v1/majorkeys/components/next",
      {
        component: state.component,
      },
      {
        errorContext: "Failed to load major key component",
        loading: loading,
      },
    )
    .then((response) => {
      const componentChecksum = response.data.partChecksum;
      toast(`Loaded component with checksum of: ${componentChecksum}`);

      const keyChecksum = response.data.keyChecksum;
      if (keyChecksum) {
        emit("newChecksum", keyChecksum);
        state.keyChecksum = keyChecksum;
      }

      state.componentsRemaining--;
      state.component = "";

      if (state.componentsRemaining === 0) {
        state.gatheringComponents = false;
        state.finished = true;
      }
    });
}

watch(showModal, (value) => {
  if (!value) {
    setDefault();
  }
});
</script>
