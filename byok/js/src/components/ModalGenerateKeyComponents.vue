<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Generate Key Components</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul v-if="components.length === 0" class="wizard-page-list">
        <li>
          <span>Number of components to generate</span>
          <input
            v-model.number="numberOfComponents"
            class="input button-wide"
            type="number"
            min="2"
            max="12"
            step="1"
          />
        </li>
        <li>
          <span>Component type</span>
          <select v-model="type" class="button button-wide">
            <option :value="null">Select a key algorithm</option>
            <option v-for="type in symmetricTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </li>
      </ul>

      <div v-if="warn">
        <p class="proceed-text">
          You are about to display a clear component. Do you wish to proceed?
        </p>
      </div>

      <div v-if="components.length > 0 && !warn" class="component-result">
        <div>
          <div class="input component-text">
            <span
              v-for="(letter, i) in components[componentIndex].component"
              :key="i"
              >{{ hideComponentData ? "*" : letter }}</span
            >
          </div>
          <button
            class="button blue-button show-hide"
            @click="hideComponentData = !hideComponentData"
          >
            {{ hideComponentData ? "Show" : "Hide" }}
          </button>
        </div>
        <ul class="wizard-page-list">
          <li>
            Component number: <span>{{ componentIndex + 1 }}</span>
          </li>
          <li>
            Component checksum:
            <span class="checksum">{{ components[componentIndex].kcv }}</span>
          </li>
          <li>
            Key checksum:
            <span class="checksum">{{ componentsKeyChecksum }}</span>
          </li>
        </ul>
      </div>
    </template>
    <template #footer>
      <button
        v-if="componentIndex !== components.length - 1 && !warn"
        class="button icon-text-button"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-times" />
        Close
      </button>

      <button
        v-if="components.length === 0"
        :disabled="generateComponentsButtonDisabled"
        class="button blue-button"
        @click="handleGenerateComponents"
      >
        Generate components
      </button>

      <button v-if="warn" class="button blue-button" @click="warn = false">
        Proceed
      </button>

      <button
        v-if="
          components.length > 0 &&
          !warn &&
          componentIndex !== components.length - 1
        "
        class="button blue-button"
        @click="handleNextComponent"
      >
        Next component
      </button>

      <button
        v-if="componentIndex === components.length - 1 && !warn"
        class="button blue-button icon-text-button"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-check" />
        Finish
      </button>
    </template>
  </modal-base>
</template>

<script>
import "@/assets/wizard-page.css";
import ModalBase from "@/components/ModalBase.vue";
import { symmetricTypes } from "@/utils/models.js";

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      symmetricTypes,
      type: null,
      numberOfComponents: 2,
      components: [],
      componentsKeyChecksum: null,
      componentIndex: 0,
      warn: false,
      hideComponentData: true,
    };
  },
  computed: {
    generateComponentsButtonDisabled: function () {
      let numberOfComponents = parseInt(this.numberOfComponents);
      return !(
        numberOfComponents >= 2 &&
        numberOfComponents <= 12 &&
        symmetricTypes.includes(this.type)
      );
    },
  },
  methods: {
    handleGenerateComponents: function () {
      let url = `clusters/sessions/${this.getSessionId()}/keyblock/components`;
      let body = {
        numComponents: this.numberOfComponents,
        type: this.type,
      };
      this.$httpV2
        .post(url, body, {
          errorContextMessage: "Failed to generate key components",
        })
        .then((data) => {
          this.components = data.components;
          this.componentsKeyChecksum = data.kcv;
          this.warn = true;
        });
    },
    handleNextComponent: function () {
      this.hideComponentData = true;
      this.components[this.componentIndex] = null;
      this.componentIndex++;
      this.warn = true;
    },
  },
};
</script>

<style scoped>
.proceed-text {
  margin-bottom: 0;
}

.component-result {
  display: grid;
  grid-template-columns: 30% calc(70% - 1rem);
  grid-gap: 1rem;
  align-items: center;
}

.component-text {
  overflow-wrap: anywhere;
  font-family: monospace;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom: 0;
}

.component-text > span:nth-child(4n)::after {
  content: " ";
}

.show-hide {
  width: 100%;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
