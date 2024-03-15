<template>
  <GoogleCryptospaceFormInputs
    v-model:justifications="state.justifications"
    v-model:name="state.name"
    v-model:permissions="state.permissions"
  />

  <ModalFooter
    :loading="loading"
    text="EDIT CRYPTOSPACE"
    @action="editCryptospace"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleCryptospaceFormInputs from "@/components/google-cryptospace/GoogleCryptospaceFormInputs.vue";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const loading = ref(false);

const props = defineProps({
  cryptospace: {
    type: Object,
    required: true,
  },
  serviceAccounts: {
    type: Array,
    required: true,
  },
});

const state = reactive({
  name: props.cryptospace.objInfo.name,
  justifications: props.cryptospace.defaultJustifications,
  permissions: props.cryptospace.accountPerms,
});

const cryptospaceUuid = computed(() => route.params.cryptospaceUuid);

function editCryptospace() {
  const accountPerms = [];
  for (const permission of state.permissions) {
    accountPerms.push({
      accountUuid: permission.accountUuid,
      perms: permission.perms,
    });
  }

  axios
    .patch(
      `/gekms/v1/cryptospaces/${cryptospaceUuid.value}`,
      {
        name: state.name,
        defaultJustifications: state.justifications,
        accountPerms,
      },
      {
        errorContext: "Failed to edit CryptoSpace",
        emit: "updateCryptospace",
        loading,
      },
    )
    .then(() => {
      toast("CryptoSpace edited");
      emit("finished");
    });
}

function setupPermissions() {
  state.permissions = props.cryptospace.accountPerms;
  for (const permission of state.permissions) {
    const accountName = props.serviceAccounts.find(
      (serviceAccount) => serviceAccount.uuid === permission.accountUuid,
    ).name;
    permission.accountName = accountName;
  }
}

function fillInMissingServiceAccountPermissions() {
  for (const serviceAccount of props.serviceAccounts) {
    if (
      !state.permissions.find(
        (permission) => permission.accountUuid === serviceAccount.uuid,
      )
    ) {
      state.permissions.push({
        accountUuid: serviceAccount.uuid,
        accountName: serviceAccount.name,
        perms: [],
      });
    }
  }
}

setupPermissions();
fillInMissingServiceAccountPermissions();
</script>
