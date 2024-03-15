<template>
  <div>
    <ul v-if="formatType() === 'AKB'" class="wizard-page-list">
      <li>
        <span>Header <span class="hint">(optional)</span></span>
        <input v-model="keyBlockHeader" class="input input-wide" />
      </li>
    </ul>
    <div v-else>
      <ul class="wizard-page-list">
        <li>
          <span>Binding method</span>
          <select-input-tr31
            v-model="bindingMethod"
            :mappings="bindingMethods"
            maxlength="1"
          />
        </li>
        <li>
          <span>Key usage</span>
          <select-input-tr31
            v-model="keyUsage"
            :mappings="keyUsages"
            maxlength="2"
            custom-text="Proprietary"
          />
        </li>
        <li>
          <span>Algorithm</span>
          <select-input-tr31
            v-model="algorithm"
            :mappings="algorithms"
            maxlength="1"
            custom-text="Proprietary"
          />
        </li>
        <li>
          <span>Mode of use</span>
          <select-input-tr31
            v-model="modeOfUse"
            :mappings="modesOfUse"
            maxlength="1"
            custom-text="Proprietary"
          />
        </li>
        <li>
          <span>Key version number</span>
          <select-input-tr31
            v-model="version"
            :mappings="versioning"
            maxlength="2"
            custom-text="Version"
          />
        </li>
        <li>
          <span>Exportability</span>
          <select-input-tr31
            v-model="exportability"
            :mappings="exportabilityOptions"
            maxlength="1"
            custom-text="Proprietary"
          />
        </li>
      </ul>

      <p class="wizard-page-description optional-blocks-text">
        Optional blocks
      </p>
      <optional-blocks v-model="optionalBlocks" />
    </div>
  </div>
</template>

<script>
import { getValidUsages } from "@/utils/models.js";
import SelectInputTr31 from "@/components/SelectInputTr31.vue";
import OptionalBlocks from "@/components/OptionalBlocks.vue";

let desBindingMethods = {
  A: "Key Variant Method 2005",
  B: "Key Derivation Method",
  C: "Key Variant Method 2010",
};

let nonDesBindingMethods = {
  D: "Key Derivation Method 2018",
};

let desBindingMethodInternational = {
  0: "DES",
};

let aesBindingMethodInternational = {
  1: "AES",
};

let keyUsages = {
  K0: "Key encryption or wrapping",
  P0: "PIN encryption",
  D0: "Data encryption",
  M1: "ISO 9797-1 MAC algorithm 1",
  V0: "PIN verification, KPV, other algorithm",
  "05": "ATM Key (Proprietary)",
  I0: "Initialization vector (IV)",
  "07": "Modifier 0x07 (Proprietary)",
  B0: "BDK base derivation key",
  P1: "PIN Generation Key (Proprietary)",
  E0: "EMV/CC master: app cryptograms",
  10: "Modifier 0x0A (Proprietary)",
  11: "Modifier 0x0B (Proprietary)",
  12: "Modifier 0x0C (Proprietary)",
  14: "Detachment Base Key (Proprietary)",
  15: "Decimalization Table (Proprietary)",
  16: "Modifier 0x10 (Proprietary)",
  17: "Modifier 0x11 (Proprietary)",
  18: "Modifier 0x12 (Proprietary)",
  19: "Modifier 0x13 (Proprietary)",
  20: "Modifier 0x14 (Proprietary)",
  21: "Modifier 0x15 (Proprietary)",
  22: "Modifier 0x16 (Proprietary)",
  23: "Modifier 0x17 (Proprietary)",
  24: "Modifier 0x18 (Proprietary)",
  25: "Modifier 0x19 (Proprietary)",
  26: "Modifier 0x1A (Proprietary)",
  30: "Modifier 0x1E (Proprietary)",
  31: "Modifier 0x1F (Proprietary)",
  E1: "EMV/CC master: secure msg for Confidentiality",
  E3: "EMV/CC master: data authentication code",
  E4: "EMV/CC master: dynamic numbers",
  B1: "DUKPT initial key",
  B2: "Base key variant key",
  C0: "CVK card verification key",
  E2: "EMV/CC master: secure msg for Integrity",
  E5: "EMV/CC master: card personalization",
  E6: "EMV/CC master: other",
  K1: "TR-31 key block protection key",
  M0: "ISO 16609 MAC algorithm 1 (using TDEA)",
  M2: "ISO 9797-1 MAC algorithm 2",
  M3: "ISO 9797-1 MAC algorithm 3",
  M4: "ISO 9797-1 MAC algorithm 4",
  M5: "ISO 9797-1 MAC algorithm 5",
  M6: "ISO 9797-1 MAC algorithm 5/CMAC",
  M7: "HMAC",
  M8: "ISO 9797-1 MAC algorithm 6",
  V1: "PIN verification, IBM 3624",
  V2: "PIN verification, VISA PVV",
  V3: "PIN verification, X9.132 algorithm 1",
  V4: "PIN verification, X9.132 algorithm 2",

  // asymmetric usages ???
  S0: "Asymmetric key pair for digital signature",
  S1: "Asymmetric key pair, CA key",
  S2: "Asymmetric key pair, non X9.24 key",
  K2: "TR-34 asymmetric key",
  K3: "Asymmetric key for key agreement/key wrapping",
  D1: "Data encryption",
};

