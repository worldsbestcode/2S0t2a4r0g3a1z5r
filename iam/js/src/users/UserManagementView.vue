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
          <th>&nbsp;</th>
          <th v-if="props.type === 'users'">Name</th>
          <th>{{ props.type === "users" ? "Username" : "Name" }}</th>
          <th>Last Login</th>
          <th>Storage</th>
          <th>{{ props.type === "users" ? "Roles" : "Roles/Services" }}</th>
          <th>Manage</th>
        </tr>
      </thead>

      <tbody>
        <!-- Row per user in results -->
        <tr v-for="user in state.tableData">
          <!-- Locked indicator -->
          <td @click="toggleLocked(user)">
            <div
              v-if="user.locked"
              class="locked-circle"
              style="background-color: red"
            ></div>
            <div
              v-else
              class="locked-circle"
              style="background-color: green"
            ></div>
          </td>
          <!-- Friendly name -->
          <td v-if="props.type === 'users'">
            {{ user.name }}
          </td>
          <!-- Username -->
          <td>
            {{ user.username }}
          </td>
          <!-- Last login -->
          <td>
            {{ user.lastLogin }}
          </td>
          <!-- Storage -->
          <td>
            <div class="row-buddies">
              <span class="material-symbols-outlined">
                <template v-if="user.storage == 'HSM'">lock</template>
                <template v-else>language</template>
              </span>
              {{ user.storage }}
            </div>
          </td>
          <!-- Roles -->
          <td>
            {{ user.roles.join("\n") }}
          </td>
          <!-- Manage icons -->
          <td>
            <div class="icon-row">
              <div class="icon-button">
                <BasicInfoModal :uuid="user.uuid" />
              </div>
              <div class="icon-button">
                <UserRolesModal
                  :uuid="user.uuid"
                  :users="props.type === 'users'"
                />
              </div>
              <div class="icon-button">
                <UserAuthModal :uuid="user.uuid" />
              </div>
              <div class="icon-button">
                <UserDeleteModal :uuid="user.uuid" />
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
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import ChcTable from "@/components/ChcTable.vue";
import BasicInfoModal from "@/users/BasicInfoModal.vue";
import UserAuthModal from "@/users/UserAuthModal.vue";
import UserDeleteModal from "@/users/UserDeleteModal.vue";
import UserRolesModal from "@/users/UserRolesModal.vue";

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

// Initialize page of results
function fetchResults() {
  axios
    .get("/kmes/v8/identities", {
      params: {
        page: state.page,
        pageCount: state.pageSize,
        search: state.search,
        application: props.type === "apps",
        archive: state.archive,
      },
      errorContext: "Failed to fetch identities",
      loading,
    })
    .then((response) => {
      state.page = response.data.response.currentPage;
      state.totalPages = response.data.response.totalPages;
      let tableData = [];

      // Convert results to UI rows
      const results = response.data.response.identities;
      for (let i in results) {
        let identity = results[i];

        let roles = [];
        for (let j in identity.roles) {
          roles.push(identity.roles[j].name);
        }

        tableData.push({
          uuid: identity.uuid,
          locked: identity.locked || identity.archive,
          name: identity.name,
          username: identity.username,
          lastLogin: identity.lastLogin,
          storage: identity.hardened ? "HSM" : "Application",
          roles: roles,
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

const store = useStore();
watch(
  () => store.state.user.dirty,
  (newDirty, oldDirty) => {
    if (newDirty) {
      store.dispatch("user/undirty");
      fetchResults();
    }
  },
  { deep: true },
);

async function toggleLocked(user) {
  try {
    store.dispatch("user/lockunlock", user);
  } catch (error) {
    // axios will send error toast
  }
}

const router = useRouter();
function addModal() {
  router.replace({
    name: props.type === "users" ? "userAdd" : "appAdd",
    params: {
      type: props.type,
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

.locked-circle {
  cursor: pointer;
  width: 20px;
  height: 20px;
  border-radius: 50%; /* Makes the element a circle */
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
