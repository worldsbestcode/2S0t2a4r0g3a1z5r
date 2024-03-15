<template>
  <fx-treeview-item-header
    :data="text"
  >
  </fx-treeview-item-header>
</template>
<script>
import CertAuthoritySchema from 'kmes/store/schema/CertAuthoritySchema';

export default {
  name: 'cert-authority-tree-item-header',
  components: {
  },
  props: {
    data: CertAuthoritySchema,
  },
  computed: {
    text: function () {
      return {
        title: this.data.name
      };
    }
  },
};
</script>
