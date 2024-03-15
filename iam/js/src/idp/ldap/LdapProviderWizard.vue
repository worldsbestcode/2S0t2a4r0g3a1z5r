<template>
  <EditorWizard objType="idp" subType="LDAP" :wizardPages="wizardPages" />
</template>

<script setup>
import EditorWizard from "@/components/EditorWizard.vue";
import AdminLogin from "@/idp/ldap/AdminLogin.vue";
import Advanced from "@/idp/ldap/Advanced.vue";
import BasicInfo from "@/idp/ldap/BasicInfo.vue";
import Lookup from "@/idp/ldap/Lookup.vue";
import Server from "@/idp/ldap/Server.vue";

const wizardPages = [
  {
    name: "Basic Info",
    component: BasicInfo,
  },
  {
    name: "Server",
    component: Server,
  },
  {
    name: "Admin Login",
    component: AdminLogin,
  },
  {
    name: "Lookup",
    component: Lookup,
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
