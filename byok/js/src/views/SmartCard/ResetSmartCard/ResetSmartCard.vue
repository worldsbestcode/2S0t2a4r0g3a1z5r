<template>
  <div>
    <div class="modal-base">
      <div class="modal-header">
        <p class="modal-header-label">Reset Smart Card</p>
        <i class="fa fa-times modal-close" @click.prevent="$emit('close')"></i>
      </div>
      <div class="modal-body">
        <p class="modal-status-text">
          Smart card status:
          <span :class="statusColor">{{ smartCardStatus }}</span>
        </p>
        <enter-puk v-if="body === 'enter-puk'" />
        <reusable-message
          v-else-if="body === 'reset-warning' && puk !== null"
          :message-data="messageData"
        />
        <enter-pin v-else-if="body === 'enter-pin'" />
        <reusable-message
          v-else-if="body === 'reset-complete' && $children[0].newPIN !== null"
          :message-data="messageData"
        />
      </div>
      <div class="modal-buttons">
        <button
          v-if="body !== 'reset-complete'"
          class="modal-cancel"
          @click.prevent="$emit('close')"
        >
          <i class="fa fa-times button-icon"></i>Cancel
        </button>
        <button class="modal-submit" @click.prevent="submit">
          <i :class="submitIcon"></i>{{ submitText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import EnterPUK from "./PUKResetModal.vue";
import ReusableMessage from "@/components/ReusableMessage.vue";
import EnterPin from "./PINResetModal.vue";
export default {
  name: "ResetSmartCard",
  components: {
    "reusable-message": ReusableMessage,
    "enter-puk": EnterPUK,
    "enter-pin": EnterPin,
  },
  props: {
    smartCardStatus: String,
    statusColor: String,
  },
  data: function () {
    return {
      messageData: {},
      body: "enter-puk",
      puk: null,
      submitIcon: "fa fa-check button-icon",
      submitText: "Continue",
    };
  },
  methods: {
    submit: function () {
      const childComponent = this.$children[0];
      if (this.body === "enter-puk") {
        this.messageData = {
          messageId: "warning",
          messageClass: "reset-body",
          iconId: "scr-warning-icon",
          iconClass: "fa fa-exclamation-triangle",
          textId: null,
          textClass: null,
          firstLine:
            "This will clear the smart card of all contents. This process cannot be undone.",
          secondLine: "Do you wish to proceed?",
        };
        this.enterPUK(childComponent);
      } else if (this.body === "reset-warning") {
        this.body = "enter-pin";
      } else if (this.body === "enter-pin") {
        this.messageData = {
          messageId: null,
          messageClass: "reset-body",
          iconId: "scr-reset-status",
          iconClass: "fa fa-check fa-2x",
          textId: "scr-completion",
          textClass: null,
          firstLine:
            "This smart card has successfully been reset. Keep the new PIN in a safe place.",
          secondLine: null,
        };
        this.resetCard(childComponent);
      } else {
        this.body = "enter-puk";
        this.submitIcon = "fa fa-check button-icon";
        this.submitText = "Continue";
        this.$emit("close");
      }
    },
    enterPUK: function (childComponent) {
      let message = "";
      if (!message && !childComponent.puk) {
        message = "Enter your PUK";
      }
      if (!message && childComponent.puk.length !== 8) {
        message = "Enter a valid PUK";
      }
      if (!message) {
        this.puk = childComponent.puk;
        this.body = "reset-warning";
      } else {
        this.$bus.emit("toaster", { message: message, type: "error" });
      }
    },
    resetCard: async function (childComponent) {
      let message;
      if (
        !childComponent.newPIN ||
        !childComponent.confirmPIN ||
        childComponent.newPIN.length !== 8 ||
        childComponent.confirmPIN.length !== 8
      ) {
        message = "Enter an 8 digit PIN";
      }
      if (!message && childComponent.newPIN !== childComponent.confirmPIN) {
        message = "Your PINs do not match";
      }
      if (message) {
        this.$bus.emit("toaster", { message: message, type: "error" });
        return;
      }

      let result = await window.fxctx.keys.smartCardReset(
        this.puk,
        childComponent.newPIN,
      );

      if (result.success) {
        this.$bus.emit("toaster", {
          message: "Smart Card succesfully reset",
          type: "success",
        });
        this.body = "reset-complete";
        this.submitIcon = "fa fa-check button-icon";
        this.submitText = "Finish";
      }

      if (!result.success) {
        this.$bus.emit("toaster", {
          message: result.msg,
          type: "error",
        });
        this.$emit("close");
      }
    },
  },
};
</script>

<style>
#scr-warning-icon {
  color: darkred;
  font-size: 2em;
  font-weight: 900;
  margin-bottom: 10px;
}

#scr-reset-status {
  margin: 0px 0px 10px 0px;
}

#scr-completion {
  margin-bottom: 0px;
}
</style>
