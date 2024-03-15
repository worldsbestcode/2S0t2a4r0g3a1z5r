<template>
  <div>
    <div class="modal-base">
      <div class="modal-header">
        <p class="modal-header-label">Change Smartcard {{ action }}</p>
        <i class="fa fa-times modal-close" @click.prevent="$emit('close')"></i>
      </div>
      <div class="modal-body">
        <p class="modal-status-text">
          Smart card status:
          <span :class="statusColor">{{ smartCardStatus }}</span>
        </p>
        <div class="cp-input-box">
          <p class="cp-input-label">{{ labelText }}</p>
          <input
            v-model="pin"
            class="cp-input"
            :placeholder="action"
            type="password"
          />
        </div>
      </div>
      <div class="modal-buttons">
        <button class="modal-cancel" @click.prevent="$emit('close')">
          <i class="fa fa-times button-icon"></i>Cancel
        </button>
        <button
          class="button blue-button"
          :disabled="pin.length !== 8"
          @click="submit"
        >
          <i class="fa fa-check button-icon"></i>{{ submitText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChangePIN",
  props: {
    action: String,
    smartCardStatus: String,
    statusColor: String,
  },
  data: function () {
    return {
      pin: "",
      currentPIN: null,
      newPIN: null,
      submitText: "Continue",
      stage: 0,
    };
  },
  computed: {
    labelText: function () {
      const labels = [
        `Enter current ${this.action}`,
        `Enter new ${this.action} (must be 8 characters)`,
        `Re-enter new ${this.action}`,
      ];
      return labels[this.stage];
    },
  },
  methods: {
    updateData: function (stage, currentPIN, newPIN, reset = false) {
      this.stage = stage;
      this.pin = "";
      this.currentPIN = reset ? null : currentPIN || this.currentPIN;
      this.newPIN = reset ? null : newPIN || this.newPIN;
    },
    changePIN: function () {
      let cbFunc = window.fxctx.keys.smartCardChangePIN;
      if (this.action === "PUK") {
        cbFunc = window.fxctx.keys.smartCardChangePUK;
      }

      cbFunc(this.currentPIN, this.newPIN).then((result) => {
        let toast;
        if (result.success) {
          toast = {
            message: `${this.action} change successful`,
            type: "success",
          };
        } else {
          toast = {
            message: result.msg,
            type: "error",
          };
        }

        this.$bus.emit("toaster", toast);
        this.$emit("close");
      });

      this.updateData(null, null, null, true);
    },
    submit: function () {
      if (this.stage === 0) {
        this.updateData(1, this.pin);
      } else if (this.stage === 1) {
        this.updateData(2, undefined, this.pin);
        this.submitText = "Finish";
      } else if (this.stage === 2 && this.pin !== this.newPIN) {
        this.$bus.emit("toaster", {
          message: `Your ${this.action}s do not match`,
          type: "error",
        });
        this.updateData(0);
      } else {
        this.changePIN();
      }
    },
  },
};
</script>

<style>
.cp-input-box {
  background-color: #eee;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 3px;
}

.cp-input-label {
  display: inline-block;
  width: calc(100% - 204px);
  margin: 0px;
}

.cp-input {
  display: inline-block;
  width: 200px;
  padding: 6px 12px 6px 12px;
  border: 1px solid #ddd;
  border-radius: 3px;
}
</style>
