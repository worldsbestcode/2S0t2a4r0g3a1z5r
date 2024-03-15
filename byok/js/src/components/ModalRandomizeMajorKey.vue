<template>
  <modal-base @esc="$emit('closeModal')">
    <template #header>
      <p>
        Randomize
        {{ (majorKey.alias && majorKey.alias.toLowerCase()) || majorKey.name }}
      </p>
      <button @click="$emit('closeModal')">
        <i class="fa fa-times" />
      </button>
    </template>
    <template #main>
      <ul v-if="displayFragments === false" class="wizard-page-list">
        <li v-if="majorKey.name === 'KEK'">
          <span>Fragment type</span>
          <select v-model="type" class="button button-wide">
            <option value="3TDES">3TDES</option>
            <option value="AES-256">AES-256</option>
          </select>
        </li>
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
      </ul>

      <div v-if="displayFragments === true" class="fragment-result">
        <ul class="wizard-page-list">
          <li>
            Status:
            <span v-if="customStatus" :class="customStatus.class">{{
              customStatus.text
            }}</span>
            <span
              v-else
              :class="cardPresent ? 'text-success' : 'text-danger'"
              >{{ smartCardStatus }}</span
            >
          </li>
          <button
            :disabled="!cardPresent || fragmentStored"
            class="store-fragment-button button blue-button icon-text-button"
            @click="handleStoreFragment"
          >
            <i class="fa fa-sim-card" />
            Store fragment {{ fragmentIndex + 1 }}
          </button>
        </ul>

        <ul class="wizard-page-list">
          <li>
            Fragment number:
            <span>{{ fragmentIndex + 1 }} of {{ mofnN }}</span>
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
      <button class="button icon-text-button" @click="$emit('closeModal')">
        <i class="fa fa-times" />
        Close
      </button>

      <button
        v-if="displayFragments === false"
        class="button blue-button icon-text-button"
        @click="handleRandomize"
      >
        <i class="fa fa-random" />
        Randomize
      </button>

      <button
        v-if="
          displayFragments === true && fragmentIndex !== fragments.length - 1
        "
        :disabled="!fragmentStored"
        class="button blue-button icon-text-button"
        @click="handleNextFragment"
      >
        <i class="fas fa-arrow-right" />
        Next fragment
      </button>

      <button
        v-if="fragmentIndex === fragments.length - 1"
        class="button blue-button icon-text-button"
        :disabled="!fragmentStored"
        @click="$emit('closeModal')"
      >
        <i class="fa fa-check" />
        Finish
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
  inject: ["getSessionId", "isGpMode", "isExcryptTouch"],
  props: {
    majorKey: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      type: "AES-256",
      mofnM: 2,
      mofnN: 3,
      fragments: [],
      fragmentIndex: 0,
      fragmentsKeyChecksum: null,
      displayFragments: false,
      fragmentStored: false,
      smartCardStatusInterval: null,
      smartCardStatus: "Loading",
      customStatus: null,
    };
  },
  computed: {
    cardPresent: function () {
      return this.smartCardStatus === "Card present";
    },
  },
  beforeUnmount: function () {
    clearInterval(this.smartCardStatusInterval);
  },
  methods: {
    handleRandomize: function () {
      let url = `/clusters/sessions/${this.getSessionId()}/major-keys/${
        this.majorKey.name
      }/randomize`;
      let body = {
        m: this.mofnM,
        n: this.mofnN,
      };
      if (this.majorKey.name === "KEK") {
        body.type = this.type;
      }
      this.$httpV2
        .post(url, body, {
          errorContextMessage: `Failed to randomize ${this.majorKey.name}`,
        })
        .then(async (data) => {
          this.fragments = data.fragments;
          this.fragmentsKeyChecksum = data.kcv;
          this.$emit("refreshMajorKeys");

          if (await this.isExcryptTouch()) {
            this.displayFragments = true;
            this.smartCardStatusIntervalFunction();
            this.smartCardStatusInterval = setInterval(
              this.smartCardStatusIntervalFunction,
              1000,
            );
          } else {
            this.$emit("closeModal");
          }
        })
        .catch(() => {
          this.$emit("closeModal");
          this.$emit("refreshMajorKeys");
        });
    },
    handleStoreFragment: async function () {
      window.fxctx.keys
        .smartCardSetFragment(this.fragments[this.fragmentIndex].fragment)
        .then((result) => {
          if (result.success) {
            this.fragmentStored = true;
            let message = `Fragment ${this.fragmentIndex + 1} stored`;
            this.customStatus = {
              text: message,
              class: "text-success",
            };
            this.$bus.emit("toaster", { message: message, type: "success" });
          } else {
            this.customStatus = {
              text: result.msg,
              class: "text-danger",
            };
            this.$bus.emit("toaster", { message: result.msg, type: "error" });
          }
        })
        .catch((error) => {
          this.$bus.emit("toaster", { message: error, type: "error" });
        });
    },
    smartCardStatusIntervalFunction: function () {
      window.fxctx.keys.smartCardGetStatus().then((result) => {
        this.smartCardStatus = result.value;
      });
    },
    handleNextFragment: function () {
      this.fragmentStored = false;
      this.customStatus = null;
      this.fragmentIndex++;
    },
  },
};
</script>

<style scoped>
.fragment-result {
  display: grid;
  grid-template-columns: 50% calc(50% - 1rem);
  grid-gap: 1rem;
  align-items: center;
}

.store-fragment-button {
  width: calc(100% + 2px);
  margin: -1px;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
