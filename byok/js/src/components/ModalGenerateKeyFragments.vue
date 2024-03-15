<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>Generate Key Fragment</p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul
        v-if="fragments.length === 0 && !selectingKey"
        class="wizard-page-list"
      >
        <li>
          <span>Number of fragments required to recreate key (M)</span>
          <input
            v-model.number="mofnM"
            class="input button-wide"
            type="number"
            min="2"
            max="12"
            step="1"
          />
        </li>
        <li>
          <span>Number of fragments total (N)</span>
          <input
            v-model.number="mofnN"
            class="input button-wide"
            type="number"
            min="2"
            max="24"
            step="1"
          />
        </li>
        <li class="form-switch">
          <span>Load fragments to smart cards</span>
          <input
            id="flexSwitchCheckChecked"
            v-model="wantEncrypted"
            class="form-check-input"
            type="checkbox"
            role="switch"
          />
        </li>
        <li class="form-switch">
          <span>Fragment key in key table</span>
          <input
            id="flexSwitchCheckChecked"
            v-model="isKeySlot"
            class="form-check-input"
            type="checkbox"
            role="switch"
          />
        </li>
        <li v-if="!isKeySlot">
          <span>Key usage</span>
          <select v-model="modifier" class="button button-wide">
            <option value="null">Select a key usage</option>
            <option
              v-for="(alias, modifier) in modifierAliases"
              :key="modifier"
              :value="modifier"
            >
              {{ alias }}
              ({{ toHexString(modifier) }})
            </option>
          </select>
        </li>
        <li v-if="!isKeySlot">
          <span>Major Key</span>
          <select v-model="majorKey" class="button button-wide">
            <option value="null">Select a major key</option>
            <option v-if="mfkLoaded" value="MFK">MFK</option>
            <option v-if="pmkLoaded" value="PMK">PMK</option>
          </select>
        </li>
      </ul>

      <modal-load-data v-if="selectingKey && !isKeySlot" v-model="keyBlock" />

      <modal-choose-key-slot
        v-if="selectingKey && isKeySlot && slot === null"
        hide-select-next
        select-sym-mode
        :key-type="isGpMode() ? '' : 'symmetric'"
        @input="
          slot = $event;
          handleGenerateFragments();
        "
      />

      <div v-if="warn">
        <p class="proceed-text">
          You are about to display a key fragment. Do you wish to proceed?
        </p>
      </div>

      <div v-if="fragments.length > 0 && !warn" class="fragment-result">
        <div v-if="!wantEncrypted">
          <key-block
            :heading="`Fragment ${fragmentIndex + 1}`"
            :file-name="`fragment-${fragmentIndex + 1}`"
            :key-block="fragments[fragmentIndex].fragment"
          />
        </div>
        <div v-if="wantEncrypted">
          <ul class="wizard-page-list">
            <li>
              <span>Status:</span>
              <span
                v-if="!fragmentStored"
                :class="cardPresent ? 'text-success' : 'text-danger'"
                >{{ smartCardStatus }}</span
              >
              <span v-if="fragmentStored" class="text-success"
                >Fragment {{ fragmentIndex + 1 }} stored</span
              >
            </li>
            <li>
              <loading-spinner
                class="loading-spinner"
                :loading="storingToCard"
              />
              <button
                class="button blue-button"
                :disabled="!canStoreFragment"
                @click="storeFragment"
              >
                <i class="fa fa-sim-card" />
                Store fragment {{ fragmentIndex + 1 }}
              </button>
            </li>
          </ul>
        </div>
        <ul class="wizard-page-list">
          <li>
            Fragment number: <span>{{ fragmentIndex + 1 }} of {{ mofnN }}</span>
          </li>
          <li>
            Fragment checksum:
            <span class="checksum">{{ fragments[fragmentIndex].kcv }}</span>
          </li>
          <li>
            Key checksum:
            <span class="checksum">{{ fragmentsKeyChecksum }}</span>
          </li>
        </ul>
      </div>
    </template>

    <template #footer>
      <button
        v-if="
          fragmentIndex !== fragments.length - 1 &&
          !warn &&
          !selectingKey &&
          !isKeySlot
        "
        class="button icon-text-button"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-times" />
        Close
      </button>

      <button
        v-if="fragments.length === 0 && !warn && !selectingKey"
        :disabled="handleGetKeyButtonDisabled"
        class="button blue-button"
        @click="handleGetKey"
      >
        {{ isKeySlot ? "Choose key slot" : "Load key block" }}
      </button>

      <button
        v-if="fragments.length === 0 && !warn && selectingKey && !isKeySlot"
        :disabled="!(keyBlock || slot !== null)"
        class="button blue-button"
        @click="handleGenerateFragments"
      >
        Fragment key
      </button>

      <button v-if="warn" class="button blue-button" @click="warn = false">
        Proceed
      </button>

      <button
        v-if="
          fragments.length > 0 &&
          !warn &&
          fragmentIndex !== fragments.length - 1
        "
        class="button blue-button"
        :disabled="wantEncrypted && !fragmentStored"
        @click="handleNextFragment"
      >
        Next fragment
      </button>

      <button
        v-if="fragmentIndex === fragments.length - 1 && !warn"
        class="button blue-button icon-text-button"
        :disabled="wantEncrypted && !fragmentStored"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-check" />
        Finish
      </button>
    </template>
  </modal-base>
</template>

