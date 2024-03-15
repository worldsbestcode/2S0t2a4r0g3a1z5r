<style scoped>
.tree-indent {
  margin-left: 1rem;
}
</style>
<template>
  <!-- Insert an item for the root item -->
  <div>
    <fx-treeview-item
      :expanded="rootItem.expanded"
      :expandable="rootExpandable"
      :selected="rootItem.selected"
      :additional-props="additionalProps"
      :data="data"
      @expand="expand"
      @collapse="collapse"
      @select="select"
      :header="header"
      :body="body"
    >
    </fx-treeview-item>

    <slot name="loading" v-if="busy">
      <span class="fa fa-spinner fa-spin"></span>Loading...
    </slot>

    <collapse id="subtree" class="tree-indent item-spacing collapsed" v-model="rootItem.expanded">
      <!-- Recursively add a tree for each child of the root item -->
      <template v-for="(childData, index) in childrenData">
        <fx-treeview-node
          :key="itemIndex(childData, index)"
          :data="childData"
          :item-index="itemIndex"
          :has-children="hasChildren"
          :filter-children="filterChildren"
          :fetch-data="fetchData"
          :header="header"
          :body="body"
          :additional-props="additionalProps"
        >
        </fx-treeview-node>
      </template>
    </collapse>

  </div>
</template>

<script>
import FxTreeViewItem from './FxTreeViewItem.vue';

export default {
  name: 'fx-treeview-node',
  components: {
    FxTreeViewItem: FxTreeViewItem
  },
  props: {
    data: {
      type: Object,
      required: true,
      default: function () {
        return {};
      }
    },
    fetchData: {
      type: Function,
      required: true
    },
    filterChildren: {
      type: Function,
      required: true,
    },
    hasChildren: {
      type: Function,
      required: true
    },
    itemIndex: {
      type: Function,
      required: false,
    },
    header: {
    },
    body: {
    },
    additionalProps: {
    }
  },
  computed: {
    childrenData: function () {
      var filtered = this.filterChildren(this.data, this.additionalProps);
      return filtered;
    },
    rootExpandable: function () {
      return !this.rootItem.expanded && this.hasChildren(this.data);
    }
  },
  methods: {
    expand: function () {
      var self = this;
      this.busy = true;

      let onSuccess = function () {
        self.rootItem.expanded = true;
        self.rootItem.expandable = self.rootExpandable;
        self.busy = false;
      };

      let onFailure = function () {
        self.busy = false;
      };

      this.fetchData(this.data).then(onSuccess, onFailure);
    },
    collapse: function () {
      this.rootItem.expanded = false;
    },
    select: function () {
      this.rootItem.selected = true;
    }
  },
  data () {
    return {
      rootItem: {
        expanded: false,
        expandable: false,
        collapsable: false,
        selected: false
      },
      busy: false
    };
  }
};
</script>
