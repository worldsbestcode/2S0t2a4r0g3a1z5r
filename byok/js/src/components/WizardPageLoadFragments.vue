<template>
  <ul class="wizard-page-list">
    <li>
      <span>Status</span>
      <span :class="cardPresent ? 'text-success' : 'text-danger'">{{
        smartCardStatus
      }}</span>
    </li>
    <li>
      <span>Smart card PIN</span>
      <input
        v-model="pin"
        class="input input-wide"
        type="password"
        :disabled="!cardPresent || allPartsRead || loadingFromCard"
      />
    </li>
    <li>
      <loading-spinner class="loading-spinner" :loading="loadingFromCard" />
      <button
        class="button blue-button"
        :disabled="!canReadFragment"
        @click="retrieveFragment"
      >
        <i class="fa fa-sim-card" />
        {{ buttonText }}
      </button>
    </li>
  </ul>
</template>

<script>
import LoadingSpinner from "@/components/LoadingSpinner.vue";
export default {
  name: "SmartCardLoadFragments",
  title: "Load Fragment",
  components: {
    "loading-spinner": LoadingSpinner,
  },
  description: null,
  continueButtonAtBottom: true,
  defaultData: function () {
    const MAX_FRAGMENTS = 12;
    return {
      authReceipts: {
        value: [],
        wizardSummaryText: null,
      },
      ...Object.fromEntries(
        Array.from(Array(MAX_FRAGMENTS).keys()).map((idx) => [
          `kcv${idx}`,
          {
            value: null,
            wizardSummaryText: `Part ${idx + 1} Checksum`,
          },
        ]),
      ),
    };
  },
  inject: ["getSessionId"],
  props: {
    keyDetails: {
      type: Function,
      required: true,
    },
  },
  data: function () {
    return {
      pin: "",
      rawFragments: [],
      smartCardStatus: "Loading",
      smartCardStatusInterval: null,
      allPartsRead: false,
      partsNeeded: null,
      loadingFromCard: false,
    };
  },
  computed: {
    wizardContinueButtonDisabled: function () {
      return !this.allPartsRead;
    },
    cardPresent: function () {
      return this.smartCardStatus && this.smartCardStatus === "Card present";
    },
    canReadFragment: function () {
      let validPin = this.pin && this.pin.length === 8;
      return validPin && this.cardPresent && !this.allPartsRead;
    },
    buttonText: function () {
      if (this.allPartsRead) {
        return `Complete (${this.partsNeeded}/${this.partsNeeded})`;
      }
      if (this.partsNeeded && this.partsNeeded > 1) {
        return `Read fragment ${this.authReceipts.length + 1} of ${
          this.partsNeeded
        }`;
      }
      return `Read first fragment`;
    },
  },
  watch: {
    wizardContinueButtonDisabled: function (newValue) {
      this.$emit("wizardContinueButtonDisabled", newValue);
    },
  },
  mounted: function () {
    this.$emit(
      "wizardContinueButtonDisabled",
      this.wizardContinueButtonDisabled,
    );

    if (window.fxctx) {
      this.smartCardStatusInterval = setInterval(
        () =>
          window.fxctx.keys.smartCardGetStatus().then((result) => {
            this.smartCardStatus = result.value;
          }),
        [1500],
      );
    }
  },
  beforeUnmount: function () {
    if (this.smartCardStatusInterval !== null) {
      clearInterval(this.smartCardStatusInterval);
    }
  },
  methods: {
    retrieveFragment: function () {
      this.loadingFromCard = true;
      this.loginToSmartCard()
        .then(() =>
          this.readFragmentFromSmartCard()
            .then((fragment) =>
              this.makeAuthReceiptFromFragment(fragment)
                .then((authReceipt) => this.handleAuthReceipt(authReceipt))
                .finally(() => {
                  this.loadingFromCard = false;
                }),
            )
            .catch(() => {
              this.loadingFromCard = false;
            }),
        )
        .catch(() => {
          this.loadingFromCard = false;
        });
    },
    loginToSmartCard: async function () {
      return new Promise((resolve, reject) =>
        window.fxctx.keys
          .smartCardPINLogin(this.pin)
          .then((result) => {
            if (result.success) {
              resolve();
            } else {
              this.$bus.emit("toaster", {
                message: result.msg || "Unknown error",
                type: "error",
              });
              reject(result.msg);
            }
          })
          .finally(() => {
            this.pin = "";
          }),
      );
    },
    readFragmentFromSmartCard: async function () {
      return new Promise((resolve, reject) =>
        window.fxctx.keys.smartCardGetFragment().then((fragmentResult) => {
          if (
            fragmentResult.success &&
            this.validateFragment(fragmentResult.value)
          ) {
            resolve(fragmentResult.value);
          } else {
            this.$bus.emit("toaster", {
              message: fragmentResult.msg || "Unknown error",
              type: "error",
            });
            reject(fragmentResult.msg);
          }
        }),
      );
    },
    validateFragment: function (fragment) {
      let error = null;

      if (!fragment) {
        error = "No fragment on card";
      } else if (this.rawFragments && this.rawFragments.includes(fragment)) {
        error = "Fragment is duplicate of previously loaded fragment";
      } else {
        this.rawFragments.push(fragment);
      }

      if (error) {
        this.$bus.emit("toaster", { message: error, type: "error" });
      }
      return !error;
    },
    makeAuthReceiptFromFragment: async function (fragment) {
      const csklUri = `/clusters/sessions/${this.getSessionId()}/keyload/auth-receipt`;
      const csklPayload = {
        input: {
          fragment: fragment,
          encrypted: true, // we read from smart card -> encrypted
        },
        ...this.keyDetails(),
      };

      return this.$httpV2
        .post(csklUri, csklPayload, {
          errorContextMessage: "Failed to encrypt key part",
        })
        .catch((error) => {
          this.$bus.emit("toaster", { message: error, type: "error" });
        });
    },
    handleAuthReceipt: function (authReceipt) {
      this[`kcv${this.authReceipts.length}`] = authReceipt.partKcv;
      this.authReceipts.push(authReceipt.authReceipt);

      let partsHave = this.authReceipts.length;
      this.partsNeeded = authReceipt.want;
      if (partsHave >= this.partsNeeded) {
        this.allPartsRead = true;
      }
    },
  },
};
</script>
