<template>
  <ChcToggle v-model="whitelisted" label="User Enabled" />

  <ChcInput v-model="name" label="User Name" placeholder="User name" />

  <ChcInput
    disabled
    label="User Email"
    :placeholder="email ? email : `john.doe@${emailDomain}`"
  />
</template>

<script setup>
import { computed, defineEmits, defineProps, inject } from "vue";

import ChcInput from "$shared/components/ChcInput.vue";
import ChcToggle from "$shared/components/ChcToggle.vue";

const emit = defineEmits(["update:name", "update:email", "update:whitelisted"]);

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
  whitelisted: {
    type: Boolean,
    required: true,
  },
});

const serviceData = inject("serviceData");

const emailDomain = computed(() => {
  const emailDomainConfig = serviceData.value.config.find(
    (x) => x.key === "Email Domain",
  );
  return emailDomainConfig.value;
});

const name = computed({
  get() {
    return props.name;
  },
  set(value) {
    emit("update:name", value);

    if (value) {
      email.value = `${value}@${emailDomain.value}`;
    } else {
      email.value = "";
    }
  },
});
const email = computed({
  get() {
    return props.email;
  },
  set(value) {
    emit("update:email", value);
  },
});
const whitelisted = computed({
  get() {
    return props.whitelisted;
  },
  set(value) {
    emit("update:whitelisted", value);
  },
});
</script>
