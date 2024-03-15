<template v-slot:KeyManager>
  <div id="key-manager">
    <modal-export-key
      v-if="showExportKeySlot"
      :key-slot="currentKey.slot"
      :type="type"
      @closeModal="showExportKeySlot = false"
    />

    <modal-edit-key
      v-if="showEditKeySlot"
      :current-key="currentKey"
      :key-slot="currentKey.slot"
      :type="type"
      @closeModal="showEditKeySlot = false"
      @refreshTable="refreshTable"
    />

    <modal-delete-key
      v-if="showDeleteKeySlot"
      :key-slot="currentKey.slot"
      :type="type"
      @closeModal="showDeleteKeySlot = false"
      @refreshTable="refreshTable"
    />

    <div id="km-header">
      <button id="km-finished" @click="$emit('close')">
        <i class="fa fa-times"></i> Finished
      </button>
      <p id="km-title">
        Key Table <span>- {{ currentCluster.name }}</span>
      </p>
    </div>

    <div id="km-body">
      <div id="km-query">
        <div id="km-search-bar">
          <p id="km-search-label">Search:</p>
          <input id="km-search-input" v-model="search" />
        </div>
      </div>

      <div id="km-keytable">
        <div id="km-keytable-header">
          <div class="km-key-info">
            <div class="km-slot" @click="startSort('slot')">
              <p class="km-key-labels">Slot<i class="fa fa-sort" /></p>
            </div>
            <div class="km-type" @click="startSort('type')">
              <p class="km-key-labels">Type<i class="fa fa-sort" /></p>
            </div>
            <div
              class="km-majorkey majorkey-padding"
              @click="startSort('majorKey')"
            >
              <p class="km-key-labels">Major Key<i class="fa fa-sort" /></p>
            </div>
            <div class="km-kcv" @click="startSort('kcv')">
              <p class="km-key-labels">KCV<i class="fa fa-sort" /></p>
            </div>
            <div class="km-modifier" @click="startSort('modifier')">
              <p class="km-key-labels">Key Usage<i class="fa fa-sort" /></p>
            </div>
            <div class="km-usage" @click="startSort('usage')">
              <p class="km-key-labels">Usage<i class="fa fa-sort" /></p>
            </div>
            <div class="km-security" @click="startSort('securityUsage')">
              <p class="km-key-labels">Security<i class="fa fa-sort" /></p>
            </div>
            <div class="km-label" @click="startSort('label')">
              <p class="km-key-labels">Label<i class="fa fa-sort" /></p>
            </div>
          </div>
          <div class="km-dropdown-column"></div>
        </div>

        <div id="km-keytable-body" ref="km-keytable-body">
          <div
            v-for="(key, index) in keys"
            :id="'key' + index"
            :key="key.slot"
            class="km-key"
            :style="keyColorAlternator(index)"
          >
            <div class="km-key-info">
              <div class="km-slot">
                <p class="km-key-data">{{ key.slot }}</p>
              </div>
              <div class="km-type">
                <p class="km-key-data">{{ key.type }}</p>
              </div>
              <div class="km-majorkey majorkey-padding">
                <p class="km-key-data">{{ key.majorKey }}</p>
              </div>
              <div class="km-kcv">
                <p class="km-key-data">{{ key.kcv }}</p>
              </div>
              <div class="km-modifier">
                <p
                  v-if="key.modifier >= 0 && key.modifier <= 31"
                  class="km-key-data"
                >
                  {{ modifierAliases[key.modifier] }}
                  ({{ toHexString(key.modifier) }})
                </p>
              </div>
              <div class="km-usage">
                <p class="km-key-data">{{ key.usage.join("/") }}</p>
              </div>
              <div class="km-security">
                <p class="km-key-data">{{ key.securityUsage.join("/") }}</p>
              </div>
              <div class="km-label">
                <p class="km-key-data">{{ key.label }}</p>
              </div>
            </div>
            <div class="km-dropdown-column dropdown dropup">
              <button
                id="dropdownMenuButton1"
                class="button blue-button"
                type="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                @click="currentKey = key"
              >
                <i :ref="'key' + key.slot" class="fa fa-cog"></i>
              </button>

              <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                <li
                  v-if="showExportButton(key)"
                  class="dropdown-item"
                  @click="showExportKeySlot = true"
                >
                  Export {{ keyTypeString(key.type) }}
                </li>
                <li
                  v-if="key.type !== 'Diebold'"
                  class="dropdown-item"
                  @click="showEditKeySlot = true"
                >
                  Edit {{ keyTypeString(key.type) }}
                </li>
                <li class="dropdown-item" @click="showDeleteKeySlot = true">
                  Delete {{ keyTypeString(key.type) }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div id="km-footer">
        <p id="km-footer-label">
          Showing {{ pageStart }} to {{ pageEnd }} of {{ totalItems }} entries
        </p>
        <nav class="page-nav">
          <button
            class="button previous"
            :disabled="pageNumber === 1"
            @click="retrieveKeys(pageNumber - 1)"
          >
            <i class="fas fa-arrow-left" />
          </button>
          <p class="page-display">{{ pageNumber }}</p>
          <button
            class="button next"
            :disabled="pageNumber >= totalPages"
            @click="retrieveKeys(pageNumber + 1)"
          >
            <i class="fas fa-arrow-right" />
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { modifierAliases } from "@/utils/models.js";
import { toHexString } from "@/utils/misc.js";
import ModalExportKey from "@/components/ModalExportKey.vue";
import ModalEditKey from "@/components/ModalEditKey.vue";
import ModalDeleteKey from "@/components/ModalDeleteKey.vue";

export default {
  name: "KeyManager",
  components: {
    "modal-export-key": ModalExportKey,
    "modal-edit-key": ModalEditKey,
    "modal-delete-key": ModalDeleteKey,
  },
  props: {
    financial: Boolean,
    type: String,
    currentCluster: Object,
  },
  data: function () {
    return {
      lineHeight: "1",
      show: null,
      orderTracker: {
        orderBy: "slot",
        ascending: true,
      },
      modifierAliases,
      selectedKey: null,
      keys: [],
      search: null,
      showKeyCountDropdown: false,
      showKeyDropdown: false,
      pageNumber: 1,
      totalPages: null,
      totalItems: 0,
      showExportKeySlot: false,
      showEditKeySlot: false,
      showDeleteKeySlot: false,
      currentKey: null,
    };
  },
  computed: {
    pageStart: function () {
      if (!this.keys.length) {
        return 0;
      } else {
        return 10 * (this.pageNumber - 1) + 1;
      }
    },
    pageEnd: function () {
      let numberOfItems = this.pageNumber * 10;
      return numberOfItems < this.totalItems ? numberOfItems : this.totalItems;
    },
  },
  watch: {
    search: function () {
      this.retrieveKeys();
    },
  },
  mounted: function () {
    this.retrieveKeys();
  },
  methods: {
    toHexString: toHexString,
    keyColorAlternator: function (index) {
      return index % 2 === 0
        ? { backgroundColor: "#f9f9f9", lineHeight: this.lineHeight }
        : { backgroundColor: "#fff", lineHeight: this.lineHeight };
    },
    close: function () {
      this.show = null;
      this.selectedKey = null;
    },

    retrieveKeys: async function (pageNumber) {
      this.pageNumber = pageNumber || this.pageNumber;

      let config = {
        params: {
          pageCount: 10,
          page: this.pageNumber,
          orderBy: this.orderTracker.orderBy,
          ascending: this.orderTracker.ascending,
          search: this.search,
        },
        errorContextMessage: "Failed to fetch keys",
      };

      let url =
        "/clusters/sessions/" + this.currentCluster.session.id + "/keytable";
      if (this.financial) {
        url += "/" + this.type.toLowerCase();
      }

      this.$httpV2.get(url, config).then((data) => {
        this.keys = data.keys;
        this.totalPages = data.totalPages;
        this.totalItems = data.totalItems;
      });
    },

    startSort: function (orderBy) {
      if (this.orderTracker.orderBy === orderBy) {
        this.orderTracker.ascending = !this.orderTracker.ascending;
      } else {
        this.orderTracker = {
          orderBy,
          ascending: true,
        };
      }
      this.retrieveKeys();
    },
    updateShow: function (payload) {
      this.show = this.show === payload.show ? null : payload.show;
      if (payload.key) {
        this.selectedKey = payload.key;
      }
    },
    keyTypeString: function (type) {
      if (type === "Diebold" || type === "Certificate") {
        return type;
      } else {
        return "Key";
      }
    },

    showExportButton: function (key) {
      return (
        key.type !== "Certificate" &&
        key.type !== "Diebold" &&
        !key.securityUsage.includes("Sensitive")
      );
    },

    refreshTable: function () {
      this.retrieveKeys();
      this.$emit("refreshTableInformation");
    },
  },
};
</script>

<style scoped>
p {
  margin: 0px;
}

.modal-close:hover,
.modal-cancel:hover,
.modal-submit:hover,
#km-finished:hover,
.fa-sort:hover,
.fa-cog:hover,
.dropdown-item:hover {
  cursor: pointer;
}

.km-key-dropdown-menu > p:hover {
  background-color: #f9f9f9;
}

#key-manager {
  position: fixed;
  top: 0px;
  left: 0px;
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
  font-size: 13px;
  z-index: 1;
}

