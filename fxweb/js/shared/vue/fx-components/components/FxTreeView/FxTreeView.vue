<template>
  <div class="panel-group">
    <fx-treeview-heading-bar
      v-if="headingBar"
      :heading-bar="headingBar"
      :heading-bar-data="headingBarData">
    </fx-treeview-heading-bar>
    <template v-for="(item, index) in dataArray">
      <fx-treeview-node
        :key="itemIndex(item, index)"
        :data="item"
        :item-index="itemIndex"
        :has-children="hasChildren"
        :fetch-data="fetchData"
        :filter-children="filterChildren"
        :header="header"
        :body="body"
        :additional-props="additionalProps"
      >
      </fx-treeview-node>
    </template>
  </div>
</template>

<script>
import FxTreeViewNode from './FxTreeViewNode';
import FxTreeViewHeadingBar from './FxTreeViewHeadingBar';
export default {
  name: 'fx-treeview',
  components: {
    FxTreeViewNode: FxTreeViewNode,
    FxTreeViewHeadingBar: FxTreeViewHeadingBar
  },
  props: {
    data: {
      required: true
    },
    hasChildren: {
      type: Function,
      default: function (parentData) {
        return parentData.children.length > 0;
      }
    },
    fetchData: {
      type: Function,
      default: function (parentData) {
        return new Promise((resolve, reject) => {
          resolve();
        });
      }
    },
    filterChildren: {
      type: Function,
      default: function (data) {
        return data.children;
      }
    },
    itemIndex: {
      type: Function,
      default: function (item, index) {
        return item.id;
      }
    },
    header: {
    },
    body: {
    },
    headingBar: {
    },
    headingBarData: {
    }
  },
  computed: {
    dataArray: function () {
      /*
      * Required nested data array that recursively holds the treeview
      * structure. Each treeview item's own data object holds data specific to each
      * individual treeview item.
      */

      if (this.data instanceof Array) {
        return this.data;
      } else if (this.data.hasOwnProperty('treeviewItemsData')) { // eslint-disable-line no-prototype-builtins
        return this.data.treeviewItemsData;
      } else {
        return [this.data];
      }
    },
    additionalProps: function () {
      /*
      * Optional props  that are generic to every treeview item. Each property will be bound
      * to every treeview item  in the treeview as a seperate prop.
      */
      let props = {};
      Object.keys(this.data).forEach(key => {
        if (key !== 'treeviewItemsData') {
          props[key] = this.data[key];
        }
      });
      return props;
    }
  }
};
</script>
