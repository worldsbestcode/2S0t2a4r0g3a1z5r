<template>
  <ChcInput
    v-model="name"
    hint="length 3-128"
    label="Name"
    placeholder="CryptoSpace name"
  />

  <ChcLabel div label="Justification">
    <div class="radio-container radio-container--two-col">
      <ChcRadio
        v-for="justification in justificationOptions"
        :key="justification"
        v-model="computedJustifications"
        type="checkbox"
        :label="justification"
        :value="justification"
      />
    </div>
  </ChcLabel>

  <ChcLabel div label="Permissions">
    <table class="permissions-table">
      <tr>
        <th class="permissions-table__th">Service Account</th>
        <td
          v-for="(apiPermission, humanPermission) in cryptospacePermissions"
          :key="apiPermission"
          class="permissions-table__td"
        >
          {{ humanPermission }}
        </td>
      </tr>

      <tr v-if="permissions.length === 0">
        <th
          class="permissions-table__th"
          style="text-align: center"
          :colspan="Object.keys(cryptospacePermissions).length + 1"
        >
          No Google Cloud service accounts found
        </th>
      </tr>
      <tr v-for="permission in permissions" :key="permission.accountUuid">
        <th class="permissions-table__th" :title="permission.accountName">
          {{ permission.accountName.split("@")[0] }}
        </th>
        <td
          v-for="apiPermission in cryptospacePermissions"
          :key="apiPermission"
          class="permissions-table__td"
        >
          <ChcRadio
            v-model="permission.perms"
            :value="apiPermission"
            no-container
            type="checkbox"
          />
        </td>
      </tr>
    </table>
  </ChcLabel>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import ChcRadio from "$shared/components/ChcRadio.vue";

import {
  cryptospacePermissions,
  justifications as justificationOptions,
} from "@/google.js";

const emit = defineEmits([
  "update:name",
  "update:justifications",
  "update:permissions",
]);

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  justifications: {
    type: Array,
    required: true,
  },
  permissions: {
    type: Object,
    required: true,
  },
});

const name = computed({
  get() {
    return props.name;
  },
  set(value) {
    emit("update:name", value);
  },
});
const computedJustifications = computed({
  get() {
    return props.justifications;
  },
  set(value) {
    emit("update:justifications", value);
  },
});
const permissions = computed({
  get() {
    return props.permissions;
  },
  set(value) {
    emit("update:permissions", value);
  },
});
</script>

<style scoped>
.permissions-table__th {
  font-weight: 500;
  font-size: 18px;
  padding: 0.25rem 0;
  padding-right: 1rem;
  border-right: 1px solid var(--border-color);
}

.permissions-table__td {
  font-size: 18px;
  padding: 0 1rem;
  text-align: center;
}
</style>
