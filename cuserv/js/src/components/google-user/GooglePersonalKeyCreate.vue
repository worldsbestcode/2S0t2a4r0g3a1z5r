<template>
  <ModalAddNew title="Create Key" :body="GooglePersonalKeyCreateBody" />
</template>

<script setup>
import GooglePersonalKeyCreateBody from "@/components/google-user/GooglePersonalKeyCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
