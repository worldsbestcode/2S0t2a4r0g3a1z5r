<template>
  <div :class="textInfoColor">
    {{ textInfo }}
  </div>

  <div class="fx-icon-container">
    <v-icon :color="iconColor" :icon="icon"></v-icon>
    <v-progress-circular
      v-if="icon === 'mdi-progress-circular'"
      indeterminate
      :color="iconColor"
      :size="25"
    ></v-progress-circular>
  </div>
</template>

<script setup>
import { eInjectionStatus } from "@/utils/common";
import { defineProps, onBeforeMount, ref, watch, computed } from "vue";
import BigInt from "big-integer";
import store from "@/store";

const props = defineProps({
  terminalId: {
    type: BigInt,
    required: true,
  },
});

let iconColor = ref("");
let textInfoColor = ref("");
let textInfo = ref("");
let icon = ref("");

const injectionStatusMap = computed(
  () => store.getters["pedinject/getInjectionStatusMap"],
);

watch(injectionStatusMap, (updatedStatusMap) => {
  const injectionResult = updatedStatusMap[props.terminalId];
  if (injectionResult === undefined) {
    return;
  }

  updateIcon(injectionResult);
  updateTextInfo(injectionResult);
});

function updateIcon(injectionResult) {
  switch (injectionResult.status) {
    case eInjectionStatus.Failed:
      icon.value = "mdi-alert-outline";
      iconColor.value = "red";
      break;
    case eInjectionStatus.Finished:
      icon.value = "mdi-checkbox-marked-circle";
      iconColor.value = "success";
      break;
    case eInjectionStatus.Running:
      icon.value = "mdi-progress-circular";
      iconColor.value = "info";
      break;
    default:
      icon.value = "";
      break;
  }
}

function updateTextInfo(injectionResult) {
  switch (injectionResult.status) {
    case eInjectionStatus.Failed:
      textInfo.value = "Injection Failed"; //injectionResult.message;

      if (injectionResult.message === null) {
        textInfo.value = "Device Injection Failed: Internal Error";
      }

      textInfoColor.value = "text-red";
      break;
    case eInjectionStatus.Finished:
      textInfo.value = "Device Injected";
      textInfoColor.value = "text-success";
      break;
    case eInjectionStatus.Running:
      textInfo.value = "Injecting Device";
      textInfoColor.value = "text-info";
      break;
    default:
      textInfo.value = "";
      break;
  }
}

onBeforeMount(() => {
  const injectionStatus =
    store.getters["pedinject/getInjectionStatusMap"][props.terminalId];
  //initialize injection status
  if (injectionStatus === undefined) {
    store.commit("pedinject/setInjectionStatus", {
      deviceId: props.terminalId,
      result: {
        status: eInjectionStatus.None,
        message: "",
      },
    });
  } else {
    updateIcon(injectionStatus);
    updateTextInfo(injectionStatus);
  }
});
</script>

<style scoped>
.fx-icon-container {
  margin-left: auto;
  margin-right: 0.5rem;
}
</style>
