<template>
  <ModalAddNew
    :body="ServiceAccountCreateBody"
    title="Create Google Cloud Service Account"
  />
</template>

<script setup>
import ServiceAccountCreateBody from "@/components/google/ServiceAccountCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
