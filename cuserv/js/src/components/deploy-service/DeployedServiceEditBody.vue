<template>
  <ChcInput
    v-model="state.name"
    hint="length 3-64"
    label="Name"
    placeholder="Service name"
  />

  <DeployServiceCategoryFuzzy v-model="state.category" />

  <ModalFooter
    :loading="loading"
    text="EDIT"
    @action="editService"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, reactive, ref } from "vue";
import { useToast } from "vue-toastification";

import ChcInput from "$shared/components/ChcInput.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

import DeployServiceCategoryFuzzy from "@/components/deploy-service/DeployServiceCategoryFuzzy.vue";
import { useDeployedServicesStore } from "@/store/deployed-services";

const toast = useToast();
const deployedServicesStore = useDeployedServicesStore();

const emit = defineEmits(["finished", "cancel"]);

const props = defineProps({
  uuid: { type: String, required: true },
  name: { type: String, required: true },
  category: { type: String, required: true },
});

const loading = ref(false);

const state = reactive({
  name: props.name,
  category: props.category,
});

function editService() {
  axios
    .patch(
      `/cuserv/v1/services/${props.uuid}`,
      {
        name: state.name,
        category: state.category,
      },
      {
        errorContext: "Failed to edit service",
        emit: "updateDeployedServices",
        loading,
      },
    )
    .then(() => {
      deployedServicesStore.refreshServiceByUuid(props.uuid);
      toast("Service edited");
      emit("finished");
    });
}
</script>
