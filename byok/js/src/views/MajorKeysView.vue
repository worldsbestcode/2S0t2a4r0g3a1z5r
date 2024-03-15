<template>
  <div class="management-page">
    <header>
      <p>Major Keys</p>
      <close-button @click="$emit('close')" />
    </header>

    <ul class="major-key-list">
      <loading-spinner
        v-if="loading"
        class="loading-spinner"
        :loading="loading"
      />
      <li v-for="majorKey in majorKeys" :key="majorKey.name" class="major-key">
        <div class="major-key-name">
          {{ keyName(majorKey) }}
        </div>
        <div class="major-key-middle">
          <div>
            <span v-if="majorKey.sessionInfo" class="text-warning">
              {{ majorKey.sessionInfo.have }} /
              {{ majorKey.sessionInfo.want }}
              {{ majorKey.sessionInfo.type.toLowerCase() }} loaded
            </span>
            <span
              v-else
              :class="majorKey.loaded ? 'text-success' : 'text-danger'"
            >
              {{ majorKey.loaded ? "Loaded" : "Not loaded" }}
            </span>
          </div>
          <div v-if="majorKey.kcv" class="checksum-container">
            Key checksum:
            <span class="checksum">{{ majorKey.kcv }}</span>
          </div>
        </div>
        <div class="major-key-end">
          <button
            data-bs-toggle="dropdown"
            class="button blue-button"
            @click="currentMajorKey = majorKey"
          >
            <i class="fa fa-caret-down" />
          </button>
          <ul class="dropdown-menu">
            <li v-if="majorKey.loaded">
              <button
                class="dropdown-item-custom"
                @click="showMajorKeyInfo = true"
              >
                <i class="fa fa-info-circle" />
                {{ keyName(majorKey) }} info
              </button>
            </li>

            <div v-if="!majorKey.loaded && !majorKey.sessionInfo">
              <li v-if="!majorKey.hideFragments">
                <button
                  class="dropdown-item-custom"
                  @click="showRandomizeMajorKey = true"
                >
                  <i class="fa fa-random" />
                  Randomize {{ keyName(majorKey) }}
                </button>
              </li>
              <li v-if="excryptTouch && !majorKey.hideFragments">
                <button
                  class="dropdown-item-custom"
                  @click="showLoadMajorKeyWithFragments = true"
                >
                  <i class="fa fa-sim-card" />
                  Load {{ keyName(majorKey) }} via smart card fragments
                </button>
              </li>
              <li v-if="excryptTouch">
                <button
                  class="dropdown-item-custom"
                  @click="setWizard('WizardLoadMajorKeyWithComponents')"
                >
                  <i class="fa fa-file-import" />
                  Load {{ keyName(majorKey) }} via XOR components
                </button>
              </li>
            </div>

            <li
              v-if="
                majorKey.sessionInfo &&
                majorKey.sessionInfo.type === 'Fragments'
              "
            >
              <button
                class="dropdown-item-custom"
                @click="showLoadMajorKeyWithFragments = true"
              >
                <i class="fa fa-sim-card" />
                Continue loading smart card fragments
              </button>
            </li>

            <li
              v-if="
                majorKey.sessionInfo &&
                majorKey.sessionInfo.type === 'Components'
              "
            >
              <button
                class="dropdown-item-custom"
                @click="setWizard('WizardLoadMajorKeyWithComponents')"
              >
                <i class="fa fa-file-import" />
                Continue loading XOR components
              </button>
            </li>

            <li v-if="kekLoaded && majorKey.loaded && majorKey.canSwitchKEK">
              <button
                class="dropdown-item-custom"
                @click="showSwitchMajorKey = true"
              >
                <i class="fa fa-exchange-alt" />
                Switch with pending major key
              </button>
            </li>

            <li v-if="majorKey.loaded || majorKey.sessionInfo">
              <button
                class="dropdown-item-custom"
                @click="showClearMajorKey = true"
              >
                <i class="fa fa-eraser"></i>
                Clear {{ keyName(majorKey) }}
              </button>
            </li>
          </ul>
        </div>
      </li>
    </ul>

    <modal-major-key-info
      v-if="showMajorKeyInfo"
      :major-key="currentMajorKey"
      @closeModal="showMajorKeyInfo = false"
    />

    <modal-clear-major-key
      v-if="showClearMajorKey"
      :major-key="currentMajorKey"
      @closeModal="showClearMajorKey = false"
      @refreshMajorKeys="refreshMajorKeys"
    />

    <modal-randomize-major-key
      v-if="showRandomizeMajorKey"
      :major-key="currentMajorKey"
      @closeModal="showRandomizeMajorKey = false"
      @refreshMajorKeys="refreshMajorKeys"
    />

    <modal-load-major-key-with-fragments
      v-if="showLoadMajorKeyWithFragments"
      :major-key="currentMajorKey"
      @closeModal="showLoadMajorKeyWithFragments = false"
      @refreshMajorKeys="refreshMajorKeys"
    />

    <modal-switch-major-key
      v-if="showSwitchMajorKey"
      :pending-major-key="majorKeys.find((x) => x.name === 'KEK')"
      :major-key="currentMajorKey"
      @closeModal="showSwitchMajorKey = false"
      @refreshMajorKeys="refreshMajorKeys"
    />

    <component
      :is="currentWizard"
      v-if="currentWizard"
      :major-key="currentMajorKey"
    />
  </div>
