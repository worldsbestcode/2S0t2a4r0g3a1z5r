<template>
  <div class="management-page">
    <header>
      <p>Working Keys</p>
      <close-button @click.prevent="$emit('close')" />
    </header>

    <div class="working-keys">
      <section id="summary">
        <div class="wk-section-title">
          <p class="wk-section-title-text">Key Table</p>
        </div>
        <div id="wk-key-table">
          <div id="wk-kt-header">
            <div class="wk-kt-type wk-kt-column-title">Type</div>
            <div class="wk-kt-used wk-kt-column-title">Used</div>
            <div class="wk-kt-available wk-kt-column-title">Available</div>
          </div>
          <div v-for="key in keys" :key="key.type" class="wk-kt-row">
            <div class="wk-kt-type">{{ apiToReadable[key.type] }}</div>
            <div class="wk-kt-used">{{ key.used }}</div>
            <div class="wk-kt-available">{{ key.available }}</div>
          </div>
        </div>
        <div id="mkt-button">
          <button class="cursor" @click.prevent="openKeyManager()">
            Manage key table
          </button>
          <div v-if="show === 'types'" id="dropdown">
            <p class="cursor types" @click="openKeyManager('symmetric')">
              Symmetric
            </p>
            <p class="cursor types" @click="openKeyManager('asymmetric')">
              Asymmetric
            </p>
            <p class="cursor types" @click="openKeyManager('diebold')">
              Diebold
            </p>
            <p
              v-if="isGpMode()"
              class="cursor types"
              @click="openKeyManager('certificates')"
            >
              Certificates
            </p>
          </div>
        </div>
      </section>

      <section id="buttons">
        <div class="wk-section-title">
          <p class="wk-section-title-text">Key Tasks</p>
        </div>
        <div id="wk-button-list">
          <button class="button" @click="setWizard('WizardRandomKey')">
            Random New Key
          </button>
          <button
            class="button"
            :disabled="!isExcryptTouchResult"
            @click="setWizard('WizardImportComponents')"
          >
            Import XOR Components
          </button>
          <button
            class="button"
            :disabled="!isExcryptTouchResult"
            @click="setWizard('WizardImportSmartCards')"
          >
            Import Smart Cards
          </button>
          <button class="button" @click="setWizard('WizardImportKeyBlock')">
            Import Key Block
          </button>
          <button class="button" @click="setWizard('WizardLoadDiebold')">
            Load Diebold Table
          </button>
          <button class="button" @click="setWizard('WizardLoadPki')">
            Load PKCS8 Private Key
          </button>
          <button class="button" @click="setWizard('WizardTranslateKey')">
            Translate Key Block
          </button>
          <button class="button" @click="setWizard('WizardVerifyKey')">
            Verify Key Block
          </button>
        </div>
      </section>
    </div>

    <key-manager
      v-if="show === 'key-manager'"
      :financial="!isGpMode()"
      :type="type"
      :current-cluster="currentCluster"
      @close="close"
      @refreshTableInformation="initializeTableInformation"
    />
    <component
      :is="currentWizard"
      @refreshTableInformation="initializeTableInformation"
    />
  </div>
</template>

<script>
import { wizardMixin, wizards } from "@/utils/wizard.js";
import CloseButton from "@/components/CloseButton.vue";
import KeyManager from "@/components/KeyManager.vue";
import WizardRandomKey from "@/components/WizardRandomKey.vue";
import WizardVerifyKey from "@/components/WizardVerifyKey.vue";
import WizardLoadDiebold from "@/components/WizardLoadDiebold.vue";
import WizardImportSmartCards from "@/components/WizardImportSmartCards.vue";
import WizardImportComponents from "@/components/WizardImportComponents.vue";
import WizardImportKeyBlock from "@/components/WizardImportKeyBlock.vue";
import WizardLoadPki from "@/components/WizardLoadPki.vue";
import WizardTranslateKey from "@/components/WizardTranslateKey.vue";

let apiToReadable = {
  certificate: "Certificate",
  diebold: "Diebold",
  ecc: "ECC",
  rsa1024: "RSA 1024",
  rsa2048: "RSA 2048",
  rsa3072: "RSA 3072",
  rsa4096: "RSA 4096",
  rsa512: "RSA 512",
  symmetric: "Symmetric",
  total: "Total",
};

