<style lang="scss" scoped>
@import '~src/css/variables.scss';

span {
  display: block;
}

.icon {
  cursor: pointer;
  height: 50%;
}

#nav-menu {
  overflow-y: overlay;
  text-align: left;
  .menu-list {
    li {
      a.is-active {
        color: white;
      }
      ul {
        margin-bottom: 0px;
        border-left: 2px solid $secondary;
      }
    }
    a:not(:hover) {
      color: $text-color;
    }
    .submenu-title {
      &.is-active {
        background: none;
        color: white;
        &:hover {
          color: $secondary !important;
        }
      }
    }
  }
}
</style>
<template>
  <div>
    <div id="nav-menu" class="menu">
      <ul class="menu-list">
        <li v-for="info in viewInfo"
            :key="info.name">
          <div @click="setSelected(info.name)">
            <a
              v-if="!iconsOnly"
              class="submenu-title"
              :class="{'is-active': isSelected(info.name)}"
            >
              {{ info.printable }}
            </a>
            <img
              v-if="iconsOnly && info.icon !== ''"
              class="click icon-format icon is-medium"
              v-tooltip.right-middle="info.printable"
              :src="info.icon"
            >
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
<script>
import ViewUtils from 'kmes/components/views/ViewUtils';

export default {
  props: {
    availableViews: {
      required: true,
      type: Array,
      default: function () {
        return [];
      }
    },
    selectedView: {
      required: true,
      type: String,
      default: ''
    },
    iconsOnly: {
      required: true,
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
    };
  },
  computed: {
    viewInfo: function () {
      return ViewUtils.getViewInfos(this.availableViews);
    }
  },
  methods: {
    setSelected: function (name) {
      this.$emit('viewChanged', name);
    },
    isSelected: function (name) {
      return name === this.selectedView;
    }
  }
};
</script>
