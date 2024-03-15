<template>
  <EditorWizard objType="idp" subType="JWT" :wizardPages="wizardPages" />
</template>

<script setup>
import EditorWizard from "@/components/EditorWizard.vue";
import Advanced from "@/idp/jwt/Advanced.vue";
import Auth from "@/idp/jwt/Auth.vue";
import BasicInfo from "@/idp/jwt/BasicInfo.vue";
import Claims from "@/idp/jwt/Claims.vue";
import IdentityInfo from "@/idp/jwt/IdentityInfo.vue";

const wizardPages = [
  {
    name: "Basic Info",
    component: BasicInfo,
  },
  {
    name: "Authentication",
    component: Auth,
  },
  {
    name: "Identity Info",
    component: IdentityInfo,
  },
  {
    name: "Claims",
    component: Claims,
  },
  {
    name: "Advanced",
    component: Advanced,
  },
  {
    name: "Success",
    component: null,
  },
];
</script>