#km-header {
  font-size: 18px;
  width: 100%;
  padding: 15px;
}

#km-finished {
  float: right;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  color: var(--text-color);
  font-size: 15px;
  width: 200px;
  line-height: 30px;
  padding: 0px;
  border: 1px solid var(--border-color);
  border-bottom-color: #b3b3b3;
  border-radius: 3px;
}

#km-finished:active {
  background: linear-gradient(
    180deg,
    rgba(233, 233, 233, 1) 0%,
    rgba(229, 229, 229, 1) 35%,
    rgba(226, 226, 226, 1) 100%
  );
  border-bottom-color: var(--border-color);
}

#km-title {
  line-height: 30px;
}

#km-title > span {
  color: #3c8dbc;
  font-size: 13px;
}

#km-body {
  width: calc(100% - 30px);
  height: calc(100% - 77px) !important;
  padding: 5px 15px 25px 15px;
  margin: 0px 15px 15px 15px;
  height: 615px;
  border: 1px solid var(--border-color);
  border-radius: 3px;
  background-color: #fff;
}

#km-query {
  margin: 10px 0px;
  height: 29px;
}

#km-search-bar {
  float: right;
}

#km-search-label {
  display: inline-block;
}

#km-search-input {
  line-height: 1;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 3px;
}

#km-keytable {
  height: calc(100% - 80px);
  width: calc(100% - 2px);
  border: 1px solid #eee;
  margin-top: 10px;
}

