<template>
  <GoogleCryptospaceFormInputs
    v-model:justifications="state.justifications"
    v-model:name="state.name"
    v-model:permissions="state.permissions"
  />

  <ModalFooter
    :loading="loading"
    text="CREATE CRYPTOSPACE"
    @action="createCryptospace"
    @cancel="emit('cancel')"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "vue-toastification";

import ModalFooter from "$shared/components/ModalFooter.vue";

import GoogleCryptospaceFormInputs from "@/components/google-cryptospace/GoogleCryptospaceFormInputs.vue";
import { cryptospacePermissions, justifications } from "@/google.js";

const route = useRoute();
const toast = useToast();

const emit = defineEmits(["finished", "cancel"]);

const loading = ref(false);

const state = reactive({
  name: "",
  justifications: [...justifications],
  permissions: [],
});

const serviceUuid = computed(() => route.params.serviceUuid);

function setupPermissions() {
  axios
    .get(`/gekms/v1/accounts/${serviceUuid.value}`, {
      errorContext: "Failed to fetch Google Cloud service accounts",
      loading,
    })
    .then((response) => {
      const accounts = response.data.accounts;

      for (const account of accounts) {
        state.permissions.push({
          accountUuid: account.uuid,
          accountName: account.name,
          perms: Object.values(cryptospacePermissions),
        });
      }
    });
}

function createCryptospace() {
  const accountPerms = [];
  for (const permission of state.permissions) {
    accountPerms.push({
      accountUuid: permission.accountUuid,
      perms: permission.perms,
    });
  }

  axios
    .post(
      "/gekms/v1/cryptospaces",
      {
        name: state.name,
        serviceUuid: serviceUuid.value,
        accountPerms,
        defaultJustifications: state.justifications,
      },
      {
        errorContext: "Failed to create CryptoSpace",
        emit: "updateCryptospaces",
        loading,
      },
    )
    .then(() => {
      toast("CryptoSpace created");
      emit("finished");
    });
}

setupPermissions();
</script>
