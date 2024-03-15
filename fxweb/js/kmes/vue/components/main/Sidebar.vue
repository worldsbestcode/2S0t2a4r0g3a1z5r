<style lang="scss" scoped>
@import '~src/css/variables.scss';

#sidebar-container {
  height: 100%;
}

#sidebar {
  width: 100%;
  min-width: 60px;
  height: 100%;
  top:0;
  bottom: 0;
  position: relative;
  display: inline-block;
  z-index: 4999;
  text-align: center;
  color: $base;
  background-color: #212121;
  -webkit-box-shadow: 2px 0px 5px 0px rgba(0,0,0,0.7);
     -moz-box-shadow: 2px 0px 5px 0px rgba(0,0,0,0.7);
          box-shadow: 2px 0px 5px 0px rgba(0,0,0,0.7);
}

#user-info  {
  border-top: 2px solid #2e2e2e;
  border-bottom: 1px solid #2e2e2e;
  text-align: left;
  .account-name {
    color: $secondary;
  }

  .user-name {
    color: $base;
  }

  .is-custom-size {
    font-size: 1rem;
  }
}

#sidebar-menu .select-options span:hover, #sidebar-menu .active span {
  color: $secondary;
}

#sidebar-menu {
  overflow-y: auto;
  overflow-y: overlay;
  color: #ABA6A6;
}

#sidebar-content {
  display: flex;
  flex-direction: column;
  position: relative;
  height: calc(100% - 5em);
}

#sidebar-footer {
  height: 5em;
  bottom: 0;
  border-top: 1px solid #2e2e2e;
  div {
    width: 50%;
    height: 100%;
    display: inline-flex;
    justify-content: center;
    align-items: center;
  }
  .left {
    background-color: #212121;
  }

  .right {
    background-color: #1D1D1D;
  }
}

.icon {
  font-size: 2rem;
}

</style>
<template>
  <div>
    <div id="sidebar-container" class="">
      <div id="sidebar" class="">
        <div id="sidebar-content">
          <div id="sidebar-header" v-if="!sidebarToggled">
            <div class="column is-12 logo">
              <img src="/images/kmes-series-3.png">
            </div>

            <div id="user-info" class="fields column is-12">
              <span class="user-name subtitle is-custom-size"> {{ userName }}</span>
            </div>
          </div>

          <div id="sidebar-menu" :class="{'toggled column is-12': sidebarToggled}">
            <transition name="fade" mode="out-in">
              <div id="nav-container" class="fields">
                <navigation
                  :available-views="availableViews"
                  :selected-view="selectedView"
                  :icons-only="sidebarToggled"
                  @viewChanged="viewChanged"
                >
                </navigation>
              </div>
            </transition>
          </div>
        </div>

        <div
          id="sidebar-footer"
          :class="{ 'rotate-sidebar': sidebarToggled}"
          class="column is-12 is-paddingless"
        >
          <div v-if="!sidebarToggled" class="column is-6 is-pulled-left left">
            <a class="click" href="/logout">
              <img class="icon is-medium click" src="/images/icons/power.svg">
            </a>
          </div>

          <div v-if="sidebarToggled">
            <img
              class="icon is-medium click"
              src="/images/icons/chevron-right.svg"
              @click="toggleSidebar"
            >
          </div>

          <div class="column is-6 is-pulled-right right" v-else>
            <img
              class="icon is-medium click"
              src="/images/icons/chevron-left.svg"
              @click="toggleSidebar"
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import Navigation from './Navigation';

export default {
  props: {
    sidebarToggled: {
      type: Boolean,
      required: true
    },
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
    userName: {
      required: true,
      type: String,
      default: ''
    }
  },
  components: {
    'navigation': Navigation
  },
  data: function () {
    return {};
  },
  methods: {
    toggleSidebar: function () {
      this.$bus.$emit('toggleSidebar');
    },
    toggleTokenGroups: function () {
      this.$bus.$emit('toggleTokenGroups');
    },
    viewChanged: function (viewName) {
      this.$emit('viewChanged', viewName);
    },
  }
};
</script>
