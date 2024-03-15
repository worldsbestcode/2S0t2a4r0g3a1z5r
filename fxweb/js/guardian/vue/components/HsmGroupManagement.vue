<style>
</style>

<template>
  <div>

    <!-- This div is to be removed when guardianObjectTab is ported to vue -->
    <div v-if="allowedTab === 2">
    <div v-if="activeTab === 2">
      <div v-if="loadedSecuritySettings">
        <hsm-security-settings
          :settings="settings.securitySettings"
          @save-settings="saveSecuritySettings">
        </hsm-security-settings>
      </div>
      <div v-else>
        <i class="fa fa-refresh fa-spin"></i>
      </div>
    </div>
    </div>

  </div>

</template>

<script>
import deviceManagement from 'guardian/deviceManagement';
import HsmSecuritySettings from 'components/HsmSecuritySettings';

const SECURITY_INDEX = 2;
const NUM_INDEXES = 3;

// Index is handled by this component in vue
function handlesIndex (index) {
  return index === SECURITY_INDEX;
}

// Objects allowed to be selected for this view
function isUpdateObject (obj) {
  return obj !== null &&
         obj.objectType === 'CARDGROUP' &&
         obj.objectID !== '-1';
}

// Object has changed since updating
function isDiffObject (newObj, oldObj) {
  return newObj.objectType !== oldObj.objectType ||
         newObj.objectID !== oldObj.objectID;
}

function canUpdate (newObj, oldObj) {
  return isUpdateObject(newObj) &&
         isDiffObject(newObj, oldObj) &&
         newObj.authorized;
}

export default {
  components: {
    'hsm-security-settings': HsmSecuritySettings,
  },
  props: {
    // Active tab by name currently controlled by angular
    activeTab: {
      required: true,
    },
    // Since each tab must exist as an independent version of this widget,
    // only show one tab until ported fully to Vue
    allowedTab: {
      required: true,
      type: Number,
    },
    selectionState: {
      required: true,
    },
  },
  data: function () {
    return {
      loadedSecuritySettings: false,
    };
  },
  created: function () {
    // Last object that we updated settings from
    // Each index should be enumerated separately
    this.lastUpdated = [];
    for (var i = 0; i < NUM_INDEXES; i++) {
      this.lastUpdated.push({
        objectID: '-1',
        objectType: null,
      });
    }

    // parent data for each tab
    this.settings = {
      securitySettings: {},
    };
  },
  methods: {
    saveSecuritySettings: function (settings) {
      deviceManagement.saveSecuritySettings(this.selectionState, settings);
    },

    queryPage: function () {
      var self = this;
      var index = self.activeTab;
      var oldObj = self.lastUpdated[index];
      var newObj = self.selectionState;
      if (canUpdate(newObj, oldObj) && handlesIndex(index)) {
        if (index === SECURITY_INDEX) {
          self.loadedSecuritySettings = false;
          deviceManagement.loadSecuritySettings(newObj, function (settings) {
            self.settings.securitySettings = Object.assign({}, settings);

            self.loadedSecuritySettings = true;
            oldObj.objectID = newObj.objectID;
            oldObj.objectType = newObj.objectType;
          });
        }
      }
    }
  },
  watch: {
    selectionState: {
      handler (newObj) {
        this.queryPage();
      },
      deep: true,
    },
    activeTab: function (newIndex) {
      this.queryPage();
    },
  },
};
</script>
