<template>
  <div>
    <div
      class="row"
      v-for="(info, index) in infoList"
      :key="index"
    >
      <div class="col-sm-3">{{info.title}}:</div>
      <div class="col-sm-9">{{info.value}}</div>
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
import ManagedObjectSchema from 'kmes/store/schema/ManagedObjectSchema';
import TreeActionPanel from 'kmes/components/views/TreeActionPanel';

export default {
  components: {
    'tree-action-panel': TreeActionPanel,
  },
  props: {
    /**
     * Array of objects with properties:
     *   title: string
     *   value: string
     */
    infoList: {
      type: Array,
      required: true,
    },
    data: {
      type: ManagedObjectSchema,
      required: true,
    },
    getActions: {
      type: Function,
      required: true,
    },
    performAction: {
      type: Function,
      required: true,
    },
  },
  computed: {
    actions: function () {
      return this.getActions(this.data);
    }
  },
};
</script>
