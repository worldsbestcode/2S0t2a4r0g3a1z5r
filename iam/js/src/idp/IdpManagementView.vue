<template>
  <LoadingSpinner v-if="loading" :loading="loading" />

  <br />

  <ChcTable :loading="loading" :searching="false" :paging="false">
    <!-- Top level buttons -->
    <template v-slot:buttons>
      <div class="button-row">
        <ChcButton
          img="/shared/static/element-plus.svg"
          @click="addLdapModal()"
        >
          ADD LDAP PROVIDER
        </ChcButton>
      </div>
      <div class="button-row">
        <ChcButton img="/shared/static/element-plus.svg" @click="addJwt()">
          ADD JWT PROVIDER
        </ChcButton>
      </div>
    </template>

    <!-- Table data -->
    <template v-slot:table>
      <!-- Header -->
      <thead>
        <tr>
          <th>Type</th>
          <th>Name</th>
          <th>Modified</th>
          <th>Manage</th>
        </tr>
      </thead>

      <tbody>
        <!-- Row per user in results -->
        <tr v-for="idp in state.tableData">
          <!-- Type -->
          <td>
            {{ idp.providerType }}
          </td>
          <td>
            {{ idp.name }}
          </td>
          <td>
            {{ idp.modified }}
          </td>
          <!-- Manage icons -->
          <td>
            <div class="icon-row">
              <div
                class="icon-button material-symbols-outlined table__link"
                @click="editIdp(idp.to, idp.uuid)"
              >
                edit
              </div>
              <div class="icon-button">
                <IdpDeleteModal :uuid="idp.uuid" />
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
import { onMounted, reactive, ref, watch, watchEffect } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

import ChcButton from "$shared/components/ChcButton.vue";
import LoadingSpinner from "$shared/components/LoadingSpinner.vue";

import ChcTable from "@/components/ChcTable.vue";
import IdpDeleteModal from "@/idp/IdpDeleteModal.vue";

const state = reactive({
  tableData: [],
  showModal: null,
});
const loading = ref(false);

function unixTimestampToLocalDate(unixTimestamp) {
  // Create a new Date object and set it to the Unix timestamp (in milliseconds)
  const date = new Date(unixTimestamp * 1000);

  // Extract the date components (year, month, day)
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are zero-based
  const day = String(date.getDate()).padStart(2, "0");

  // Assemble the local time format (YYYY-mm-dd)
  const localTimeFormat = `${year}-${month}-${day}`;

  return localTimeFormat;
}

// Initialize page of results
function fetchResults() {
  axios
    .get("/iam/v1/idp/stubs", {
      errorContext: "Failed to fetch identity providers",
      loading,
    })
    .then((response) => {
      let tableData = [];

      // Convert results to UI rows
      const results = response.data.results;
      for (let i in results) {
        const idp = results[i];

        let to = null;
        if (idp.providerType == "JWT") to = "idpJwt";
        else if (idp.providerType == "LDAP") to = "idpLdap";
        else continue;

        tableData.push({
          uuid: idp.uuid,
          name: idp.name,
          modified: unixTimestampToLocalDate(idp.modified),
          providerType: idp.providerType,
          to: to,
        });
      }

      state.tableData = tableData;
    });
}
watchEffect(fetchResults);
onMounted(() => {
  // Trigger load
  fetchResults();
});

const store = useStore();
watch(
  () => store.state.idp.dirty,
  (newDirty, oldDirty) => {
    if (newDirty) {
      store.dispatch("idp/undirty");
      fetchResults();
    }
  },
  { deep: true },
);

const router = useRouter();
function addJwt() {
  router.replace({
    name: "idpJwt",
    params: {
      uuid: "new",
    },
  });
}
function addLdapModal() {
  router.replace({
    name: "idpLdap",
    params: {
      uuid: "new",
    },
  });
}

function editIdp(to, uuid) {
  router.replace({
    name: to,
    params: {
      uuid: uuid,
    },
  });
}
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Two items per row */
  gap: 16px; /* Adjust the gap between items as needed */
}

.grid-item {
  /* Add styles for your grid items here */
  padding: 16px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
  text-decoration: none;
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  text-align: center; /* Center the text horizontally */
}
.icon-row {
  display: flex;
}
.icon-button {
  flex: 1;
}
</style>
