<template>
  <div>
    <cert-tree
      :data="treeData"
      :fetch-data="fetchChildren"
      :has-children="hasChildren"
      :filter-children="filterChildren"
      :get-cert-info="getCertInfo"
    >
    </cert-tree>
    <action-modal
      :action="currentAction"
      :show.sync="showModal"
    >
    </action-modal>
  </div>
</template>

<script>
import ActionList from 'kmes/components/views/ActionList';
import ActionModal from 'kmes/components/views/ActionModal';
import CertAuthorityModule from 'kmes/store/features/CertAuthorityModule';
import CertificateImport from 'kmes/components/cert/CertificateImport';
import CertificateTree from './cert/CertificateTree';
import CertificateModule from 'kmes/store/features/CertificateModule';
import MajorKeyModule from 'kmes/store/features/MajorKeyModule';
import VIPModal from 'kmes/components/plugins/VIPModal';

// Actions
import ImportCertificateAction from './actions/ImportCertificateAction';
import ImportRootCertificateAction from './actions/ImportRootCertificateAction';

export default {
  components: {
    'action-modal': ActionModal,
    'cert-tree': CertificateTree,
    'fx-modal': VIPModal,
  },
  data () {
    return {
      currentAction: null,
      currentObject: null,
      showModal: false,
    };
  },
  created () {
    CertAuthorityModule.ready();
    MajorKeyModule.ready();
  },
  computed: {
    majorKeys () {
      return MajorKeyModule.getters.loaded;
    },
    treeData: function () {
      return {
        // Top-level tree data should be an array
        treeviewItemsData: CertAuthorityModule.getters['Objects/dataArray'],
        // We just include this so the cert-tree reacts to cert module changes
        certData: CertificateModule.getters['Objects/dataMap'],
        // Action info
        getActions: this.getActionNames,
        performAction: this.performAction,
      };
    },
    /**
     * Generates all of the actions that CA nodes can have.
     */
    caActions () {
      // If no major key is loaded, don't allow any actions
      if (this.majorKeys.length === 0) {
        return new ActionList();
      }

      let actions = [
        new ImportRootCertificateAction(
          this.importCertificate,
          CertificateImport,
          {
            fileData: '',
            loadedMajorKeys: this.majorKeys,
            majorKey: this.majorKeys[0],
          },
        ),
      ];

      return new ActionList(actions);
    },
    /**
     * Generates all of the actions that certificate nodes can have.
     */
    certActions () {
      // If no major key is loaded, don't allow any actions
      if (this.majorKeys.length === 0) {
        return new ActionList();
      }

      let majorKey = 'MFK';
      if (this.currentObject) {
        majorKey = this.currentObject.majorKey;
      }

      let actions = [
        new ImportCertificateAction(
          this.importCertificate,
          CertificateImport,
          {
            fileData: '',
            loadedMajorKeys: [majorKey],
            majorKey: majorKey,
          },
        ),
      ];

      return new ActionList(actions);
    },
  },
  methods: {
    /**
     * Retrieves all of the actions for a specific object type.
     *
     * @param objectData The object data
     *
     * @return the object actions
     */
    getObjectActionList: function (objectData) {
      if (this.isCertificate(objectData)) {
        return this.certActions;
      } else {
        return this.caActions;
      }
    },
    /**
     * Retrieves an action based on the object type and action name.
     *
     * @param objectData The object data, including object type
     * @param name The action name
     *
     * @return A single action matching the object+name, or null if none found
     */
    getAction: function (objectData, name) {
      let objectActionList = this.getObjectActionList(objectData);
      return objectActionList.getAction(name);
    },
    /**
     * Get all of the available actions based on the given data.
     *
     * @param objectData The object to get actions for
     *
     * @return An array of allowed actions for the given object
     */
    getActionNames: function (objectData) {
      let objectActions = this.getObjectActionList(objectData);
      return objectActions.getEnabledActionNames(objectData);
    },
    /**
     * Callback called when an action is activated.
     *
     * Sets the current action and current object to the ones sent in.
     *
     * @param objectData The object to be acted upon
     * @param name The name of the action that was activated
     */
    performAction: function (objectData, name) {
      this.currentObject = objectData;
      this.currentAction = this.getAction(objectData, name);
      this.showModal = true;
    },
    /**
     * Determines if the given object is a certificate.
     *
     * @param objectData The object to check
     *
     * @return true=is certificate, false=not certificate
     */
    isCertificate: function (objectData) {
      return objectData && objectData.objectType === 'X509CERT';
    },
    /**
     * Imports a certificate, updates affected objects on success.
     */
    importCertificate: function () {
      let { caID, certID } = this.getFilterInfo(this.currentObject);

      let promise = CertificateModule.dispatch({
        type: 'importCertificate',
        caID: caID,
        certID: certID,
        data: this.currentAction.props.fileData,
        majorKey: this.currentAction.props.majorKey,
      });

      let self = this;

      // Show success + update local objects
      let onSuccess = function (response) {
        self.$bus.$emit('showAlert', 'Certificate successfully imported.');

        let caIDs = [];
        let certIDs = [];
        if (response.newCertID) {
          certIDs.push(response.newCertID);
        }

        if (certID === '-1') {
          caIDs.push(caID);
        } else {
          certIDs.push(certID);
        }

        self.updateFromChange(caIDs, certIDs);
      };

      // Show failure message
      let onFailure = function (error) {
        let errorMessage = 'Certificate import failed.';
        if (error) {
          errorMessage += ' ';
          errorMessage += error;
        }
        self.$bus.$emit('showAlert', errorMessage, 'warning');
      };

      promise = promise.then(onSuccess, onFailure);

      // Hide the modal
      promise.then(function (response) {
        self.showModal = false;
      });
    },
    /**
     * Updates specific objects by querying them by ID.
     *
     * @param caIDs the CA IDs to update
     * @param certIDs the cert IDs to update
     */
    updateFromChange: function (caIDs, certIDs) {
      CertAuthorityModule.dispatch('Objects/getByIDs', caIDs);
      CertificateModule.dispatch('Objects/getByIDs', certIDs);
    },
    /**
     * Determines if the given object (CA or Certificate) has children.
     *
     * @param {Object} parentData - CA or Certificate object
     *
     * @returns true=has children, false=no children
     */
    hasChildren: function (parentData) {
      return parentData.hasChildren;
    },
    /**
     * Fetches a chunk of children for the given parent.
     *
     * @param {Object} parentData - CA or Certificate object
     *
     * @returns promise for the server query
     */
    fetchChildren: function (parentData) {
      const { caID, certID } = this.getFilterInfo(parentData);

      return CertificateModule.dispatch({
        type: 'getCertChildren',
        caID: caID,
        certID: certID,
      });
    },
    /**
     * Retrieves the children for the given parentData.
     *
     * @param {Object} parentData - CA or Certificate object
     * @param {Object} additionalProps - Ignored
     *
     * @returns the children of parentData
     */
    filterChildren: function (parentData, additionalProps) {
      const { caID, certID } = this.getFilterInfo(parentData);
      return CertificateModule.getters.getChildrenOf(caID, certID);
    },
    /**
     * Gets the CA and Cert ID for the given object.
     *
     * @param {Object} data - CA or Certificate object
     *
     * @returns ca and cert id in an object
     */
    getFilterInfo: function (data) {
      let caID = '-1';
      let certID = '-1';

      if (data.objectType === 'X509CERT') {
        caID = data.certAuthorityID;
        certID = data.objectID;
      } else if (data.objectType === 'CERTAUTHORITY') {
        caID = data.objectID;
      }

      return { caID, certID };
    },
  }
};
</script>
