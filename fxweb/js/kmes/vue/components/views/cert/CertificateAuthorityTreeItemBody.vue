<template>
  <default-mo-item-body
    :info-list="infoList"
    :data="data"
    :get-actions="getActions"
    :perform-action="performAction"
  >
  </default-mo-item-body>
</template>
<script>
import CertAuthoritySchema from 'kmes/store/schema/CertAuthoritySchema';
import DefaultMOTreeItemBody from 'kmes/components/views/DefaultMOTreeItemBody';

export default {
  components: {
    'default-mo-item-body': DefaultMOTreeItemBody,
  },
  props: {
    data: {
      type: CertAuthoritySchema,
      required: true,
    },
    getActions: {
      type: Function,
      required: true,
    },
    performAction: {
      type: Function,
      required: true,
    }
  },
  computed: {
    infoList () {
      return [
        {
          title: 'PKI Type',
          value: this.data.pkiTypeString
        }
      ];
    }
  },
};
</script>