let internationalKeyUsages = {
  "01": "WatchWord Key (WWK)",
  "02": "RSA Public Key",
  "03": "RSA Private Key (signing key management)",
  "04": "RSA Private Key (EMV Issunace)",
  "05": "RSA Private Key (PIN Management)",
  "06": "RSA Private Key (TLS decryption)",
  11: "Card verification (American Express CSC)",
  12: "Card verification (Mastercard CVC)",
  13: "Card verification (Visa CVV)",
  21: "Data encryption using a DEK",
  22: "Data encryption using a ZEK",
  23: "Data encryption using a TEK",
  31: "VisaCash Master Load Key KML",
  32: "Dynamic CVV Master Key MK-CVC3",
  41: "DUKPT Base Derivation Key BDK-2",
  42: "DUKPT Base Derivation Key BDK-3",
  43: "DUKPT Base Derivation Key BDK-4",
  51: "Terminal key encryption TMK",
  52: "Zone key encryption ZMK",
  53: "ZKA Master Key",
  54: "ZKA - Encryption Key (KEK)",
  55: "ZKA - Encryption Key (Transport Key)",
  61: "HMAC Key (sha1)",
  62: "HMAC Key (SHA224)",
  63: "HMAC Key (SHA256)",
  64: "HMAC Key (SHA384)",
  65: "HMAC Key (SHA512)",
  71: "Terminal PIN encryption TPK",
  72: "Zone PIN encryption ZPK",
  73: "Transaction key scheme Terminal Key Register TKR",
};

let algorithms = {
  D: "DEA (single DES)",
  T: "Triple DEA (TDEA/TDES)",
  A: "AES",
  R: "RSA",
  E: "ECC",
};

let modesOfUse = {
  B: "Both encrypt and decrypt",
  C: "MAC calculate (generate and verify)",
  D: "Decrypt only",
  E: "Encrypt only",
  G: "MAC generate only",
  N: "No special restrictions or not applicable",
  T: "Both Sign and decrypt",
  S: "Signature only",
  V: "MAC verify only",
  X: "Key used to derive other keys",
  Y: "Key used to create key variants",
};

let versioning = {
  "00": "No versioning used",
};

let exportabilityOptions = {
  N: "Non-exportable",
  E: "Exportable under trusted key",
};

let defaultUsageForModifiers = {
  0x0: "K0",
  0x1: "P0",
  0x2: "D0",
  0x3: "M1",
  0x4: "V0",
  0x5: "05",
  0x6: "I0",
  0x7: "07",
  0x8: "B0",
  0x9: "P1",
  0xa: "10",
  0xb: "11",
  0xc: "12",
  0xd: "E0",
  0xe: "14",
  0xf: "15",
  0x10: "16",
  0x11: "17",
  0x12: "18",
  0x13: "19",
  0x14: "20",
  0x15: "21",
  0x16: "22",
  0x17: "23",
  0x18: "24",
  0x19: "25",
  0x1a: "26",
  0x1b: "E4",
  0x1c: "E3",
  0x1d: "E1",
  0x1e: "30",
  0x1f: "31",
};

let defaultUsageForAsymmetricKeys = {
  Sign: "S0",
  Verify: "S0",
  Wrap: "K2",
  Unwrap: "K2",
  Encrypt: "D1",
  Decrypt: "D1",
};