#km-keytable-header {
  display: flex;
  background: linear-gradient(
    180deg,
    rgba(249, 249, 249, 1) 0%,
    rgba(241, 241, 241, 1) 35%,
    rgba(238, 238, 238, 1) 100%
  );
  height: 54px;
  border-bottom: 1px solid #eee;
}

.fa-sort {
  line-height: 1;
  padding-left: 6px;
}

#km-keytable-body {
  height: calc(100% - 54px);
}

.km-key-info {
  cursor: pointer;
  display: flex;
  height: 100%;
  width: 100%;
  border-right: 1px solid #eee;
}

.km-key-info > div {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  border-right: 1px solid #eee;
}

.km-key-info > div:last-of-type {
  border-right: 0px;
}

.km-key-labels {
  display: flex;
  align-items: center;
  height: 100%;
  padding-right: 5px;
}

.km-key-data {
  padding: 0px 5px;
}

.km-key-labels,
.km-slot,
.km-type,
.km-majorkey,
.km-kcv,
.km-modifier,
.km-usage,
.km-security,
.km-label {
  line-height: 1;
}

.km-slot {
  width: 7%;
}

.km-type {
  width: 10%;
}

.km-majorkey {
  width: 10%;
}

.km-kcv {
  width: 9%;
}

.km-modifier {
  width: 10%;
}

.km-usage {
  width: 18%;
}

.km-security {
  width: 18%;
}

.km-label {
  width: 18%;
}

.km-dropdown-column {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 100%;
  line-height: 1;
}

.dropdown-menu {
  padding: 0px !important;
  border: 1px solid #ddd;
  border-radius: 3px;
}

.dropdown-item {
  color: var(--text-color);
  font-size: 13px;
  padding: 6px 12px;
  border-bottom: 1px solid #eee;
}

.km-key {
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 10%;
  border-bottom: 1px solid #eee;
}

.km-key:last-of-type {
  border-bottom: 0px;
}

#km-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
}

#km-footer-label {
}

.page-nav {
  display: flex;
}

.previous {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.page-display {
  background-color: #337ab7;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 1rem;
}

.next {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>
