<template>
  <ModalAddNew
    :body="ClientAppEndpointCredentialCreateBody"
    title="Add Credential"
  />
</template>

<script setup>
import ClientAppEndpointCredentialCreateBody from "@/components/client-app/ClientAppEndpointCredentialCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