</template>

<script>
import { wizardMixin, wizards } from "@/utils/wizard.js";
import LoadingSpinner from "@/components/LoadingSpinner.vue";
import CloseButton from "@/components/CloseButton.vue";

import ModalMajorKeyInfo from "@/components/ModalMajorKeyInfo.vue";
import ModalClearMajorKey from "@/components/ModalClearMajorKey.vue";
import ModalRandomizeMajorKey from "@/components/ModalRandomizeMajorKey.vue";
import ModalLoadMajorKeyWithFragments from "@/components/ModalLoadMajorKeyWithFragments.vue";
import ModalSwitchMajorKey from "@/components/ModalSwitchMajorKey.vue";

import WizardLoadMajorKeyWithComponents from "@/components/WizardLoadMajorKeyWithComponents.vue";

let allowedMajorKeys = [
  {
    name: "PMK",
    canSwitchKEK: true,
  },
  {
    name: "FTK",
    canSwitchKEK: true,
  },
  {
    name: "MFK",
    canSwitchKEK: true,
  },
  {
    name: "BAK",
  },
  {
    name: "VMK",
    hideFragments: true,
  },
  {
    name: "SCEK",
    hideFragments: true,
  },
  {
    name: "KEK",
    alias: "Pending major key",
  },
];

export default {
  components: {
    "loading-spinner": LoadingSpinner,
    "close-button": CloseButton,
    "modal-major-key-info": ModalMajorKeyInfo,
    "modal-clear-major-key": ModalClearMajorKey,
    "modal-randomize-major-key": ModalRandomizeMajorKey,
    "modal-switch-major-key": ModalSwitchMajorKey,
    ModalLoadMajorKeyWithFragments,
  },
  mixins: [wizardMixin],
  inject: ["getSessionId", "isExcryptTouch"],
  data: function () {
    return {
      wizards: wizards({
        WizardLoadMajorKeyWithComponents,
      }),
      majorKeys: [],
      currentMajorKey: null,
      showMajorKeyInfo: false,
      showClearMajorKey: false,
      showRandomizeMajorKey: false,
      showLoadMajorKeyWithFragments: false,
      showSwitchMajorKey: false,
      loading: true,
      excryptTouch: false,
    };
  },
  computed: {
    kekLoaded: function () {
      return this.majorKeys.find((x) => x.name === "KEK").loaded;
    },
  },
  created: function () {
    this.$bus.on("majorKeyPartialKeyLoad", this.refreshMajorKeys);
  },
  unmounted: function () {
    this.$bus.off("majorKeyPartialKeyLoad", this.refreshMajorKeys);
  },
  mounted: async function () {
    this.initializeMajorKeys();
    this.excryptTouch = await this.isExcryptTouch();
  },
  methods: {
    keyName: function (key) {
      return key.alias || key.name;
    },
    initializeMajorKeys: function () {
      let majorKeysUrl = `/clusters/sessions/${this.getSessionId()}/major-keys`;
      this.$httpV2
        .get(majorKeysUrl, {
          errorContextMessage: "Failed to get major key status",
        })
        .then((data) => {
          this.majorKeys = allowedMajorKeys
            .map((majorKey) => {
              let dataMajorKey = data.majorKeys.find(
                (x) => x.name === majorKey.name,
              );
              return (
                dataMajorKey && {
                  ...majorKey,
                  ...dataMajorKey,
                }
              );
            })
            .filter((_) => _);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    refreshMajorKeys: function () {
      this.loading = true;
      this.majorKeys = [];
      this.initializeMajorKeys();
    },
  },
};
</script>

<style scoped>
.loading-spinner {
  margin: auto;
}

.major-key-list {
  margin: 0;
  padding: 1rem;
  display: grid;
  gap: 1rem;
}

.major-key {
  display: flex;
  background: #f5f5f5;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
  height: 56px;
}

.major-key-name {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  ) !important;
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  border-right: 1px solid var(--border-color);
  font-size: 18px;
  min-width: 80px;
  padding: 1rem;
}

.major-key-middle {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  align-self: center;
}

.major-key-end {
  margin-top: -1px;
  margin-bottom: -1px;
  margin-right: -1px;
}

.major-key-end > button {
  width: 80px;
  height: 100%;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
}

.checksum-container {
  white-space: nowrap;
  padding: 0.3rem 0.6rem;
  background-color: #ecf0f5;
  color: var(--text-color-blue-lighter);
  border: 1px solid #c6d1df;
  border-radius: 3px;
}

.major-key-status {
  font-size: 14px;
}
</style>
