<template>
  <EditorWizard
    objType="role"
    :subType="props.type"
    :wizardPages="wizardPages"
  />
</template>

<script setup>
import EditorWizard from "@/components/EditorWizard.vue";
import AdvancedInfo from "@/roles/AdvancedInfo.vue";
import BasicInfo from "@/roles/BasicInfo.vue";
import ManagedRoles from "@/roles/ManagedRoles.vue";
import RolePerms from "@/roles/RolePerms.vue";
import ServicePermissions from "@/roles/ServicePermissions.vue";

const props = defineProps({
  type: {
    type: String,
    default: "user",
  },
});

const wizardPages =
  props.type === "user"
    ? [
        {
          name: "Basic Info",
          component: BasicInfo,
        },
        {
          name: "Service Permissions",
          component: ServicePermissions,
        },
        {
          name: "Permissions",
          component: RolePerms,
        },
        {
          name: "Managed Roles",
          component: ManagedRoles,
        },
        {
          name: "Advanced Info",
          component: AdvancedInfo,
        },
        {
          name: "Success",
          component: null,
        },
      ]
    : [
        {
          name: "Basic Info",
          component: BasicInfo,
        },
        {
          name: "Service Permissions",
          component: ServicePermissions,
        },
        {
          name: "Advanced Info",
          component: AdvancedInfo,
        },
        {
          name: "Success",
          component: null,
        },
      ];
</script>
