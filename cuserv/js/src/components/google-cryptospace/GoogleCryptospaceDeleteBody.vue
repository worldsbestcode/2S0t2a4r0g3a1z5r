<template>
  <ModalDeleteBody
    axios-emit="updateCryptospaces"
    error="Failed to delete CryptoSpace"
    success="CryptoSpace deleted"
    :url="`/gekms/v1/cryptospaces/${props.cryptospaceUuid}`"
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
  cryptospaceUuid: {
    type: String,
    required: true,
  },
});

function afterDelete() {
  if (route.name === "cryptospace") {
    router.replace({ name: "cryptospaces" });
  }
}
</script>
