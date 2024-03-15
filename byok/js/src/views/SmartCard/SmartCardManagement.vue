<template>
  <div class="management-page">
    <header>
      <p>Smart cards</p>
      <div class="smart-card-status">
        Smart card status:
        <span :class="statusColor">{{ smartCardStatus }}</span>
      </div>
      <close-button @click="$emit('close')" />
    </header>

    <nav class="smart-card-nav">
      <button class="button reset-button" @click="resetCard">Reset card</button>
      <button class="button pin-button" @click="changePIN('PIN')">
        Change PIN
      </button>
      <button class="button puk-button" @click="changePIN('PUK')">
        Change PUK
      </button>
    </nav>

    <reset-smart-card
      v-if="startReset"
      id="modal"
      :key="startReset"
      :smart-card-status="smartCardStatus"
      :status-color="statusColor"
      @close="close"
    />
    <change-pin
      v-if="startPINChange || startPUKChange"
      id="modal"
      :key="action"
      :action="action"
      :smart-card-status="smartCardStatus"
      :status-color="statusColor"
      @close="close"
    />
  </div>
</template>

<script>
import CloseButton from "@/components/CloseButton.vue";
import ResetSmartCard from "@/views/SmartCard/ResetSmartCard/ResetSmartCard.vue";
import ChangePIN from "@/views/SmartCard/ChangePIN.vue";
export default {
  name: "SmartCard",
  components: {
    "reset-smart-card": ResetSmartCard,
    "change-pin": ChangePIN,
    "close-button": CloseButton,
  },
  props: {
    currentCluster: Object,
  },
  data: function () {
    return {
      statusChecker: null,
      smartCardStatus: "Reader not detected",
      startReset: false,
      action: null,
      startPINChange: false,
      startPUKChange: false,
    };
  },
  computed: {
    statusColor: function () {
      return this.smartCardStatus === "Card present"
        ? "smart-card-connected"
        : "no-smart-card";
    },
  },
  mounted: function () {
    if (window.fxctx) {
      this.statusChecker = setInterval(this.checkSmartCardStatus, [1500]);
    }
  },
  beforeUnmount: function () {
    if (this.statusChecker !== null) {
      clearInterval(this.statusChecker);
    }
  },
  methods: {
    close: function () {
      this.startReset = false;
      this.startPINChange = false;
      this.startPUKChange = false;
      this.action = null;
    },
    resetCard: function () {
      this.startReset = true;
    },
    changePIN: function (action) {
      this.action = action;
      this[action === "PIN" ? "startPINChange" : "startPUKChange"] = true;
    },
    checkSmartCardStatus: function () {
      window.fxctx.keys.smartCardGetStatus().then((result) => {
        this.smartCardStatus = result.value;
      });
    },
  },
};
</script>

<style scoped>
.smart-card-status {
  margin-right: 1rem;
}

.smart-card-connected {
  color: #3c763d;
}

.no-smart-card {
  color: rgba(255, 0, 0, 0.5);
}

.smart-card-nav {
  display: grid;
  grid-template-areas:
    "reset pin"
    "reset puk";
  gap: 1rem;
  margin: 1rem;
}

.reset-button {
  grid-area: reset;
  background-image: linear-gradient(to bottom, #ee5f5b, #bd362f);
  color: white;
  text-shadow: none;
  border-color: rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.1) rgba(0, 0, 0, 0.25);
}

.reset-button:hover {
  background: #bd362f;
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.15),
    0 1px 2px rgba(0, 0, 0, 0.05);
  color: white;
}

.reset-button:active {
  background-color: #bd362f;
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.15),
    0 1px 2px rgba(0, 0, 0, 0.05);
  color: white;
}

.puk-button {
  grid-area: puk;
}

.pin-button {
  grid-area: pin;
}
</style>
