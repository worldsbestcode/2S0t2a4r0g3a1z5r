<template>
  <GoogleCryptospaceKeyFormInputs
    v-model:justifications="state.justifications"
    v-model:keyAlgorithm="state.keyAlgorithm"
    v-model:name="state.name"
    v-model:rotationPeriod="state.rotationPeriod"
  />

  <ModalFooter
    :loading="loading"
    text="CREATE KEY"
    @action="createKey"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, reactive, ref, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleCryptospaceKeyFormInputs from "@/components/google-cryptospace/GoogleCryptospaceKeyFormInputs.vue";
import { justifications } from "@/google.js";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const loading = ref(false);

const state = reactive({
  justifications: [...justifications],
  name: "",
  keyAlgorithm: "ALGORITHM_EXTERNAL_SYMMETRIC_ENCRYPTION",
  rotationPeriod: "5 Days",
});

const cryptospaceUuid = computed(() => route.params.cryptospaceUuid);

function createKey() {
  axios
    .post(
      `/gekms/v1/keys`,
      {
        name: state.name,
        crypto_space: cryptospaceUuid.value,
        algorithm: state.keyAlgorithm,
        rotation_period: state.rotationPeriod,
        justifications: state.justifications,
      },
      {
        errorContext: "Failed to create key",
        emit: "updateCryptospaceKeys",
        loading,
      },
    )
    .then(() => {
      toast("Key created");
      emit("finished");
    });
}

watchEffect(() => {
  if (state.keyAlgorithm === "ALGORITHM_EXTERNAL_SYMMETRIC_ENCRYPTION") {
    if (state.rotationPeriod === undefined) {
      state.rotationPeriod = "5 Days";
    }
  } else {
    state.rotationPeriod = undefined;
  }
});
</script>
