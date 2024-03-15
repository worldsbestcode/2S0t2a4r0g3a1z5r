<template>
  <div class="row">
    <data-label class="col-sm-3">{{description}}</data-label>
    <data-label class="col-sm-1">{{extension.critical}}</data-label>
    <data-label class="col-sm-8">{{extension.value}}</data-label>
  </div>
</template>
<script>
import DataLabel from 'kmes/components/misc/DataLabel';
import X509ServiceDefs from 'shared/X509ServiceDefs';

export default {
  components: {
    'data-label': DataLabel,
  },
  props: {
    extension: {
      type: Object,
      required: true,
    },
  },
  computed: {
    description: function () {
      const extInfo = X509ServiceDefs.getAllExtensions().find(extInfo => {
        return extInfo.oid === this.extension.oid.split('.').join('_');
      });

      let description = null;
      if (extInfo) {
        description = extInfo.name;
      } else {
        description = this.extension.oid;
      }

      return description;
    }
  }
};
</script>
