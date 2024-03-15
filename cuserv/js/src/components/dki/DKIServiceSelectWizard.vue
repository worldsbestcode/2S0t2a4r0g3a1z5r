<template>
  <div v-if="wizardPages.length > 1" class="dki-wizard-bread-container">
    <WizardBreadCrumbs
      class="dki-wizard-bread-crumbs"
      :crumbs="wizardCrumbs"
      :page-index="state.pageIndex"
    />
  </div>

  <component
    :is="wizardPages[state.pageIndex].component"
    v-model:serviceUuid="state.serviceUuid"
    v-model:serviceName="state.serviceName"
    v-model:selectedKeySlots="state.selectedKeySlots"
    v-model:deviceGroupUuid="state.deviceGroupUuid"
    @serviceSelected="verifyServiceUuid"
  />
  <DKIWizardButtonContainer
    v-model:pageIndex="state.pageIndex"
    :wizard-pages-length="wizardPages.length"
    @deploy="continueToInjectionPage"
    @next="verifyServiceUuid"
  />
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, reactive } from "vue";
import { useToast } from "vue-toastification";

import DKIServiceKeyManagement from "@/components/dki/DKIServiceKeyManagement.vue";
import DKIServiceSelector from "@/components/dki/DKIServiceSelector.vue";
import DKIWizardButtonContainer from "@/components/dki/DKIWizardButtonContainer.vue";
import WizardBreadCrumbs from "@/components/wizard/WizardBreadCrumbs.vue";

const props = defineProps({
  serviceUuid: {
    type: String,
    required: false,
    default: "",
  },
  serviceName: {
    type: String,
    required: false,
    default: "",
  },
});
const toast = useToast();

const state = reactive({
  pageIndex: 0,
  serviceUuid: props.serviceUuid,
  serviceName: props.serviceName,
  selectedKeySlots: [],
  deviceGroupUuid: "",
});

const wizardPages = computed(() => {
  let pages = [];
  if (props.serviceUuid.length > 0) {
    pages = [
      {
        name: "Select Optional Keys",
        component: DKIServiceKeyManagement,
      },
    ];
  } else {
    pages = [
      {
        name: "Select Key Injection  Service",
        component: DKIServiceSelector,
      },
      {
        name: "Select Optional Keys",
        component: DKIServiceKeyManagement,
      },
    ];
  }
  return pages;
});

const wizardCrumbs = computed(() => {
  return wizardPages.value.map((x) => x.name);
});

function continueToInjectionPage() {
  if (state.serviceUuid.length == 0) {
    toast.error("Invalid service UUID.");
  } else if (state.selectedKeySlots.length === 0) {
    toast.error("No optional keys selected.");
  } else {
    axios
      .patch(
        `/dki/v1/device/${state.deviceGroupUuid}`,
        {
          keySlotRefs: state.selectedKeySlots,
        },
        {
          errorContext: "Failed to update device group",
        },
      )
      .then((response) => {
        if (response.status === 200) {
          window.location.href = "/dki/#/pedinject/" + state.serviceUuid;
        }
      });
  }
}

function verifyServiceUuid() {
  if (state.serviceUuid.length == 0) {
    toast.error(
      "No service selected. Please enter or scan service name/barcode",
    );
  } else {
    state.pageIndex++;
  }
}
</script>

<style scoped>
.dki-wizard-bread-crumbs {
  align-items: center;
}

.dki-wizard-bread-container {
  background: var(--secondary-background-color);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  /* match the header's left spacing? */
  margin: 2rem 16rem;
}
</style>
