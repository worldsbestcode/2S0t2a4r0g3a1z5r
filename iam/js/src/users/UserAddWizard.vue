<template>
  <EditorWizard
    objType="user"
    :subType="props.type"
    :wizardPages="wizardPages"
  />
</template>

<script setup>
import EditorWizard from "@/components/EditorWizard.vue";
import BasicInfo from "@/users/BasicInfo.vue";
import UserAuth from "@/users/UserAuth.vue";
import UserRoles from "@/users/UserRoles.vue";

const props = defineProps({
  type: {
    type: String,
    default: "user",
  },
});

const wizardPages = [
  {
    name: "Basic Info",
    component: BasicInfo,
  },
  {
    name: props.type === "user" ? "Roles" : "Partitions",
    component: UserRoles,
  },
  {
    name: "Authentication",
    component: UserAuth,
  },
  {
    name: "Success",
    component: null,
  },
];
</script>
