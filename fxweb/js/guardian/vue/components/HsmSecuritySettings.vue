<style>
  .has-v-select {
    overflow: visible;
  };

  .warning-text {
    color: red;
  }
</style>

<template>
<div>
  <div class="guardian-tab-element">
    <div :class="{ 'has-error': hasKeyBlockError }" >
      <label class="panel-title">
        Key Block Policy
      </label>

      <fx-checkbox
        v-model="localSettings.keyBlockPolicy.cryptogram"
        description="Cryptograms">
      </fx-checkbox>
      <fx-checkbox
        v-model="localSettings.keyBlockPolicy.akb"
        description="AKB Format">
      </fx-checkbox>
      <fx-checkbox
        v-model="localSettings.keyBlockPolicy.tr31"
        description="ANSI Key Blocks (TR-31)">
      </fx-checkbox>

      <label v-if="hasKeyBlockError" class="warning-text">
        At least one key block policy must be allowed.
      </label>
    </div>
  </div>

  <div class="guardian-tab-element">
    <label class="panel-title">
      Weak PIN Checking
    </label>

    <fx-checkbox
      v-model="localSettings.pinCheck.duplicate"
      description="Check for duplicate (Ex: 1111)">
    </fx-checkbox>
    <fx-checkbox
      v-model="localSettings.pinCheck.ascend"
      description="Check for ascending series (Ex: 1234)">
    </fx-checkbox>
    <fx-checkbox
      v-model="localSettings.pinCheck.descend"
      description="Check for descending series (Ex: 4321)">
    </fx-checkbox>
  </div>

  <div class="guardian-tab-element" v-if="!unavailableFields.includes('hmac')">
    <label class="panel-title">
      HMAC Settings
    </label>

    <fx-hex-input
      v-model="localSettings.hmac.salt"
      description="Salt">
    </fx-hex-input>

    <fx-number
      v-model="localSettings.hmac.minIterations"
      description="Minimum iteration count"
      min="1"
      max="10000">
    </fx-number>

    <fx-number
      v-model="localSettings.hmac.leftMask"
      description="Left output mask"
      min="0"
      max="6">
    </fx-number>

    <fx-number
      v-model="localSettings.hmac.rightMask"
      description="Right output mask"
      min="0"
      max="4">
    </fx-number>

    <fx-number
      v-model="localSettings.hmac.outputLength"
      description="Output length"
      min="16"
      max="48">
    </fx-number>
  </div>

  <div class="guardian-tab-element has-v-select">
    <label class="panel-title">
      Miscellaneous
    </label>

    <fx-checkbox
      v-model="localSettings.distressPIN"
      description="Enable Distress Check (PIN backwards)">
    </fx-checkbox>

    <fx-checkbox
      v-model="localSettings.fixStandardLineFeed"
      description="Remove linefeed characters from end of Standard commands">
    </fx-checkbox>

    <fx-checkbox
      v-model="localSettings.rsaLegacy"
      description="Use legacy RSA functionality">
    </fx-checkbox>

    <fx-checkbox v-if="!unavailableFields.includes('allowWeakKeys')"
      v-model="localSettings.allowWeakKeys"
      description="Allow loading weak keys">
    </fx-checkbox>

    <fx-checkbox
      v-model="localSettings.macVerify8Char"
      description="Limit MAC verification to 8 characters">
    </fx-checkbox>

    <fx-checkbox
      v-model="localSettings.rsaBlinding"
      description="RSA blinding">
    </fx-checkbox>

    <fx-checkbox
      v-model="localSettings.legacyModifierCardMod"
      description="Legacy modifier for dynamic card value generation/modification">
    </fx-checkbox>

    <fx-checkbox v-if="!unavailableFields.includes('trackFailedCommands')"
      v-model="localSettings.trackFailedCommands"
      description="Enable tracking of failed commands">
    </fx-checkbox>

    <fx-number
      v-model="localSettings.checkDigitLength"
      description="Check Digit Length"
      min="4"
      max="6">
    </fx-number>

    <div>
      <label>
        Decimalization Table Format
      </label>
      <v-select v-model="localSettings.decimalTableFormat" :options="decimalTableFormats">
      </v-select>
    </div>

  </div>

  <div class="guardian-tab-element">
    <button class="btn" @click="saveSettings">
      Save
    </button>
  </div>

</div>
</template>

<script>

export default {
  props: [
    'settings',
  ],
  computed: {
    hasKeyBlockError: function () {
      var policy = this.localSettings.keyBlockPolicy;
      return !policy.cryptogram &&
             !policy.akb &&
             !policy.tr31;
    },
  },
  data () {
    return {
      localSettings: Object.assign({}, this.settings),
      decimalTableFormats: ['Clear', 'Encrypted'],
      unavailableFields: this.settings.unavailableFields,
    };
  },
  methods: {
    saveSettings: function () {
      var savedSettings = this.localSettings;
      savedSettings.unavailableFields = this.unavailableFields;
      this.$emit('save-settings', savedSettings);
    },
  },
};
</script>
