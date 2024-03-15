<template>
  <!-- Add new roles -->
  <ChcFuzzyInput
    v-model:selected="state.selectedRoles"
    :data="state.pendingRoles"
    :display="(item) => `${item.name} - ${item.roleType}`"
    :keys="['name', 'roleType']"
    no-search-results="No roles found"
    placeholder="Search role"
  />

  <!-- Managed roles -->
  <ChcTable :loading="loading" :paging="false" :searching="false">
    <!-- Table data -->
    <template v-slot:table>
      <!-- Header -->
      <thead>
        <tr>
          <th>Role</th>
          <th>Type</th>
          <th>Storage</th>
          <th>Remove</th>
        </tr>
      </thead>

      <tbody>
        <!-- Row per assigned role -->
        <tr v-for="(role, index) in state.subRoles" :key="role.name">
          <!-- Name -->
          <td>
            {{ role.name }}
          </td>
          <!-- Type -->
          <td>
            {{ role.roleType }}
          </td>
          <!-- Storage -->
          <!-- TODO: Component -->
          <td>
            <div class="row-buddies">
              <span class="material-symbols-outlined">
                <template v-if="role.hardened">lock</template>
                <template v-else>language</template>
              </span>
              {{ role.hardened ? "HSM" : "Application" }}
            </div>
          </td>
          <!-- Remove -->
          <td>
            <button
              class="access-results-remove chc-link"
              @click="removeRole($event, role)"
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
import { defineEmits, defineProps, onMounted, reactive, ref, watch } from "vue";
import { useStore } from "vuex";

import ChcFuzzyInput from "@/components/ChcFuzzyInput.vue";
import ChcTable from "@/components/ChcTable.vue";

const state = reactive({
  subRoles: [], // name, roleType, hardened
  pendingRoles: [],
  selectedRoles: [],
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

function getRoleType(uuid) {
  for (let i in store.state.managedRoles.managedRoles) {
    const role = store.state.managedRoles.managedRoles[i];
    if (role.uuid == uuid) return role.roleType;
  }
  for (let i in store.state.auth.roles) {
    const role = store.state.auth.roles[i];
    if (role.uuid == uuid) {
      if (role.principal) return "Principal";
      else return "Auxiliary";
    }
  }

  return "Unmanaged"; // TODO: Roles i cant view
}

function getRole(uuid) {
  for (const i in store.state.managedRoles.managedRoles) {
    const role = store.state.managedRoles.managedRoles[i];
    if (role.uuid == uuid) return role;
  }
  return null;
}

function removeRole(event, role) {
  event.preventDefault(); // prevents click from closing results
  state.pendingRoles.push(role);
  for (let i in state.subRoles) {
    const activeRole = state.subRoles[i];
    if (activeRole.uuid == role.uuid) {
      state.subRoles.splice(i, 1);
      break;
    }
  }
  store.dispatch("role/removeRole", role.uuid);
}

function addRole(role) {
  state.subRoles.push(role);
  for (let i in state.pendingRoles) {
    const pendingRole = state.pendingRoles[i];
    if (pendingRole.uuid == role.uuid) {
      state.pendingRoles.splice(i, 1);
      break;
    }
  }
  store.dispatch("role/addRole", role.uuid);
}

// When roles are set, initialize possible values
const store = useStore();
const initRoles = () => {
  // Initialize active roles
  state.subRoles = [];
  const usedRoleUuids = [];
  for (let i in store.state.role.subRoles) {
    let role = getRole(store.state.role.subRoles[i]);
    if (usedRoleUuids.includes(role.uuid)) continue;
    if (role.name == "Anonymous") continue;
    if (role.name == "CryptoHub Central App") continue;
    role.roleType = getRoleType(role.uuid);
    state.subRoles.push(role);
    usedRoleUuids.push(role.uuid);
  }
  // Initialize pending roles
  state.pendingRoles = [];
  for (let i in store.state.managedRoles.managedRoles) {
    const role = store.state.managedRoles.managedRoles[i];
    if (usedRoleUuids.includes(role.uuid)) continue;
    if (role.managedType != "Controllable") continue;
    if (role.hardened && !store.state.role.hardened) continue;
    if (role.management != store.state.role.management) continue;
    if (role.name == "Anonymous") continue;
    if (state.selectedRoles.includes(role.uuid)) state.subRoles.push(role);
    else state.pendingRoles.push(role);
    usedRoleUuids.push(role.uuid);
  }
};
watch(() => store.state.role.loaded, initRoles, { deep: true });
onMounted(initRoles);

watch(
  state.selectedRoles,
  (value) => {
    for (const i in value) addRole(value[i]);
    state.selectedRoles.pop();
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
