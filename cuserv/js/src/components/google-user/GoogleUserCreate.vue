<template>
  <ModalAddNew title="Create Google User" :body="GoogleUserCreateBody" />
</template>

<script setup>
import GoogleUserCreateBody from "@/components/google-user/GoogleUserCreateBody.vue";
import ModalAddNew from "@/components/ModalAddNew.vue";
</script>
