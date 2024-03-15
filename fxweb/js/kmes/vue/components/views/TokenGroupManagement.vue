<style lang="scss" scoped>
@import '~src/css/variables.scss';

.border {
  border: 2px solid #ddd;
}

.objectTable {
  overflow-y: auto;
  overflow-y: overlay;
  width: 100%;
  margin-bottom: 15px;
}

.rTable {
  display: table;
  width: 100%;
}
.rTableRow {
  display: table-row;
  vertical-align: inherit;
  border-color: inherit;
}
.rTableCell, .rTableHead {
  display: table-cell;
  padding: 8px;
}

.rTableHeading {
  background-color: #eee;
  display: table-header-group;
  font-weight: bold;
  border-bottom: 2px solid #ddd;
}

.rTableBody {
  display: table-row-group;
}

.rTableBody:nth-child(even) {
  background-color: #e4e4e4;
  .inner-row {
    background-color: white;
  }
}

.rTableBody:nth-child(odd) {
  background-color: white ;
  .inner-row {
    background-color: $base;
  }
}

.tokenGroup-buttons {
  overflow: hidden;
  display: flex;
  justify-content: flex-end;
  float: right;
}

.header .column {
  padding: 0px;
}

</style>
<template>
  <div class="tokenGroupView">
    <div class="column is-12">
      <div class="field is-grouped">
        <button class="button control" v-show="canAddTokenGroups()" @click="showTokenGroupAdd">
          Add Token Group
        </button>
      </div>
      <div class="objectTable">
      <div v-if="tokenGroups.length > 0" class="rTable table-striped">
        <div class="rTableHeading">
          <div class="rTableRow">
            <div class="rTableHead">
              Name
            </div>
            <div class="rTableHead"></div>
          </div>
        </div>
        <div
          class="rTableBody"
          v-for="tokenGroup in tokenGroups"
          :title="tokenGroup.name"
          :key="tokenGroup.name"
        >
          <div class="rTableRow">
            <div class="header rTableCell">
              <span class="panel-name column is-4">
                <strong>
                  {{ tokenGroup.name }}
                </strong>
              </span>
            </div>
            <div class="rTableCell tokenGroup-buttons column is-8">
              <button
                class="button"
                v-show="canDeleteTokenGroups()"
                @click.stop="openDeleteGroupModal(tokenGroup)"
              >
                Delete Token Group
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="has-text-centered">
        <div class="title is-3">No Token Groups found.</div>
      </div>
      </div>
    </div>

    <modal
      title="Add Token Group"
      :callback="addTokenGroup"
      :show="addGroupModal"
      @on-close="addGroupModal = false"
    >
      <div slot="modal-body">
        <div class="form-group">
          <token-profile :keys="keys" @changed='editTokenGroupChanged'>
          </token-profile>
        </div>
      </div>
    </modal>

    <delete-modal
      title="Delete Token Group"
      :show="deleteGroupModal"
      :data="deleteGroupData()"
      :callback="deleteGroup"
      @on-close="deleteGroupModal = false"
    >
    </delete-modal>

  </div>
</template>

<script>
import VIPModal from 'kmes/components/plugins/VIPModal';
import DeleteModal from 'kmes/components/plugins/DeleteModal';
import SymmetricKeyModule from 'kmes/store/features/SymmetricKeyModule';
import TokenGenerationProfile from 'kmes/components/token/TokenGenerationProfile';
import TokenGroupSchema from 'kmes/store/schema/TokenGroupSchema';
import TokenGroupModule from 'kmes/store/features/TokenGroupModule';

export default {
  props: {
    classPerms: {
      type: Object,
      required: true,
    }
  },
  created () {
    SymmetricKeyModule.ready();
    TokenGroupModule.ready();
  },
  components: {
    'modal': VIPModal,
    'token-profile': TokenGenerationProfile,
    'delete-modal': DeleteModal,
  },
  data () {
    return {
      editTokenGroup: new TokenGroupSchema(),
      addGroupModal: false,
      deleteGroupModal: false,
    };
  },
  computed: {
    tokenGroups () {
      return TokenGroupModule.getters['Objects/dataArray'];
    },
    keys () {
      return SymmetricKeyModule.getters['Objects/dataArray'];
    }
  },
  methods: {
    /**
     * Called when a user clicks the 'Add Token Group' button.
     *
     * Loads aes encryption keys from the server, then shows the token add modal.
     */
    showTokenGroupAdd () {
      let self = this;
      SymmetricKeyModule.dispatch('loadAESEncryptionKeys').then(() => {
        self.addGroupModal = true;
      });
    },
    /**
     * Deletes the group from the server.
     */
    deleteGroup: function () {
      let self = this;

      let onSuccess = function () {
        self.reloadTokenGroups();
      };

      let onFailure = function (error) {
        self.$bus.$emit('showAlert',
          'Error deleting token group. ' + error,
          'warning');
      };

      let ids = [this.editTokenGroup.objectID];
      let promise = TokenGroupModule.dispatch('Objects/deleteByID', ids);

      promise.then(onSuccess, onFailure);
    },
    openDeleteGroupModal: function (tokenGroup) {
      this.editTokenGroup = tokenGroup;
      this.deleteGroupModal = true;
    },
    deleteGroupData: function () {
      return {
        data: [this.editTokenGroup],
        order: ['name'],
        header: ['Name'],
      };
    },
    /**
     * Adds the current token group to the server.
     */
    addTokenGroup: function () {
      let self = this;

      let onSuccess = function () {
        self.reloadTokenGroups();
      };

      let onFailure = function (error) {
        self.$bus.$emit('showAlert',
          'Failed adding key. ' + error,
          'warning');
      };

      let promise = TokenGroupModule.dispatch('Objects/add', this.editTokenGroup);
      promise.then(onSuccess, onFailure);
    },
    /**
     * Called when the token group currently getting edited is chagned.
     *
     * @param {Object} tokenGroup - The new token group
     */
    editTokenGroupChanged: function (tokenGroup) {
      this.editTokenGroup = tokenGroup;
    },
    /**
     * Determines if permissions are sufficient to add a token group.
     *
     * @returns true=can add, false=cannot add
     */
    canAddTokenGroups: function () {
      return this.classPerms.canAddTokenGroups();
    },
    /**
     * Determines if permissions are sufficient to delete a token group.
     *
     * @returns true=can delete, false=cannot delete
     */
    canDeleteTokenGroups: function () {
      return this.classPerms.canDeleteTokenGroups();
    },
    /**
     * Gets updated token group info from the server.
     */
    reloadTokenGroups: function () {
      let self = this;

      this.addGroupModal = false;
      this.deleteGroupModal = false;

      let onFailure = function (error) {
        self.$bus.$emit('showAlert',
          'Error reloading tokens. ' + error,
          'warning');
      };

      let promise = TokenGroupModule.dispatch('Objects/loadPage', 0);
      promise.catch(onFailure);
    }
  },
};
</script>
