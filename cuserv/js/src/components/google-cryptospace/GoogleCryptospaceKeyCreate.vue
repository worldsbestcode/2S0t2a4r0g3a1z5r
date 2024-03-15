<template>
  <ModalAddNew :body="GoogleCryptospaceKeyCreateBody" title="Create Key" />
</template>

<script setup>
import GoogleCryptospaceKeyCreateBody from "@/components/google-cryptospace/GoogleCryptospaceKeyCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
