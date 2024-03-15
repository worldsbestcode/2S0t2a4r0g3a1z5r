<template>
  <main class="app-main chc-main-horizontal-padding">
    <ChcWizardBreadContainer
      v-bind="$attrs"
      :crumbs="wizardCrumbs"
      :page-index="state.pageIndex"
    />

    <br />

    <component :is="props.wizardPages[state.pageIndex].component" />

    <ChcWizardButtonContainer
      v-model:pageIndex="state.pageIndex"
      :loading="loading"
      :wizard-pages-length="props.wizardPages.length"
      @deploy="finish"
    />
  </main>
</template>

<script setup>
import axios from "axios";
import { computed, defineProps, onMounted, reactive, ref } from "vue";
import { useStore } from "vuex";

import ChcWizardBreadContainer from "@/wizard/ChcWizardBreadContainer.vue";
import ChcWizardButtonContainer from "@/wizard/ChcWizardButtonContainer.vue";

const loading = ref(false);

const props = defineProps({
  uuid: {
    type: String,
    default: null,
  },
  objType: {
    type: String,
    required: true,
  },
  subType: {
    type: String,
    required: true,
  },
  wizardPages: {
    type: Array,
    required: true,
  },
});

const state = reactive({
  pageIndex: 0,
});

const wizardCrumbs = computed(() => {
  return props.wizardPages.map((x) => x.name);
});

function isNew() {
  return !props.uuid || props.uuid === "new";
}

const store = useStore();
onMounted(() => {
  if (!isNew()) store.dispatch(props.objType + "/load", props.uuid);
  else store.dispatch(props.objType + "/loadNew", props.subType);
});

function finish() {
  if (!isNew()) store.dispatch(props.objType + "/update");
  else store.dispatch(props.objType + "/add");
}
</script>
