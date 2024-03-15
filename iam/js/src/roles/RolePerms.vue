<template>
  <div v-for="(perm, index) in perms" :key="index">
    <ChcCheckBox v-model="perm.value" :label="perm.label" />
  </div>
</template>

<script setup>
import { computed, defineEmits, defineProps, ref } from "vue";
import { useStore } from "vuex";

import ChcComboBox from "$shared/components/ChcComboBox.vue";
import ChcInput from "$shared/components/ChcInput.vue";

import ChcCheckBox from "@/components/ChcCheckBox.vue";

const store = useStore();

function buildCompute(perm) {
  return computed({
    get() {
      return store.state.role.perms.includes(perm);
    },
    set(value) {
      if (value) {
        if (!store.state.role.perms.includes(perm)) {
          store.state.role.perms.push(perm);
        }
      } else {
        for (const i in store.state.role.perms) {
          if (store.state.role.perms[i] == perm) {
            store.state.role.perms.splice(i, 1);
            break;
          }
        }
      }
    },
  });
}

const perms = ref([
  {
    label: "Administration",
    value: buildCompute("Administration"),
  },
  {
    label: "Database",
    value: buildCompute("Database"),
  },
  {
    label: "Users",
    value: buildCompute("Users"),
  },
  {
    label: "Roles",
    value: buildCompute("Roles"),
  },
  {
    label: "Services",
    value: buildCompute("Services"),
  },
  {
    label: "Logs",
    value: buildCompute("Logs"),
  },
  {
    label: "Backup / Restore",
    value: buildCompute("BackupRestore"),
  },
  {
    label: "Reboot / Power",
    value: buildCompute("Reboot"),
  },
  {
    label: "HSMs",
    value: buildCompute("Hsms"),
  },
]);
</script>
