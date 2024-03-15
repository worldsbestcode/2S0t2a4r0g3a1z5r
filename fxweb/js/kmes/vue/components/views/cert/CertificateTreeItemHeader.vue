<template>
  <fx-treeview-item-header
    :data="title"
  >
  </fx-treeview-item-header>
</template>

<script>
import X509CertSchema from 'kmes/store/schema/X509CertSchema';

export default {
  name: 'cert-treeview-item-header',
  components: {
  },
  props: {
    data: X509CertSchema,
  },
  computed: {
    title: function () {
      return {
        title: this.data.displayName
      };
    }
  },
};
</script>
