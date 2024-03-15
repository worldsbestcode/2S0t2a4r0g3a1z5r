<template>
  <div class="slot-picker-wrapper">
    <table class="slot-table">
      <thead>
        <tr>
          <th class="slot-slot">Slot</th>
          <th>Label</th>
          <th class="slot-key-type">Key Type</th>
          <th class="slot-status">Status</th>
          <th class="slot-select">Select</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="keys.length === 0 && !loading">
          <td class="no-slots-found" colspan="5">No key slots found</td>
        </tr>

        <tr v-for="key in keys" :key="key.slot">
          <td>{{ key.slot }}</td>
          <td :title="key.label">{{ key.label }}</td>
          <td :title="key.type === 'Empty' ? '' : key.type">
            {{ key.type === "Empty" ? "" : key.type }}
          </td>
          <td>
            <div :class="`key-status ${statusClass(key)}`">
              {{ statusText(key) }}
            </div>
          </td>
          <td>
            <button
              class="button blue-button"
              :disabled="selectDisabled(key)"
              @click="selectKeySlot(key)"
            >
              <i class="fas fa-check" />
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <nav class="page-nav">
      <loading-spinner class="loading-spinner" :loading="loading" />
      <button
        class="button previous"
        :disabled="pageNumber == 1"
        @click="pageNumber--"
      >
        <i class="fas fa-arrow-left" />
      </button>
      <input
        type="number"
        class="input page-number"
        :value="pageNumber"
        @input="handlePageInput"
      />
      <button
        class="button next"
        :disabled="pageNumber == totalPages"
        @click="pageNumber++"
      >
        <i class="fas fa-arrow-right" />
      </button>

      <button
        v-if="!hideSelectNext && !selectKekMode && !selectPrivateMode"
        class="button blue-button next-open-slot"
        @click="selectKeySlot({ slot: -1 })"
      >
        Select first empty slot
      </button>
    </nav>
  </div>
</template>

<script>
import _ from "lodash";
import { isSymmetric, isPrivate } from "@/utils/models.js";

import LoadingSpinner from "@/components/LoadingSpinner.vue";

function isImmutable(key) {
  return key.securityUsage.includes("Immutable");
}

function isKek(key) {
  return (
    isSymmetric(key.type) &&
    key.modifier === 0 &&
    (key.usage.includes("Wrap") || key.usage.includes("Encrypt"))
  );
}

export default {
  name: "WizardPageChooseKeySlot",
  title: "Select a Key Slot",
  description: "Select a key slot",
  components: {
    "loading-spinner": LoadingSpinner,
  },
  inject: ["getSessionId"],
  props: {
    hideSelectNext: {
      type: Boolean,
      default: false,
    },
    selectKekMode: {
      type: Boolean,
      default: false,
    },
    selectPrivateMode: {
      type: Boolean,
      default: false,
    },
    keyType: {
      type: [String, Function],
      default: "",
    },
  },
  defaultData: function () {
    return {
      slot: {
        value: null,
        wizardSummaryText: "Slot number",
      },
      keyInformation: {
        value: null,
      },
    };
  },
  data: function () {
    return {
      loading: false,
      previousPageNumberRequested: null,
      pageNumber: 1,
      totalPages: 1,
      keys: [],
    };
  },
  watch: {
    pageNumber: function () {
      this.fillSlots();
    },
  },
  mounted: function () {
    this.fillSlots();
  },
  methods: {
    handlePageInput: function (event) {
      let value = Number(event.target.value);
      event.target.value = _.clamp(value, 1, this.totalPages);
      this.pageNumber = event.target.value;
    },
    statusClass: function (key) {
      if (this.selectKekMode) {
        if (isKek(key)) {
          return "green";
        } else {
          return "red";
        }
      } else if (this.selectPrivateMode) {
        if (isPrivate(key.type)) {
          return "green";
        } else {
          return "red";
        }
      } else {
        if (key.type === "Empty") {
          return "green";
        } else {
          return "red";
        }
      }
    },
    statusText: function (key) {
      if (this.selectKekMode) {
        if (key.type === "Empty") {
          return "Empty";
        } else if (isKek(key)) {
          return "KEK";
        } else {
          return "Not KEK";
        }
      } else if (this.selectPrivateMode) {
        if (key.type === "Empty") {
          return "Empty";
        } else if (isPrivate(key.type)) {
          return "Private";
        } else {
          return "Not private";
        }
      } else {
        if (key.type === "Empty") {
          return "Empty";
        } else if (isImmutable(key)) {
          return "Immutable";
        } else {
          return "Loaded";
        }
      }
    },
    selectDisabled: function (key) {
      if (this.selectKekMode) {
        return !isKek(key);
      } else if (this.selectPrivateMode) {
        return !isPrivate(key.type);
      } else {
        if (key.type === "Empty") {
          return false;
        } else {
          return isImmutable(key);
        }
      }
    },
    selectKeySlot: function (key) {
      this.slot = key.slot;
      this.keyInformation = key;
      this.nextPage();
    },
    fillSlots: async function () {
      let pageNumber = this.pageNumber;
      if (this.previousPageNumberRequested === pageNumber) {
        return;
      }

      this.loading = true;

      this.previousPageNumberRequested = pageNumber;

      let url = `/clusters/sessions/${this.getSessionId()}/keytable`;
      let keyType =
        typeof this.keyType === "function" ? this.keyType() : this.keyType;
      if (keyType) {
        url += `/${keyType}`;
      }
      let config = {
        params: {
          page: pageNumber,
          pageCount: 10,
          includeEmpty: true,
        },
        silenceToastError: true,
      };
      this.$httpV2
        .get(url, config)
        .then((data) => {
          if (this.pageNumber === pageNumber) {
            this.totalPages = data.totalPages;
            this.keys = data.keys;
          }
        })
        .catch((error) => {
          this.$bus.emit("toaster", {
            message: `Failed to load the key table: ${error.message}`,
            type: "error",
          });
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style scoped>
.slot-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}

.slot-table thead {
  background-color: #f4f4f4;
  border: 1px solid #eee;
}

.slot-table th {
  text-align: center;
  color: #666;
  padding: 0.5rem;
  border: 1px solid #eee;
  font-weight: 500;
  white-space: nowrap;
}

.slot-table tbody {
  border: 1px solid #eee;
}

.slot-table tbody tr {
  height: 46px;
}

.slot-table td {
  text-align: center;
  padding: 0.3rem 0.6rem;
  border: 1px solid #eee;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slot-slot {
  width: 60px;
}

.slot-key-type {
  width: 120px;
}

.slot-status {
  width: 120px;
}

.slot-select {
  width: 65px;
}

.no-slots-found {
  text-align: center;
}

.page-nav {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}

.previous {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.page-number {
  align-self: stretch;
  border-radius: 0;
  border-left: 0;
  border-right: 0;
  text-align: center;
  width: 8ch;
}

/* Remove arrows from type="number" */
.page-number {
  appearance: textfield;
}
.page-number::-webkit-outer-spin-button,
.page-number::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.next {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.next-open-slot {
  margin-left: 1rem;
}

.key-status {
  border: 1px solid;
  border-radius: 3px;
  text-align: center;
  padding: 0.2rem 0.6rem;
}

.green {
  background-color: #ecf5ec;
  color: #769976;
  border-color: #c6dfca;
}

.red {
  background-color: #f5ecec;
  color: #997676;
  border-color: #dfc6c6;
}

.loading-spinner {
  margin-right: 0.5rem;
}
</style>
