<template>
  <main class="settings-view">
    <div>
      <h2>System Settings</h2>
      <div class="system-settings">
        <ChcModalConfirm title="Reboot" action-closes @action="reboot">
          <template #button="{ on }">
            <ChcButton
              secondary
              :loading="rebootLoading"
              :disabled="systemActionDisabled"
              v-on="on"
            >
              Reboot
            </ChcButton>
          </template>
          Are you sure you want to reboot the device?
          <br />
          <br />
          This action will return you to the login page.
        </ChcModalConfirm>

        <ChcModalConfirm title="Restart" action-closes @action="restart">
          <template #button="{ on }">
            <ChcButton
              secondary
              :loading="restartLoading"
              :disabled="systemActionDisabled"
              v-on="on"
            >
              Restart
            </ChcButton>
          </template>
          Are you sure you want to restart the server process?
          <br />
          <br />
          This action will return you to the login page.
        </ChcModalConfirm>

        <ChcModalConfirm title="Debug" action-closes @action="debug">
          <template #button="{ on }">
            <ChcButton
              secondary
              :loading="debugLoading"
              :disabled="systemActionDisabled"
              v-on="on"
            >
              Debug
            </ChcButton>
          </template>
          Are you sure you want to debug the restart server process?
          <br />
          <br />
          This action will return you to the login page.
        </ChcModalConfirm>
      </div>
    </div>

    <div>
      <LoadingSpinner
        v-if="fetchServicesLoading"
        :loading="fetchServicesLoading"
      />
      <template v-else>
        <h2>Service Settings</h2>
        <div class="service-settings">
          <div
            v-for="service in state.services"
            :key="service"
            class="service__container"
          >
            <div class="service__text">
              {{ service }}
            </div>
            <ChcButton
              :disabled="restartServiceLoading[service].value"
              secondary
              small
              @click="restartService(service)"
            >
              Restart
            </ChcButton>
          </div>
        </div>
      </template>
    </div>
  </main>
</template>

<script setup>
import axios from "axios";
import { computed, reactive, ref } from "vue";
import { useToast } from "vue-toastification";
import { useStore } from "vuex";

import { sendToLogin } from "$shared";
import ChcButton from "$shared/components/ChcButton.vue";
import ChcModalConfirm from "$shared/components/ChcModalConfirm.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

defineOptions({
  inheritAttrs: false,
});

const restartUrl = "/home/v1/restart";

const toast = useToast();
const store = useStore();

const rebootLoading = ref(false);
const restartLoading = ref(false);
const debugLoading = ref(false);

const fetchServicesLoading = ref(false);
let restartServiceLoading = {};

const state = reactive({
  services: [],
});

const systemActionDisabled = computed(
  () => rebootLoading.value || restartLoading.value || debugLoading.value,
);

function reboot() {
  axios
    .post(
      `${restartUrl}/reboot`,
      {},
      {
        loading: rebootLoading,
        errorContext: "Failed to reboot system",
      },
    )
    .then(() => {
      toast.success("Reboot successful");
      store.dispatch("auth/logout").finally(sendToLogin);
    });
}

function restart() {
  axios
    .post(
      `${restartUrl}/restart`,
      {},
      {
        loading: restartLoading,
        errorContext: "Failed to restart system",
      },
    )
    .then(() => {
      toast.success("Restart successful");
      store.dispatch("auth/logout").finally(sendToLogin);
    });
}

function debug() {
  axios
    .post(
      `${restartUrl}/debug`,
      {},
      {
        loading: debugLoading,
        errorContext: "Failed to debug system",
      },
    )
    .then(() => {
      toast.success("Debug successful");
      store.dispatch("auth/logout").finally(sendToLogin);
    });
}

function fetchServices() {
  axios
    .get(`${restartUrl}/`, {
      loading: fetchServicesLoading,
      errorContext: "Failed to fetch services",
    })
    .then((response) => {
      state.services = response.data.services;

      restartServiceLoading = {};
      for (const service of state.services) {
        restartServiceLoading[service] = ref(false);
      }
    });
}

function restartService(service) {
  axios
    .post(
      `${restartUrl}/service/${service}`,
      {},
      {
        loading: restartServiceLoading[service],
        errorContext: `Failed to restart ${service}`,
      },
    )
    .then(() => {
      toast.success(`Successfuly restarted ${service}.`);
    });
}

fetchServices();
</script>

<style scoped>
.settings-view {
  margin-top: 2rem;
  margin-bottom: 1rem;
  display: grid;
  gap: 2rem;
}
.system-settings {
  display: flex;
  gap: 1rem;
}

.service-settings {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.service__container {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 15px;
}

.service__text {
  font-weight: 500;
  font-size: 18px;
  text-align: center;
}
</style>
