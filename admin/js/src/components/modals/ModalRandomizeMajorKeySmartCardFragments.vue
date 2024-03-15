<template>
  <ChcModal v-model="showModal" title="Randomize Major Key">
    <template #button="{ on }">
      <ChcButton style="font-size: 12px" secondary v-on="on">
        Randomize and save to smart cards
      </ChcButton>
    </template>

    <template v-if="state.gatheringMofn">
      <ChcInput
        v-model.number="state.numberToRecombine"
        label="Number to recombine"
      />
      <ChcInput v-model.number="state.numberOfParts" label="Number of parts" />
    </template>
    <template v-else-if="state.savingToSmartCards">
      <ChcInput
        v-model="state.smartCardPin"
        :label="`Smart card PIN (fragment ${currentFragmentNumber}/${state.numberOfParts})`"
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
      :loading="loading"
      :text="modalFooterText"
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

const emit = defineEmits(["newChecksum"]);
const toast = useToast();

const props = defineProps({
  majorKey: {
    type: String,
    required: true,
  },
});

const showModal = ref(false);
const loading = ref(false);

const defaultState = {
  gatheringMofn: true,
  numberToRecombine: 0,
  numberOfParts: 0,

  savingToSmartCards: false,
  fragmentsRemaining: 0,
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
  if (state.gatheringMofn) {
    return handleGatheringMofn;
  } else if (state.savingToSmartCards) {
    return handleSavingToSmartCards;
  } else if (state.finished) {
    return toggleModal;
  }

  return undefined;
});

const currentFragmentNumber = computed(
  () => state.numberOfParts - state.fragmentsRemaining + 1,
);

function setDefault() {
  Object.assign(state, defaultState);
}

function toggleModal() {
  showModal.value = !showModal.value;
}

function handleGatheringMofn() {
  axios
    .post(
      "/admin/v1/majorkeys/random",
      {
        majorKey: props.majorKey,
        saveToSmartcard: true,
        remote: false,
        numRecombine: state.numberToRecombine,
        numSmartcards: state.numberOfParts,
      },
      {
        errorContext: "Failed to randomize major key",
        loading: loading,
      },
    )
    .then((response) => {
      const newChecksum = response.data.keyChecksum;
      state.newChecksum = newChecksum;
      emit("newChecksum", newChecksum);
      toast(`The ${props.majorKey} major key was randomized.`);

      state.gatheringMofn = false;

      state.savingToSmartCards = true;
      state.fragmentsRemaining = state.numberOfParts;
    });
}

function handleSavingToSmartCards() {
  axios
    .get("/admin/v1/majorkeys/random/next", {
      params: {
        pin: state.smartCardPin,
      },
      errorContext: "Failed to save major key fragment to smart card",
      loading: loading,
    })
    .then((response) => {
      const data = response.data;
      const partChecksum = data.partChecksum;
      toast(`Saved fragment with checksum of: ${partChecksum}`);

      if (data.nextCard) {
        state.fragmentsRemaining--;
        state.smartCardPin = "";
      } else {
        state.savingToSmartCards = false;
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
