<template>
  <div class="management-page">
    <header>
      <p>Generate Components</p>
      <close-button @click="$emit('close')" />
    </header>

    <nav>
      <button class="button" @click="showGenerateKeyComponents = true">
        Generate key components
      </button>
      <button
        class="button"
        :disabled="!pmkOrMfkLoadedResult"
        @click="showGenerateKeyFragments = true"
      >
        Generate key fragments
      </button>
    </nav>

    <modal-generate-key-components
      v-if="showGenerateKeyComponents"
      @closeModal="showGenerateKeyComponents = false"
    />
    <modal-generate-key-fragments
      v-if="showGenerateKeyFragments"
      @closeModal="showGenerateKeyFragments = false"
    />
  </div>
</template>

<script>
import CloseButton from "@/components/CloseButton.vue";

import ModalGenerateKeyComponents from "@/components/ModalGenerateKeyComponents.vue";
import ModalGenerateKeyFragments from "@/components/ModalGenerateKeyFragments.vue";

export default {
  components: {
    "close-button": CloseButton,
    "modal-generate-key-components": ModalGenerateKeyComponents,
    "modal-generate-key-fragments": ModalGenerateKeyFragments,
  },
  inject: ["getSessionId"],
  data: function () {
    return {
      showGenerateKeyComponents: false,
      showGenerateKeyFragments: false,
      pmkOrMfkLoadedResult: null,
    };
  },
  mounted: async function () {
    this.pmkOrMfkLoadedResult = await this.pmkOrMfkLoaded();
  },
  methods: {
    pmkOrMfkLoaded: async function () {
      let url = `/clusters/sessions/${this.getSessionId()}/major-keys`;
      let data = await this.$httpV2.get(url, {
        errorContextMessage: "Failed to get major key status",
      });
      let majorKeys = data.majorKeys;
      let pmk = majorKeys.find((x) => x.name === "PMK");
      let mfk = majorKeys.find((x) => x.name === "MFK");
      return pmk.loaded || mfk.loaded;
    },
  },
};
</script>

<style scoped>
nav {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  margin: 1rem;
  gap: 1rem;
}
</style>
