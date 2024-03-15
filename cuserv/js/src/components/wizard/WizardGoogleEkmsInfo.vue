<template>
  <WizardPage title="Google Cloud Service Accounts with Access">
    <ChcLabel div>
      <div
        v-for="(_, index) in serviceAccounts"
        :key="index"
        class="service-account__wrapper"
      >
        <ChcInput
          v-model="serviceAccounts[index]"
          :class="
            serviceAccounts.length > 1 && 'service-account__input--with-remove'
          "
          placeholder="service-{number}@gcp-sa-ekms.iam.gserviceaccount.com"
        />
        <button
          v-if="serviceAccounts.length > 1"
          class="service-account__remove"
          @click="serviceAccounts.splice(index, 1)"
        >
          <img
            class="service-account__remove-img"
            src="/shared/static/close.svg"
          />
        </button>
      </div>
    </ChcLabel>

    <ChcLabel div style="text-align: center">
      <ChcButton
        img="/shared/static/element-plus.svg"
        @click="addServiceAccount"
      >
        ADD SERVICE ACCOUNT
      </ChcButton>
    </ChcLabel>
  </WizardPage>
</template>

<script setup>
import { computed, defineEmits, defineProps } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import ChcInput from "$shared/components/ChcInput.vue";
import ChcLabel from "$shared/components/ChcLabel.vue";
import WizardPage from "$shared/components/wizard/WizardPage.vue";

const emit = defineEmits(["update:serviceAccounts"]);

const props = defineProps({
  serviceAccounts: {
    type: Array,
    required: true,
  },
});

const serviceAccounts = computed({
  get() {
    return props.serviceAccounts;
  },
  set(value) {
    emit("update:serviceAccounts", value);
  },
});

function addServiceAccount() {
  serviceAccounts.value.push("");
}

if (serviceAccounts.value.length === 0) {
  addServiceAccount();
}
</script>

<style scoped>
.service-account__wrapper {
  position: relative;

  width: min-content;
  margin: auto;
}

:deep(.service-account__input--with-remove) {
  /* 1rem: remove's right value  */
  /* 20px: remove's size/width */
  /* 0.5rem: a bit of padding */
  padding-right: calc(1rem + 20px + 0.5rem);
}
.service-account__remove {
  border: 0;
  background: 0;
  padding: 0;

  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 1rem;
}

.service-account__remove-img {
  display: block;
}
</style>
