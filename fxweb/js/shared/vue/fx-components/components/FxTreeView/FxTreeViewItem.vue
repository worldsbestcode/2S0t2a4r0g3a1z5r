<style scoped>
.icon {
  text-align: center;
  width: 2rem;
}

.fa {
  font-size: 12px;
}
</style>
<template>
  <div :class="{'panel-open': bodyShown }" class="panel list-view-group">
    <div class="panel-heading list-view-header" role="button" @click="toggleShowInfo">
      <div
        class="icon"
        v-if="expandable"
        @click.stop="expand"
      >
        <span class="fa fa-plus"></span>
      </div>
      <div
        class="icon"
        v-else-if="collapsable"
        @click.stop="collapse"
      >
        <span class="fa fa-minus"></span>
      </div>
      <div class="icon" v-else></div>
      <span
        v-if="item.icon"
        class="fa"
        :class="item.icon"
      >
      </span>
      <component
        class="panel-title"
        :is="getHeader()"
        :data="data"
        :item="item"
        :v-bind="additionalProps"
      >
      </component>
    </div>
    <collapse class="panel-collapse" v-model="bodyShown" v-if="body">
        <div class = "panel-body">
          <component
            :is="getBody()"
            :data="data"
            :item="item"
            v-bind="additionalProps"
            >
          </component>
        </div>
    </collapse>
  </div>
</template>

<script>
export default {
  name: 'fx-treeview-item',
  components: {
  },
  props: {
    expanded: {
      type: Boolean,
      required: false,
      default: false
    },
    expandable: {
      type: Boolean,
      required: false,
      default: true
    },
    selected: {
      type: Boolean,
      required: false,
      default: false
    },
    data: {
      type: Object
    },
    header: {
    },
    body: {
    },
    additionalProps: {
    }
  },
  computed: {
    collapsable: function () {
      return this.expanded;
    },
    item: function () {
      return this;
    },
  },
  methods: {
    selectItem: function () {
      this.emitItemSelected(this);
    },
    toggleShowInfo: function () {
      this.item.bodyShown = !this.item.bodyShown;
    },
    expand: function () {
      this.$emit('expand');
    },
    collapse: function () {
      this.$emit('collapse');
    },
    getHeader: function () {
      if (typeof this.header === 'function') {
        return this.header(this.data);
      } else {
        return this.header;
      }
    },
    getBody: function () {
      if (typeof this.body === 'function') {
        return this.body(this.data);
      } else {
        return this.body;
      }
    }
  },
  data () {
    return {
      bodyShown: false
    };
  }
};
</script>
