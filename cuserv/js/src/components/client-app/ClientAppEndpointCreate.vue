<template>
  <ModalAddNew :body="ClientAppEndpointsCreateBody" title="Add Endpoint" />
</template>

<script setup>
import ClientAppEndpointsCreateBody from "@/components/client-app/ClientAppEndpointCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
