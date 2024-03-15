<template>
  <div>
    <component :is="injectedComponent" />

    <p v-if="showSubmit" class="wizard-page-icon-text-button">
      <span> Press submit to finish the wizard. </span>
      <span>
        <loading-spinner class="loading-spinner" :loading="loading" />
        <button
          class="button blue-button"
          :disabled="disableSubmitButton"
          @click="handleSubmitClick"
        >
          Submit
        </button>
      </span>
    </p>

    <p v-if="showSuccess" class="wizard-page-icon-text-button">
      <span>
        <i class="fa fa-check fa-2x" />
        {{ successText }}
      </span>
      <button class="button blue-button" @click="$bus.emit('wizardClose')">
        Finish
      </button>
    </p>

    <p v-if="showFail" class="wizard-page-icon-text-button">
      <span>
        <i class="fa fa-times fa-2x" />
        {{ failText }}
      </span>
      <button class="button blue-button" @click="$bus.emit('wizardClose')">
        Finish
      </button>
    </p>
  </div>
</template>

<script>
import LoadingSpinner from "@/components/LoadingSpinner.vue";

export default {
  title: "Submit",
  components: {
    "loading-spinner": LoadingSpinner,
  },
  data: function () {
    return {
      showSubmit: true,
      showSuccess: false,
      showFail: false,
      successText: "",
      failText: "",
      disableSubmitButton: false,
      injectedComponent: null,
      loading: false,
    };
  },
  methods: {
    handleSuccess: function (text, component) {
      this.showSubmit = false;
      this.showSuccess = true;
      this.loading = false;
      this.successText = text;
      this.injectedComponent = component;
    },
    handleFail: function (text, component) {
      this.showSubmit = false;
      this.showFail = true;
      this.loading = false;
      this.failText = text;
      this.injectedComponent = component;
    },
    handleSubmitClick: function () {
      this.disableSubmitButton = true;
      this.loading = true;
      this.$emit("wizardSubmit", this.handleSuccess, this.handleFail);
    },
  },
};
</script>

<style scoped>
.wizard-page-icon-text-button {
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  margin-bottom: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text-color-blue-lighter);
}

.wizard-page-icon-text-button > span {
  display: flex;
  align-items: center;
}

.wizard-page-icon-text-button > span > i {
  margin-right: 0.5rem;
}

.loading-spinner {
  margin-right: 1rem;
}
</style>
