<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Load Major Key</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul v-if="getSmartCardPin" class="wizard-page-list">
        <li>
          <span>Smart card PIN</span>
          <input
            v-model="smartCardPin"
            type="password"
            maxlength="8"
            class="input button-wide"
          />
        </li>
      </ul>

      <button
        v-if="!getSmartCardPin && !smartCardLoadData"
        :disabled="loadSmartCardButtonPressed"
        class="button blue-button load-fragment"
        @click="handleLoadSmartCard"
      >
        Load fragment from smart card
      </button>

      <ul v-if="smartCardLoadData">
        <li>
          Loaded {{ smartCardLoadData.have }} /
          {{ smartCardLoadData.want }} smart card fragments
        </li>
        <li v-if="smartCardLoadData.kcv">
          Major key checksum
          <span class="checksum">{{ smartCardLoadData.kcv }}</span>
        </li>
        <li>
          Smart card fragment key checksum:
          <span class="checksum">{{ smartCardLoadData.partKcv }}</span>
        </li>
      </ul>
    </template>
    <template #footer>
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>

      <button
        v-if="getSmartCardPin"
        :disabled="smartCardPin.length !== 8"
        class="button blue-button icon-text-button"
        @click="handleSmartCardPin"
      >
        <i class="fa fa-check" />
        Login
      </button>
    </template>
  </modal-base>
</template>

<script>
import ModalBase from "@/components/ModalBase.vue";

export default {
  components: {
    "modal-base": ModalBase,
  },
  inject: ["getSessionId"],
  props: {
    majorKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      getSmartCardPin: true,
      smartCardPin: "",
      loadSmartCardButtonPressed: false,
      smartCardLoadData: null,
    };
  },
  methods: {
    handleSmartCardPin: async function () {
      let { success, msg } = await window.fxctx.keys.smartCardPINLogin(
        this.smartCardPin,
      );
      if (success) {
        this.getSmartCardPin = false;
      } else {
        this.$bus.emit("toaster", { message: msg });
      }
    },

    handleLoadSmartCard: async function () {
      this.loadSmartCardButtonPressed = true;

      let {
        success,
        value: fragment,
        msg,
      } = await window.fxctx.keys.smartCardGetFragment();

      if (!success) {
        this.$bus.emit("toaster", { message: msg });
        this.$emit("closeModal");
        return;
      }

      let url = `/clusters/sessions/${this.getSessionId()}/major-keys/${
        this.majorKey.name
      }/partial-key-load`;
      let body = {
        input: {
          fragment: fragment,
          encrypted: true,
        },
      };

      this.$httpV2
        .post(url, body, {
          errorContextMessage:
            "Failed to load smart card fragment to major key",
        })
        .then((data) => {
          this.smartCardLoadData = data;
          this.$emit("refreshMajorKeys");
        })
        .catch(() => {
          this.$emit("closeModal");
          this.$emit("refreshMajorKeys");
        });
    },
  },
};
</script>

<style scoped>
.load-fragment {
  display: block;
  margin: auto;
  height: 4rem;
}
</style>
