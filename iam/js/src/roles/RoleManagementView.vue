<template>
  <LoadingSpinner v-if="loading" :loading="loading" />
  <ChcTable
    :loading="loading"
    v-model:page="state.page"
    v-model:totalPages="state.totalPages"
    v-model:pageSize="state.pageSize"
    v-model:search="state.search"
    v-model:archive="state.archive"
    :hasArchive="true"
  >
    <!-- Top level buttons -->
    <template v-slot:buttons>
      <div class="button-row">
        <ChcButton img="/shared/static/element-plus.svg" @click="addModal()">
          ADD
        </ChcButton>
      </div>
    </template>

    <!-- Table data -->
    <template v-slot:table>
      <!-- Header -->
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Storage</th>
          <th>{{ props.type === "users" ? "Services" : "Permissions" }}</th>
          <th>Manage</th>
        </tr>
      </thead>

      <tbody>
        <!-- Row per user in results -->
        <tr v-for="role in state.tableData">
          <!-- Name -->
          <td>
            {{ role.name }}
          </td>
          <!-- Principal -->
          <td>
            {{ role.roleType }}
          </td>
          <!-- Storage -->
          <td>
            <div class="row-buddies">
              <span class="material-symbols-outlined">
                <template v-if="role.storage === 'HSM'">lock</template>
                <template v-else>language</template>
              </span>
              {{ role.storage }}
            </div>
          </td>
          <!-- Number permissions -->
          <td>
            {{ role.permCount }}
          </td>
          <!-- Manage icons -->
          <td>
            <div class="icon-row">
              <div class="icon-button" v-if="!role.archive">
                <BasicInfoModal :uuid="role.uuid" />
              </div>
              <div class="icon-button" v-if="!role.archive">
                <ServicePermissionsModal :uuid="role.uuid" />
              </div>
              <div
                class="icon-button"
                v-if="!role.archive && props.type === 'users'"
              >
                <RolePermsModal :uuid="role.uuid" />
              </div>
              <div
                class="icon-button"
                v-if="props.type === 'users' && !role.archive"
              >
                <ManagedRolesModal :uuid="role.uuid" />
              </div>
              <div class="icon-button" v-if="!role.archive">
                <AdvancedInfoModal :uuid="role.uuid" />
              </div>
              <div class="icon-button" v-if="role.archive">
                <RoleUnarchiveModal :uuid="role.uuid" />
              </div>
              <div class="icon-button">
                <RoleDeleteModal :uuid="role.uuid" />
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </template>
  </ChcTable>
</template>

<script setup>
import axios from "axios";
import { defineProps, onMounted, reactive, ref, watch, watchEffect } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcToggleSwitch from "$shared/components/ChcToggleSwitch.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import ChcTable from "@/components/ChcTable.vue";
import AdvancedInfoModal from "@/roles/AdvancedInfoModal.vue";
import BasicInfoModal from "@/roles/BasicInfoModal.vue";
import ManagedRolesModal from "@/roles/ManagedRolesModal.vue";
import RoleDeleteModal from "@/roles/RoleDeleteModal.vue";
import RolePermsModal from "@/roles/RolePermsModal.vue";
import RoleUnarchiveModal from "@/roles/RoleUnarchiveModal.vue";
import ServicePermissionsModal from "@/roles/ServicePermissionsModal.vue";

const props = defineProps({
  type: {
    type: String,
    default: "users",
  },
});

const state = reactive({
  page: 1,
  pageSize: 25,
  totalPages: 1,
  search: "",
  tableData: [],
  showModal: null,
  archive: false,
});
const loading = ref(false);
const store = useStore();

// Initialize page of results
function fetchResults() {
  axios
    .get("/kmes/v8/roles", {
      params: {
        page: state.page,
        pageCount: state.pageSize,
        search: state.search,
        application: props.type === "apps",
        archive: state.archive,
      },
      errorContext: "Failed to fech roles",
      loading,
    })
    .then((response) => {
      state.page = response.data.response.currentPage;
      state.totalPages = response.data.response.totalPages;
      let tableData = [];

      // Convert results to UI rows
      const results = response.data.response.roles;
      for (let i in results) {
        const role = results[i];

        tableData.push({
          uuid: role.uuid,
          name: role.name,
          permCount: props.type === "apps" ? role.permCount : role.serviceCount,
          roleType: role.principal ? "Principal" : "Auxiliary",
          storage: role.hardened ? "HSM" : "Application",
          archive: role.archive,
        });
      }

      state.tableData = tableData;
    });
}
watchEffect(fetchResults);
onMounted(() => {
  // Trigger load
  state.page = 1;
});

watch(
  () => store.state.role.dirty,
  (newDirty, oldDirty) => {
    if (newDirty) {
      store.dispatch("role/undirty");
      fetchResults();
    }
  },
  { deep: true },
);

const router = useRouter();
function addModal() {
  router.replace({
    name: props.type === "users" ? "userRoleAdd" : "appRoleAdd",
    params: {
      user: props.type === "users",
    },
  });
}
</script>

<style scoped>
.content {
  display: flex;
  align-self: center;
  flex-direction: column;
}

.type-toggle-box {
  display: flex;
  flex-direction: column;
  align-items: center; /* Center items horizontally */
  justify-content: center; /* Center items vertically */
}

.row-buddies {
  display: flex;
}

.button-row {
  text-align: right;
  padding: 10px;
  display: inline-block;
}

.icon-row {
  display: flex;
}
.icon-button {
  flex: 1;
}
</style>
