<style>
.panel-body {
  border: 1px solid #ddd;
}
</style>
<template>
  <div>
    <fx-treeview
      :header="getHeader"
      :body="getBody"
      :data="data"
      :item-index="getItemIndex"
      :fetch-data="fetchData"
      :has-children="hasChildren"
      :filter-children="filterChildren"
    >
    </fx-treeview>
  </div>
</template>

<script>
import CertificateTreeItemHeader from 'kmes/components/views/cert/CertificateTreeItemHeader';
import CertificateTreeItemBody from 'kmes/components/views/cert/CertificateTreeItemBody';
import CertificateAuthorityTreeItemHeader from 'kmes/components/views/cert/CertificateAuthorityTreeItemHeader';
import CertificateAuthorityTreeItemBody from 'kmes/components/views/cert/CertificateAuthorityTreeItemBody';

export default {
  props: {
    data: {
    },
    hasChildren: {
      type: Function,
      required: true,
    },
    filterChildren: {
      type: Function,
      required: true,
    },
    fetchData: {
      type: Function,
      required: true,
    },
  },
  methods: {
    getHeader: function (data) {
      return {
        'CERTAUTHORITY': CertificateAuthorityTreeItemHeader,
        'X509CERT': CertificateTreeItemHeader
      }[data.objectType];
    },
    getBody: function (data) {
      return {
        'CERTAUTHORITY': CertificateAuthorityTreeItemBody,
        'X509CERT': CertificateTreeItemBody
      }[data.objectType];
    },
    getItemIndex: function (item, index) {
      return item.objectID;
    }
  },
  data () {
    return {
    };
  }
};
</script>