let keyTableTypeOrder = [
  "certificate",
  "diebold",
  "ecc",
  "rsa512",
  "rsa1024",
  "rsa2048",
  "rsa3072",
  "rsa4096",
  "symmetric",
  "total",
];

export default {
  name: "WorkingKeys",
  components: {
    "key-manager": KeyManager,
    "close-button": CloseButton,
  },
  mixins: [wizardMixin],
  inject: ["getSessionId", "isGpMode", "isExcryptTouch"],
  props: {
    currentCluster: Object,
  },
  data: function () {
    return {
      wizards: wizards({
        WizardVerifyKey,
        WizardLoadDiebold,
        WizardImportSmartCards,
        WizardImportKeyBlock,
        WizardLoadPki,
        WizardTranslateKey,
        WizardRandomKey,
        WizardImportComponents,
      }),
      keys: [],
      type: null,
      show: null,
      apiToReadable: apiToReadable,
      isExcryptTouchResult: null,
    };
  },
  mounted: async function () {
    this.initializeTableInformation();
    this.isExcryptTouchResult = await this.isExcryptTouch();
  },
  methods: {
    close: function () {
      this.show = null;
      this.type = null;
    },
    openKeyManager: function (type = "types") {
      let permitted = ["Keys", "Excrypt:GPKM"].some(
        (permission) => this.currentCluster.session.permissions[permission],
      );
      if (permitted && !this.isGpMode()) {
        this.show =
          type === "types"
            ? this.show === "types"
              ? null
              : type
            : "key-manager";
        this.type = type;
      } else if (permitted && this.isGpMode()) {
        this.show = "key-manager";
      }
    },
    initializeTableInformation: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/keytable/info`;
      this.$httpV2
        .get(url, {
          errorContextMessage: "Failed to fetch keytable information",
        })
        .then((data) => {
          if (!this.isGpMode()) {
            delete data.certificate;
          }

          this.keys = keyTableTypeOrder
            .map((type) => {
              let key = data[type];
              if (key) {
                return {
                  type: type,
                  available: key.available,
                  used: key.used,
                };
              }
            })
            .filter((x) => x !== undefined);
        });
    },
  },
};
</script>

<style scoped>
.cursor:hover {
  cursor: pointer;
}

.working-keys {
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  align-items: start;
}

#summary,
#buttons {
  border: 1px solid var(--border-color);
  border-radius: 3px;
}

.wk-section-title {
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  line-height: 1;
  font-size: 16px;
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
  border-top-right-radius: 3px;
  border-top-left-radius: 3px;
}

.wk-section-title-text {
  color: var(--text-color-blue);
  margin: 0px;
}

#wk-kt-header {
  background-color: #f4f4f4;
}

.wk-kt-row {
  border-top: 1px solid #eee;
}

.wk-kt-column-title {
  color: #666;
}

.wk-kt-available,
.wk-kt-used,
.wk-kt-type {
  display: inline-block;
  font-size: 13px;
  padding: 8px;
  margin-right: -5px;
}

.wk-kt-type {
  width: calc(38% - 13px);
}

.wk-kt-used {
  width: calc(21% - 13px);
  border-left: 1px solid #eee;
  border-right: 1px solid #eee;
}

.wk-kt-available {
  width: calc(38% - 13px);
}

#mkt-button {
  padding: 10px;
  border-top: 1px solid #eee;
}

#mkt-button > button {
  width: 100%;
  padding: 6px 12px;
  border: 1px solid #367fa9;
  border-radius: 3px;
  background-image: linear-gradient(to bottom, #0088cc, #0044cc);
  color: #fff;
  font-size: 14px;
}

#mkt-button > button:active {
  background-image: linear-gradient(to bottom, #0081cc, #0041cc);
  color: #fafafa;
}

#dropdown {
  width: calc(100% - 4px);
  border: 1px solid #eee;
  margin: 0px auto;
  text-align: center;
  font-size: 13px;
  background-color: rgba(0, 0, 0, 0.02);
}

.types {
  padding: 8px;
  border-bottom: 1px solid #eee;
  margin: 0px;
}

#dropdown > p:last-of-type {
  border: 0px;
}

.wk-kt-list-label-wrapper {
  background-color: #f4f4f4;
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 2px;
  font-size: 13px;
  color: #666;
}

.wk-kt-list-label {
  margin: 0px;
}

#wk-button-list {
  display: grid;
  gap: 0.5rem;
  padding: 0.5rem;
}
</style>
