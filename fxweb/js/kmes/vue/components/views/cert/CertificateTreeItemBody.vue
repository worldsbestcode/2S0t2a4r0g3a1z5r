<style>
.item-body {
  padding: 15px
}
</style>

<template>
  <div class="item-body">
    <div v-if="item.bodyShown">
      <cert-info :cert="data.certificate" >
      </cert-info>
    </div>
    <div v-else>
      loading
    </div>
    <tree-action-panel
      :data="data"
      :actions="this.actions"
      :perform-action="this.performAction"
    >
    </tree-action-panel>
  </div>
</template>

<script>
import CertificateInfo from 'kmes/components/cert/CertificateInfo';
import TreeActionPanel from 'kmes/components/views/TreeActionPanel';
import X509CertSchema from 'kmes/store/schema/X509CertSchema';

export default {
  name: 'cert-tree-item-body',
  components: {
    'cert-info': CertificateInfo,
    'tree-action-panel': TreeActionPanel,
  },
  props: {
    data: X509CertSchema,
    item: Object,
    getActions: {
      type: Function,
      required: true,
    },
    performAction: {
      type: Function,
      required: true,
    }
  },
  data () {
    return {};
  },
  computed: {
    actions: function () {
      return this.getActions(this.data);
    }
  },
};
</script>
