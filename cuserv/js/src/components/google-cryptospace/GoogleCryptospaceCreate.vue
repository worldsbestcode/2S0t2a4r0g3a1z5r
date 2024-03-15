<template>
  <ModalAddNew :body="GoogleCryptospaceCreateBody" title="Create CryptoSpace" />
</template>

<script setup>
import GoogleCryptospaceCreateBody from "@/components/google-cryptospace/GoogleCryptospaceCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
