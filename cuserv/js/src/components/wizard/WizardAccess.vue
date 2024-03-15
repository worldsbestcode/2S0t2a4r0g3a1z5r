<template>
  <WizardPage title="Who has Access?" :loading="loading">
    <div class="access-container">
      <div class="access-results">
        <ChcLabel div label="Authorized Resources" center />
        <!-- todo: Stop this table from resizing/moving around! -->
        <table>
          <thead>
            <tr>
              <th class="access-results-name">Name</th>
              <th>Type</th>
              <th class="access-results-button"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in selected" :key="item.uuid">
              <td class="access-results-name access-results-name-td">
                {{ item.name }}
              </td>
              <td class="access-results-type-td">{{ item.type }}</td>
              <td class="access-results-button">
                <button
                  v-if="!principalRoles.some((x) => x.uuid === item.uuid)"
                  class="access-results-remove chc-link"
                  @click="selected.splice(index, 1)"
                >
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="access-seperator" />

      <WizardFuzzyInput
        v-model:selected="selected"
        center
        label="Add Additional Resources"
        hint="optional"
        :data="rolesAndIdentitiesArray"
        :display="(item) => `${item.name} - ${item.type}`"
        :keys="['name', 'type']"
        no-search-results="No roles or identites found"
        placeholder="Search role or identity"
      />
    </div>
  </WizardPage>
</template>

<script setup>
import axios from "axios";
import { computed, defineEmits, defineProps, reactive, ref } from "vue";
import { useStore } from "vuex";

import ChcLabel from "$shared/components/ChcLabel.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

import WizardFuzzyInput from "@/components/wizard/WizardFuzzyInput.vue";

const store = useStore();

const emit = defineEmits(["update:serviceAccess"]);

const props = defineProps({
  serviceAccess: {
    type: Array,
    required: true,
  },
});

const loading = ref(false);

const state = reactive({
  identities: [],
});

const selected = computed({
  get() {
    return props.serviceAccess;
  },
  set(value) {
    emit("update:serviceAccess", value);
  },
});

const controllableRoles = computed(() =>
  store.state.auth.managed_roles
    .filter((x) => x.type === "Controllable" && x.name !== "Anonymous")
    .map((x) => ({
      type: "Role",
      name: x.name,
      uuid: x.uuid,
    })),
);

const principalRoles = computed(() =>
  store.state.auth.roles.filter((x) => x.principal),
);

const rolesAndIdentitiesArray = computed(() => [
  ...controllableRoles.value,
  ...state.identities,
]);

function fetchIdentities() {
  axios
    .get("/cuserv/v1/users/identities", {
      params: {
        page: 1,
        pageSize: 100,
      },
      errorContext: "Failed to fetch identites",
      loading,
    })
    .then((response) => {
      state.identities = response.data.identities.map((x) => ({
        type: "Identity",
        name: x.name,
        uuid: x.uuid,
      }));
    });
}

function populatePrincipalRoles() {
  if (selected.value.length === 0) {
    selected.value = principalRoles.value.map((x) => ({
      type: "Role",
      name: x.name,
      uuid: x.uuid,
    }));
  }
}

fetchIdentities();
populatePrincipalRoles();
</script>

<style scoped>
.access-container {
  display: flex;
  gap: 72px;
  justify-content: center;
  margin: 0rem auto;
}

.access-seperator {
  width: 1px;
  background: var(--border-color);
}

.access-results-empty {
  height: 60px;
  display: flex;
  align-items: center;
  font-weight: 700;
  font-size: 18px;
  flex-grow: 1;
}

.access-results {
  text-align: left;
  flex-grow: 1;
}

.access-results table {
  width: 100%;
}

.access-results th {
  font-weight: 700;
}

.access-results th:nth-child(1) {
  width: 400px;
}

.access-results th:nth-child(2) {
  width: 120px;
}

.access-results thead tr {
  border-bottom: 1px solid;
}

/* should use .access-results tbody tr:not(:last-of-type) { */
.access-results tbody tr {
  border-bottom: 1px solid var(--border-color);
  height: 44px;
}

.access-results tbody tr:last-of-type {
  border-bottom: 0;
}

.access-results-name {
  padding-left: 1rem;
}

.access-results-button {
  padding-right: 1rem;
}

.access-results-name-td {
  padding-right: 4rem;
}

.access-results-type-td {
  padding-right: 4rem;
  color: var(--muted-text-color);
}

.access-results-remove {
  background: 0;
  padding: 0;
  border: 0;
}
</style>
