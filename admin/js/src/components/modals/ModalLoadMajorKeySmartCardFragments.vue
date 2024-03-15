<template>
  <ChcModal
    v-model="showModal"
    title="Load Major Key from Smart Card Fragments"
  >
    <template #button="{ on }">
      <ChcButton style="font-size: 12px" secondary v-on="on">
        Load from smart card fragments
      </ChcButton>
    </template>

    <template v-if="state.gatheringSmartCardPin">
      <ChcInput
        v-model="state.smartCardPin"
        :label="`Smart card PIN (fragment #${state.smartCardCount})`"
      />
    </template>
    <template v-else-if="state.finished">
      <p>You have randomized the {{ props.majorKey }} major key.</p>

      <p>
        The {{ props.majorKey }} major key checksum is:
        <span class="checksum">{{ state.newChecksum }}</span>
      </p>
    </template>

    <ModalFooter
      :text="modalFooterText"
      :loading="loading"
      @action="modalFooterAction"
      @cancel="toggleModal"
    >
    </ModalFooter>
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
  gatheringSmartCardPin: true,
  smartCardCount: 1,
  smartCardPin: "",

  finished: false,
  newChecksum: null,
};

const state = reactive({
  ...defaultState,
});

const modalFooterText = computed(() => {
  if (state.finished) {
    return "Finish";
  } else {
    return "Continue";
  }
});
const modalFooterAction = computed(() => {
  if (state.gatheringSmartCardPin) {
    return handleGatheringSmartCardPin;
  } else {
    return toggleModal;
  }
});

function setDefault() {
  Object.assign(state, defaultState);
}

function toggleModal() {
  showModal.value = !showModal.value;
}

function startFragmentLoadingSession() {
  axios.post(
    "/admin/v1/majorkeys/fragments",
    {
      majorKey: props.majorKey,
      remote: false,
    },
    {
      errorContext: "Failed to start major key loading session",
      loading: loading,
    },
  );
}

function handleGatheringSmartCardPin() {
  axios
    .post(
      "/admin/v1/majorkeys/fragments/next",
      {
        pin: state.smartCardPin,
      },
      {
        errorContext: "Failed to load fragment",
        loading: loading,
      },
    )
    .then((response) => {
      const checksum = response.data.partChecksum;
      toast(`Successfully loaded fragment with checksum of: ${checksum}`);
      state.smartCardCount++;
      state.smartCardPin = "";

      const newChecksum = response.data.keyChecksum;
      if (newChecksum) {
        state.gatheringSmartCardPin = false;
        state.finished = true;
        state.newChecksum = newChecksum;
        emit("newChecksum", newChecksum);
      }
    });
}

watch(showModal, (value) => {
  if (value) {
    startFragmentLoadingSession();
  } else {
    setDefault();
  }
});
</script>