<script>
import "@/assets/wizard-page.css";
import { modifierAliases } from "@/utils/models.js";
import { toHexString } from "@/utils/misc.js";
import KeyBlock from "@/components/KeyBlock.vue";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import ModalBase from "@/components/ModalBase.vue";
import ModalLoadData from "@/components/ModalLoadData.vue";
import ModalChooseKeySlot from "@/components/ModalChooseKeySlot.vue";

export default {
  components: {
    KeyBlock,
    LoadingSpinner,
    ModalBase,
    ModalLoadData,
    ModalChooseKeySlot,
  },
  inject: ["getSessionId", "isGpMode"],
  data: function () {
    return {
      mofnM: 2,
      mofnN: 3,
      isKeySlot: true,
      keyBlock: null,
      slot: null,
      wantEncrypted: true, // whether to load to smart card
      fragments: [],
      fragmentIndex: 0,
      combinedKeyChecksum: null,
      warn: false,
      selectingKey: false,
      modifier: null,
      majorKey: null,
      modifierAliases,
      smartCardStatus: "Loading",
      smartCardStatusInterval: null,
      storingToCard: false,
      fragmentStored: false,
      mfkLoaded: false,
      pmkLoaded: false,
    };
  },
  computed: {
    handleGetKeyButtonDisabled: function () {
      let m = parseInt(this.mofnM);
      let n = parseInt(this.mofnN);
      let modifier = parseInt(this.modifier);
      return !(
        m >= 2 &&
        m <= 12 &&
        n >= 2 &&
        n <= 24 &&
        (this.isKeySlot ||
          (modifier >= 0x00 && modifier <= 0x1f && this.majorKey))
      );
    },
    cardPresent: function () {
      return this.smartCardStatus && this.smartCardStatus === "Card present";
    },
    canStoreFragment: function () {
      return this.cardPresent && !this.fragmentStored;
    },
  },
  mounted: async function () {
    let url = `/clusters/sessions/${this.getSessionId()}/major-keys`;
    let data = await this.$httpV2.get(url, {
      errorContextMessage: "Failed to get major key status",
    });
    let majorKeys = data.majorKeys;
    let pmk = majorKeys.find((x) => x.name === "PMK");
    let mfk = majorKeys.find((x) => x.name === "MFK");
    this.pmkLoaded = pmk.loaded;
    this.mfkLoaded = mfk.loaded;
  },
  beforeUnmount: function () {
    clearInterval(this.smartCardStatusInterval);
  },
  methods: {
    toHexString,
    handleGetKey: function () {
      this.selectingKey = true;
    },
    handleGenerateFragments: function () {
      let url = `clusters/sessions/${this.getSessionId()}/keyblock/fragment`;
      if (this.isKeySlot) {
        let table = this.isGpMode() ? "keytable" : "keytable/symmetric";
        url = `clusters/sessions/${this.getSessionId()}/${table}/${
          this.slot
        }/fragment`;
      }

      let body = {
        m: this.mofnM,
        n: this.mofnN,
        encrypted: this.wantEncrypted,
      };
      if (!this.isKeySlot) {
        body.key = {
          keyBlock: this.keyBlock,
          modifier: this.modifier,
          majorKey: this.majorKey,
        };
      }

      this.$httpV2
        .post(url, body, {
          errorContextMessage: "Failed to generate key fragments",
        })
        .then((data) => {
          this.warn = !this.wantEncrypted;
          this.fragments = data.fragments;
          this.fragmentsKeyChecksum = data.kcv;
        });
      this.selectingKey = false;
      if (this.wantEncrypted) {
        clearInterval(this.smartCardStatusInterval);
        this.smartCardStatusInterval = setInterval(
          () =>
            window.fxctx.keys.smartCardGetStatus().then((result) => {
              this.smartCardStatus = result.value;
            }),
          [1000],
        );
      }
    },
    storeFragment: async function () {
      this.storingToCard = true;
      window.fxctx.keys
        .smartCardSetFragment(this.fragments[this.fragmentIndex].fragment)
        .then((result) => {
          if (result.success) {
            this.fragmentStored = true;
          } else {
            this.smartCardStatus = result.msg;
            this.$bus.emit("toaster", { message: result.msg, type: "error" });
          }
        })
        .catch((error) => {
          this.smartCardStatus = error;
          this.$bus.emit("toaster", { message: error, type: "error" });
        })
        .finally(() => {
          this.storingToCard = false;
          clearInterval(this.smartCardStatusInterval);
        });
    },
    handleNextFragment: function () {
      this.fragmentStored = false;
      this.warn = !this.wantEncrypted;
      this.fragments[this.fragmentIndex] = null;
      this.fragmentIndex++;
      this.smartCardStatus = "Loading";
      if (this.wantEncrypted) {
        clearInterval(this.smartCardStatusInterval);
        this.smartCardStatusInterval = setInterval(
          () =>
            window.fxctx.keys.smartCardGetStatus().then((result) => {
              this.smartCardStatus = result.value;
            }),
          [1000],
        );
      }
    },
  },
};
</script>

<style scoped>
.proceed-text {
  margin-bottom: 0;
}

.fragment-result {
  display: grid;
  grid-template-columns: 50% calc(50% - 1rem);
  grid-gap: 1rem;
  align-items: center;
}

.fragment-text > span:nth-child(4n)::after {
  content: " ";
}

.show-hide {
  width: 100%;
}
</style>
