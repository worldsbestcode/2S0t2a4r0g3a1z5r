<template>
  <ModalDeleteBody
    :url="`/gcse/v1/users/${props.userUuid}`"
    axios-emit="updateUsers"
    error="Failed to delete CSE User"
    success="CSE User deleted"
    @finished="afterDelete"
  />
</template>

<script setup>
import { defineProps } from "vue";
import { useRoute, useRouter } from "vue-router";

import ModalDeleteBody from "@/components/ModalDeleteBody.vue";

const route = useRoute();
const router = useRouter();

const props = defineProps({
  userUuid: {
    type: String,
    required: true,
  },
});

function afterDelete() {
  if (route.name === "googleUser") {
    router.replace({ name: "googleUsers" });
  }
}
</script>
