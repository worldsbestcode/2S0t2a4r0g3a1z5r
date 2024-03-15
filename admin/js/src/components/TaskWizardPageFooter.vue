<template>
  <WizardPageFooter>
    <div class="playlist-buttons-container">
      <template v-if="playlist">
        <ChcButton v-if="previousPage" secondary @click="previousPage">
          Back
        </ChcButton>
      </template>
      <ChcButton v-else secondary @click="$router.replace('./')">
        Cancel
      </ChcButton>
    </div>

    <div class="playlist-buttons-container">
      <slot name="footer" />
    </div>

    <div class="playlist-buttons-container">
      <ChcButton v-if="playlist" secondary @click="skip">Skip</ChcButton>
      <ChcButton v-bind="$attrs">
        <span v-if="playlist">Continue</span>
        <span v-else>Finish</span>
      </ChcButton>
    </div>
  </WizardPageFooter>
</template>

<script setup>
import { defineOptions, inject } from "vue";

import ChcButton from "$shared/components/ChcButton.vue";
import WizardPageFooter from "$shared/components/wizard/WizardPageFooter.vue";

import { usePlaylist } from "@/composables";

defineOptions({
  inheritAttrs: false,
});

const playlist = usePlaylist();

const previousPage = inject("previousPage");
const skip = inject("skip");
</script>

<style scoped>
.playlist-buttons-container {
  display: flex;
  gap: 1rem;
}
</style>
