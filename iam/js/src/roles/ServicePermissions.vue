<template>
  <!-- Add new Services -->
  <ChcFuzzyInput
    v-model:selected="state.selectedService"
    :data="state.pendingServices"
    :display="(item) => `${item.name}`"
    :keys="['name', 'uuid', 'hardened']"
    no-search-results="No services found"
    placeholder="Search services"
  />

  <!-- Permissible services -->
  <ChcTable :loading="loading" :paging="false" :searching="false">
    <!-- Table data -->
    <template v-slot:table>
      <!-- Header -->
      <thead>
        <tr>
          <th>Service</th>
          <th>Storage</th>
          <th>Remove</th>
        </tr>
      </thead>

      <tbody>
        <!-- Row per assigned role -->
        <tr
          v-for="(service, index) in state.activeServices"
          :key="service.name"
        >
          <!-- Name -->
          <td>
            {{ service.name }}
          </td>
          <!-- Storage -->
          <td>
            <div class="row-buddies">
              <span class="material-symbols-outlined">
                <template v-if="service.hardened">lock</template>
                <template v-else>language</template>
              </span>
              {{ service.hardened ? "HSM" : "Application" }}
            </div>
          </td>
          <!-- Remove -->
          <td>
            <button
              class="access-results-remove chc-link"
              @click="removeService($event, service)"
            >
              Remove
            </button>
          </td>
        </tr>
      </tbody>
    </template>
  </ChcTable>
  <br />
</template>

<script setup>
import axios from "axios";
import {
  computed,
  defineEmits,
  defineProps,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";
import { useStore } from "vuex";

import ChcFuzzyInput from "@/components/ChcFuzzyInput.vue";
import ChcTable from "@/components/ChcTable.vue";

const state = reactive({
  activeServices: [], // uuid, name, hardened
  pendingServices: [],
  selectedService: [],
});

const props = defineProps({
  uuid: {
    type: String,
    default: "",
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

function getServiceInfo(uuid) {
  for (const i in store.state.managedRoles.managedServices) {
    const service = store.state.managedRoles.managedServices[i];
    if (service.uuid == uuid) return service;
  }
  return null;
}

function removeService(event, service) {
  event.preventDefault(); // prevents click from closing results
  state.pendingServices.push(service);
  for (let i in state.activeServices) {
    const activeService = state.activeServices[i];
    if (activeService.uuid == service.uuid) {
      state.activeServices.splice(i, 1);
      break;
    }
  }
  store.dispatch("role/removeService", service.uuid);
}

function addService(service) {
  state.activeServices.push(service);
  for (let i in state.pendingServices) {
    const pendingService = state.pendingServices[i];
    if (pendingService.uuid == service.uuid) {
      state.pendingServices.splice(i, 1);
      break;
    }
  }
  store.dispatch("role/addService", service.uuid);
}

// When services are set, initialize possible values
const store = useStore();
const initServices = () => {
  state.activeServices = [];
  const usedUuids = [];
  for (let i in store.state.role.services) {
    const service = getServiceInfo(store.state.role.services[i]);
    if (!service) continue;
    if (usedUuids.includes(service.uuid)) continue;
    state.activeServices.push(service);
    usedUuids.push(service.uuid);
  }
  // Initialize pending roles
  state.pendingServices = [];
  for (let i in store.state.managedRoles.managedServices) {
    const service = store.state.managedRoles.managedServices[i];
    if (usedUuids.includes(service.uuid)) continue;
    if (service.hardened && !store.state.role.hardened) continue;
    if (state.selectedService.includes(service.uuid))
      state.activeServices.push(service);
    else state.pendingServices.push(service);
    usedUuids.push(service.uuid);
  }
};
watch(() => store.state.role.loaded, initServices, { deep: true });
watch(() => store.state.role.hardened, initServices, { deep: true });
onMounted(initServices);

watch(
  state.selectedService,
  (value) => {
    for (const i in value) addService(value[i]);
    state.selectedService.pop();
  },
  { deep: true },
);
</script>

<style scoped>
.access-results-remove {
  background: 0;
  padding: 0;
  border: 0;
}
</style>
