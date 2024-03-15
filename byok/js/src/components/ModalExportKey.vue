<template>
  <div>
    <modal-base @esc="$emit('closeModal')">
      <template #header>
        <p>Export Key - Slot {{ keySlot }}</p>
        <button @click="$emit('closeModal')">
          <i class="fa fa-times" />
        </button>
      </template>
      <template #main>
        <loading-spinner
          v-if="loading"
          class="loading-spinner"
          :loading="loading"
        />

        <ul>
          <li v-for="(value, key) in responseData" :key="key">
            {{ apiToReadable[key] }}:
            <span v-if="key === 'curve'" class="value">
              {{ eccCurveOidToName[value] }} ({{ value }})
            </span>
            <span v-else :class="[key === 'kcv' ? 'checksum' : 'value']">{{
              join(value)
            }}</span>
          </li>
        </ul>

        <key-block
          v-if="keyBlock"
          heading="Key Block"
          :key-block="keyBlock"
          :file-name="`key-block-${keySlot}`"
        />
      </template>
      <template #footer>
        <button class="button" @click="$emit('closeModal')">Close</button>
        <button
          v-if="!rawResponseData.publicKeyBlock"
          class="button blue-button"
          @click="showTranslateWizard = true"
        >
          Translate
        </button>
      </template>
    </modal-base>
    <wizard-translate-export
      v-if="showTranslateWizard"
      :key-block="keyBlock"
      :key-type="keyTypeForTranslate"
      :symmetric-type="symmetricType"
      :key-modifier="rawResponseData.modifier"
      :major-key="rawResponseData.majorKey"
    />
  </div>
</template>

<script>
import { eccCurveOidToName } from "@/utils/models.js";
import ModalBase from "@/components/ModalBase.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import KeyBlock from "@/components/KeyBlock.vue";

import WizardTranslateExport from "@/components/WizardTranslateExport.vue";

let apiToReadable = {
  usage: "Usage",
  securityUsage: "Security usage",
  kcv: "Checksum",
  label: "Label",
  majorKey: "Major key",
  type: "Type",
  modifier: "Modifier",
  exponent: "Exponent",
  modulus: "Modulus",
  curve: "Curve",
};

function join(value) {
  if (Array.isArray(value)) {
    return value.join(", ");
  }
  return value;
}

export default {
  components: {
    "modal-base": ModalBase,
    "loading-spinner": LoadingSpinner,
    "key-block": KeyBlock,
    "wizard-translate-export": WizardTranslateExport,
  },
  inject: ["getSessionId", "isGpMode"],
  props: {
    type: {
      type: String,
      required: false,
    },
    keySlot: {
      type: Number,
      required: true,
    },
  },
  data: function () {
    return {
      rawResponseData: {},
      responseData: null,
      keyBlock: null,
      loading: true,
      eccCurveOidToName: eccCurveOidToName,
      apiToReadable: apiToReadable,
      showTranslateWizard: false,
      keyTypeForTranslate: "",
      symmetricType: "",
    };
  },
  mounted: function () {
    let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
    if (!this.isGpMode()) {
      url += `/${this.type.toLowerCase()}`;
    }
    url += `/${this.keySlot}`;
    this.$httpV2
      .get(url, { errorContextMessage: "Failed to export key" })
      .then((data) => {
        this.rawResponseData = data;

        // 🤷
        if (data.keyBlock) {
          this.symmetricType = data.type;
          this.keyTypeForTranslate = "Symmetric";
        } else if (data.modulus) {
          this.keyTypeForTranslate = "RSA";
        } else {
          this.keyTypeForTranslate = "ECC";
        }

        let filteredData = {};
        for (let key in data) {
          if (key.toLowerCase().includes("keyblock")) {
            this.keyBlock = data[key];
            continue;
          }
          if (Array.isArray(data[key]) && data[key].length === 0) {
            continue;
          }
          filteredData[key] = data[key];
        }
        this.responseData = filteredData;
      })
      .finally(() => {
        this.loading = false;
      });
  },
  created: function () {
    this.$bus.on("wizardClose", this.handleWizardClose);
  },
  unmounted: function () {
    this.$bus.off("wizardClose", this.handleWizardClose);
  },
  methods: {
    join: join,
    handleWizardClose: function () {
      this.showTranslateWizard = false;
    },
  },
};
</script>

<style scoped>
.value {
  color: var(--text-color-blue-lighter);
}

.loading-spinner {
  margin: auto;
}
</style>
