<template>
  <ChcLabel div label="Choose what to do with the associated objects">
    <div class="radio-container">
      <ChcRadio
        v-model="state.associatedObjectsAction"
        type="radio"
        value="Delete"
        label="Delete"
      />

      <ChcRadio
        v-model="state.associatedObjectsAction"
        type="radio"
        value="Preserve"
        label="Preserve"
      />

      <ChcRadio
        v-model="state.associatedObjectsAction"
        type="radio"
        value="Archive"
        label="Archive"
      />
    </div>
  </ChcLabel>

  <template
    v-if="['Preserve', 'Archive'].includes(state.associatedObjectsAction)"
  >
    <ChcLabel
      div
      label="Choose what to do with the roles and identities created for this service"
    >
      <div class="radio-container">
        <ChcRadio
          v-model="state.rolesAndIdentitiesAction"
          type="radio"
          value="Delete"
          label="Delete"
        />

        <ChcRadio
          v-model="state.rolesAndIdentitiesAction"
          type="radio"
          value="Preserve"
          label="Keep"
        />

        <ChcRadio
          v-model="state.rolesAndIdentitiesAction"
          type="radio"
          value="Archive"
          label="Archive"
        />
      </div>
    </ChcLabel>

    <AvailableRoles
      v-if="state.rolesAndIdentitiesAction === 'Delete'"
      v-model="state.reparentRole"
    />
  </template>

  <ModalFooter
    :loading="loading"
    text="DELETE"
    @action="deleteService"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { defineEmits, defineProps, reactive, ref } from "vue";
import { useToast } from "vue-toastification";

import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";
import ModalFooter from "$shared/components/ModalFooter.vue";

import AvailableRoles from "@/components/AvailableRoles.vue";
import { useDeployedServicesStore } from "@/store/deployed-services";

const toast = useToast();
const deployedServicesStore = useDeployedServicesStore();

const emit = defineEmits(["finished", "cancel"]);

const props = defineProps({
  uuid: {
    type: String,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  associatedObjectsAction: "Delete",
  rolesAndIdentitiesAction: "Delete",
  reparentRole: "",
});

function deleteService() {
  let handleAccess = state.rolesAndIdentitiesAction;
  if (state.associatedObjectsAction === "Delete") {
    handleAccess = "Delete";
  }

  let reparentRole = undefined;
  if (
    state.associatedObjectsAction !== "Delete" &&
    state.rolesAndIdentitiesAction === "Delete"
  ) {
    reparentRole = state.reparentRole;
  }

  axios
    .delete(`/cuserv/v1/services/${props.uuid}`, {
      data: {
        handle_access: handleAccess,
        handle_objects: state.associatedObjectsAction,
        reparent_role: reparentRole,
      },
      errorContext: "Failed to delete service",
      loading,
    })
    .then(() => {
      deployedServicesStore.removeServiceByUuid(props.uuid);
      toast("Service deleted");
      emit("finished");
    })
    .finally(() => {
      state.loading = false;
    });
}
</script>
