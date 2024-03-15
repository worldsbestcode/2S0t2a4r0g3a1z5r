<template>
  <div>
    <datatable
      title="Certificate Authorities"
      editable="true"
      :table-data="certAuthData"
      :click-callback="selectCA"
      :click="true"
      @update-checked="updateChecked"
      :input-checked-items="checkedItems"
    >
    </datatable>
    <div class="field is-grouped">
      <button
        class="button control"
        :disabled="!canAddCA()"
        @click="addCAModal = true"
      >
        Add Certificate Authority
      </button>
      <button
        class="button control"
        :disabled="!canDeleteCA()"
        @click="deleteCAModal = true"
      >
        Delete Certificate Authority
      </button>
    </div>

    <modal
      title="Add Certificate Authority"
      :callback="addCertificateAuthority"
      :show="addCAModal"
      @on-close="addCAModal = false"
    >
      <div slot="modal-body">
        <cert-authority v-model="addCAData">
        </cert-authority>
      </div>
    </modal>
    <delete-modal
      title="Delete Certificate Authorities"
      :show="deleteCAModal"
      :data="deleteCAData"
      :callback="deleteCA"
      @on-close="deleteCAModal = false"
    >
    </delete-modal>
  </div>
</template>

<script>
import DataTable from 'src/components/plugins/DataTable';
import DeleteModal from 'src/components/plugins/DeleteModal';
import VIPModal from 'src/components/plugins/VIPModal';

import CertAuthority from 'kmes/components/cert/CertAuthority';
import CertAuthorityModule from 'kmes/store/features/CertAuthorityModule';
import CertAuthoritySchema from 'kmes/store/schema/CertAuthoritySchema';
import CertType from 'kmes/store/schema/CertType';

export default {
  props: {
    classPerms: {
      type: Object,
      required: true,
    },
  },
  components: {
    'modal': VIPModal,
    'datatable': DataTable,
    'delete-modal': DeleteModal,
    'cert-authority': CertAuthority,
  },
  data () {
    return {
      headers: ['Name', 'PKI Type'],
      order: ['name', 'pkiTypeString'],
      types: CertType.getTypeStrings(),
      checkedItems: [],
      addCAData: new CertAuthoritySchema(),
      addCAModal: false,
      deleteCAModal: false,
      selectedCA: {}
    };
  },
  created () {
    CertAuthorityModule.ready();
  },
  computed: {
    selected: function () {
      return this.checkedItems.map(function (item) {
        var ca = new CertAuthoritySchema();
        ca.fromJSON(JSON.parse(item));
        return ca;
      });
    },
    deleteCAData: function () {
      return {
        order: this.order,
        headers: this.headers,
        data: this.selected
      };
    },
    certAuthData: function () {
      return {
        order: this.order,
        headers: this.headers,
        types: this.types,
        data: CertAuthorityModule.getters['Objects/dataArray'],
      };
    },
  },
  methods: {
    canAddCA: function () {
      return this.classPerms.canAddCertAuthorities();
    },
    canDeleteCA: function () {
      var hasPerms = this.classPerms.canDeleteCertAuthorities();
      var itemsChecked = this.checkedItems.length > 0;
      return hasPerms && itemsChecked;
    },
    reloadCAData: function () {
      this.resetAddCAData();
      CertAuthorityModule.dispatch({
        type: 'Objects/loadPage',
        chunkIndex: 0
      });
    },
    resetAddCAData: function () {
      this.addCAData = new CertAuthoritySchema();
    },
    selectCA: function (row) {
      this.selectedCA = row;
    },
    deleteCA: function () {
      /*
        Deletes a certificate authority
      */
      var self = this;
      var ids = self.selected.map(x => x.objectID);

      var promise = CertAuthorityModule.dispatch('Objects/deleteByID', ids);
      promise.then(function (response) {
        self.checkedItems = [];
      });
    },
    addCertificateAuthority: function () {
      /*
        Adds a certificate authority
      */
      const self = this;

      var promise = CertAuthorityModule.dispatch('Objects/add', this.addCAData);

      var onSuccess = function (response) {
        self.$bus.$emit('showAlert', 'Successfully added CA.');
        self.addCAModal = false;
        self.reloadCAData();
      };

      var onFailure = function (error) {
        var errorMessage = 'Failed to add CA.';
        if (error) {
          errorMessage += ' ';
          errorMessage += error;
        }
        self.$bus.$emit('showAlert', errorMessage, 'warning');
      };

      promise.then(onSuccess, onFailure);
    },
    updateChecked: function (checkedItems) {
      this.checkedItems = checkedItems;
    },
  }
};
</script>