export default {
  components: {
    SelectInputTr31,
    OptionalBlocks,
  },
  inject: ["isGpMode"],
  title: "Key Block Header",
  description: "Fill out the key block header (optional)",
  continueButtonAtBottom: true,
  defaultData: function () {
    return {
      keyBlockHeader: {
        value: null,
        wizardSummaryText: "Key block header",
      },
    };
  },
  props: {
    formatType: {
      type: Function,
      required: true,
    },
    wrappingKeyType: {
      type: Function,
      required: true,
    },

    keyInitialUsage: {
      type: Function,
      required: true,
    },

    keyType: {
      type: Function,
      required: true,
    },

    keyTypeForGetValidUsages: {
      type: Function,
      required: true,
    },

    keyModifier: {
      type: Function,
      required: true,
    },
  },
  data: function () {
    return {
      bindingMethod: "0",
      keyUsage: "00",
      algorithm: "0",
      modeOfUse: "0",
      version: "00",
      exportability: "E",
      optionalBlocks: [],

      bindingMethods: {},
      keyUsages,
      algorithms,
      modesOfUse,
      versioning,
      exportabilityOptions,
    };
  },
  computed: {
    builtKeyBlockHeader: function () {
      let header = "";

      if (this.formatType() === "International") {
        header += "S";
      }

      header += this.bindingMethod.padStart(1, "0");

      // length of keyblock, field is ignored
      header += "0000";

      header += this.keyUsage.padStart(2, "0");

      header += this.algorithm.padStart(1, "0");

      header += this.modeOfUse.padStart(1, "0");

      header += this.version.padStart(2, "0");

      header += this.exportability.padStart(1, "0");

      header += this.optionalBlocks.length
        .toString(16)
        .toUpperCase()
        .padStart(2, "0");

      // reserved, always 00
      header += "00";

      for (let optionalBlock of this.optionalBlocks) {
        let valueLength = optionalBlock.value.length;
        let optionalBlockTotalLength = 4 + valueLength;
        header += optionalBlock.key;
        header += optionalBlockTotalLength
          .toString(16)
          .toUpperCase()
          .padStart(2, "0");
        header += optionalBlock.value;
      }

      return header;
    },
  },
  watch: {
    builtKeyBlockHeader: function (newValue) {
      this.keyBlockHeader = newValue;
    },
  },
  mounted: function () {
    this.$emit("wizardContinueButtonDisabled", false);

    let formatType = this.formatType();
    let keyType = this.keyType();
    let isAsymmetric = keyType === "RSA" || keyType === "ECC";
    let initialKeyUsage = this.keyInitialUsage();

    if (initialKeyUsage.length === 0) {
      initialKeyUsage = getValidUsages({
        type: this.keyTypeForGetValidUsages(),
        gpMode: this.isGpMode(),
        modifier: this.keyModifier(),
      })[0];
    }

    this.setBindingMethod(formatType);
    this.setKeyUsage(formatType, isAsymmetric, initialKeyUsage);
    this.setAlgorithm(keyType);
    this.setModeOfUse(initialKeyUsage, isAsymmetric);
  },
  methods: {
    setBindingMethod: function (formatType) {
      let wrappingKeyType = this.wrappingKeyType();
      if (wrappingKeyType.includes("DES")) {
        if (formatType === "International") {
          this.bindingMethods = desBindingMethodInternational;
        } else {
          this.bindingMethods = desBindingMethods;
        }
      } else {
        if (formatType === "International") {
          this.bindingMethods = aesBindingMethodInternational;
        } else {
          this.bindingMethods = nonDesBindingMethods;
        }
      }
      this.bindingMethod = Object.keys(this.bindingMethods)[0];
    },

    setKeyUsage: function (formatType, isAsymmetric, initialKeyUsage) {
      if (formatType === "International") {
        this.keyUsages = { ...keyUsages, ...internationalKeyUsages };
      }

      let keyModifier = this.keyModifier();
      if (isAsymmetric) {
        if (initialKeyUsage.length === 0) {
          this.keyUsage = "00";
        } else {
          this.keyUsage = defaultUsageForAsymmetricKeys[initialKeyUsage[0]];
        }
      } else {
        this.keyUsage = defaultUsageForModifiers[keyModifier];
      }
    },

    setAlgorithm: function (keyType) {
      if (keyType === "RSA") {
        this.algorithm = "R";
      } else if (keyType === "ECC") {
        this.algorithm = "E";
      } else if (keyType.startsWith("AES")) {
        this.algorithm = "A";
      } else if (keyType === "DES") {
        this.algorithm = "D";
      } else if (keyType === "2TDES" || keyType === "3TDES") {
        this.algorithm = "T";
      }
    },

    setModeOfUse: function (initialKeyUsage, isAsymmetric) {
      let hasEncrypt = initialKeyUsage.includes("Encrypt");
      let hasDecrypt = initialKeyUsage.includes("Decrypt");
      let hasWrap = initialKeyUsage.includes("Wrap");
      let hasUnwrap = initialKeyUsage.includes("Unwrap");
      let hasSign = initialKeyUsage.includes("Sign");
      let hasVerify = initialKeyUsage.includes("Verify");
      let isEncryptDecrypt = hasEncrypt && hasDecrypt;
      let isWrapUnwrap = hasWrap && hasUnwrap;
      let isSignVerify = hasSign && hasVerify;

      if (isEncryptDecrypt || isWrapUnwrap) {
        this.modeOfUse = "B";
      } else if (hasEncrypt || hasWrap) {
        this.modeOfUse = "E";
      } else if (hasDecrypt || hasUnwrap) {
        this.modeOfUse = "D";
      } else if (isSignVerify) {
        if (isAsymmetric) {
          this.modeOfUse = "S";
        } else {
          this.modeOfUse = "C";
        }
      } else if (hasSign) {
        if (isAsymmetric) {
          this.modeOfUse = "S";
        } else {
          this.modeOfUse = "G";
        }
      } else if (hasVerify) {
        this.modeOfUse = "V";
      } else if (initialKeyUsage.includes("Derive")) {
        this.modeOfUse = "X";
      } else {
        this.modeOfUse = "N";
      }
    },
  },
};
</script>

<style scoped>
.optional-blocks-text {
  margin-top: 1rem;
}
</style>
