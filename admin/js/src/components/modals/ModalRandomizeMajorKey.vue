<template>
  <ChcModalConfirm
    v-model="state.showModal"
    :loading="loading"
    title="Randomize Major Key"
    :action-text="actionText"
    @action="action"
    @cancel="toggleModal"
  >
    <template #button="{ on }">
      <ChcButton secondary v-on="on">Randomize</ChcButton>
    </template>

    <template v-if="state.newChecksum">
      <p>You have randomized the {{ props.majorKey }} major key.</p>

      <p>
        The {{ props.majorKey }} major key checksum is:
        <span class="checksum">{{ state.newChecksum }}</span>
      </p>
    </template>
    <template v-else>
      <p>
        This will generate a new random major key. This interface does not
        support backing up this key.
      </p>
    </template>
  </ChcModalConfirm>
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref, watch } from "vue";
import { useToast } from "vue-toastification";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcModalConfirm from "$shared/components/ChcModalConfirm.vue";

const emit = defineEmits(["newChecksum"]);
const toast = useToast();

const props = defineProps({
  majorKey: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  showModal: false,
  newChecksum: null,
});

const actionText = computed(() => (state.newChecksum ? "Finish" : "Randomize"));
const action = computed(() =>
  state.newChecksum ? toggleModal : randomizeMajorKey,
);

function toggleModal() {
  state.showModal = !state.showModal;
}

function randomizeMajorKey() {
  axios
    .post(
      "/admin/v1/majorkeys/random",
      {
        majorKey: props.majorKey,
      },
      {
        loading,
        errorContext: `Failed to randomize the ${props.majorKey} major key`,
      },
    )
    .then((response) => {
      toast(`Randomized the ${props.majorKey} major key.`);
      state.newChecksum = response.data.keyChecksum;
      emit("newChecksum", state.newChecksum);
    });
}

watch(
  () => state.showModal,
  (value) => {
    if (!value) {
      state.newChecksum = null;
    }
  },
);
</script>
